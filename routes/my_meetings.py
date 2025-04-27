from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from datetime import datetime
from notifications.email_scheduler import send_email
from flask import current_app

# Create a Blueprint for the date-time routes
meeting_bp = Blueprint('my_meetings', __name__, template_folder="../templates")

mysql = MySQL()

def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            flash('You need to login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

def get_user(meeting_id):
    user_id = session.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT buyer_id, seller_id, listing_id FROM meetings WHERE id = %s", (meeting_id,))
    result = cursor.fetchone()

    if user_id == result[0]:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT email FROM users WHERE id = %s", (result[1],))
        seller = cursor.fetchone()
        return seller[0]
    
    elif user_id == result[1]:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT email FROM users WHERE id = %s", (result[0],))
        buyer = cursor.fetchone()
        return buyer[0]

@meeting_bp.route("/my-meetings", methods=["GET"])
@login_required
def my_meetings_page():
    user_id = session.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id, address, date, TIME_FORMAT(time, '%%H:%%i') as time, status, buyer_id, seller_id
        FROM meetings
        WHERE buyer_id = %s OR seller_id = %s
    """, (user_id, user_id))
    meetings = cursor.fetchall()

    now = datetime.now()
    upcoming_meetings = []

    for m in meetings:
        meeting_id, address, date_str, time_str, status, buyer_id, seller_id = m
        meeting_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        formatted_time = meeting_datetime.strftime("%I:%M %p")

        if meeting_datetime < now:
            cursor.execute(
                "INSERT INTO prior_meetings (id, address, date, time, status) VALUES (%s, %s, %s, %s, %s)",
                (meeting_id, address, date_str, time_str, status)
            )
            cursor.execute("DELETE FROM meetings WHERE id = %s", (meeting_id,))
        else:
            upcoming_meetings.append({
                'id': meeting_id,
                'address': address,
                'date': date_str,
                'time': formatted_time,
                'status': status,
                'is_seller': (seller_id == user_id)  # mark if logged-in user is seller
            })

    mysql.connection.commit()
    cursor.close()

    return render_template("my_meetings.html", meetings=upcoming_meetings)
    
# Edit meeting
@meeting_bp.route('/<int:meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    email = get_user(meeting_id)
    try:
        address = request.form.get('query')
        date = request.form.get('date')
        time = request.form.get('time')

        print(f"Updating meeting {meeting_id} with: {address}, {date}, {time}")

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE meetings SET address = %s, date = %s, time = %s, status= %s WHERE id = %s", 
                       (address, date, time, 'pending update', meeting_id))
        mysql.connection.commit()
        cursor.close()

        if email:
                send_email(current_app._get_current_object(), email, 'Meeting Update', 'Please approve meeting update or cancel meeting')

        return jsonify({'message': f'Meeting #{meeting_id} update waiting for approval'})
    except Exception as e:
        print("Error during update:", e)
        return jsonify({'error': str(e)})

# Cancel meeting
@meeting_bp.route('/<int:meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    email = get_user(meeting_id)

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT listing_id FROM meetings WHERE id = %s", (meeting_id,))
    result = cursor.fetchone()
    
    listing_id = result[0]
    try:
        print(f"Deleting meeting {meeting_id}")
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM meetings WHERE id = %s", (meeting_id,))
        cursor.execute("DELETE FROM purchases WHERE listing_id = %s", (listing_id,))
        mysql.connection.commit()
        cursor.close()

        if email:
                send_email(current_app._get_current_object(), email, 'Meeting Canceled', f'Your meeting for listing #{listing_id} has been canceled')

        return jsonify({'message': f'Meeting #{meeting_id} removed successfully!'})
    except Exception as e:
        print("Error during delete:", e)
        return jsonify({'error': str(e)})

@meeting_bp.route('/<int:meeting_id>', methods=["POST"])
def confirm_meeting(meeting_id):
    user_id = session.get('user_id')
    email = get_user(meeting_id)

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT seller_id, listing_id FROM meetings WHERE id = %s", (meeting_id,))
    result = cursor.fetchone()

    if not result:
        flash("Meeting not found.", "danger")
        return redirect(url_for('my_meetings.my_meetings_page'))

    seller_id = result[0]
    listing_id = result[1]

    if seller_id != user_id:
        flash("You are not authorized to confirm/cancel this meeting.", "danger")
        return redirect(url_for('my_meetings.my_meetings_page'))

    if 'confirm' in request.form:
        cursor.execute("UPDATE meetings SET status = 'confirmed' WHERE id = %s", (meeting_id,))
        flash("Meeting confirmed!", "success")
        if email:
                send_email(current_app._get_current_object(), email, 'Meeting Cconfirmed', f'Your meeting for listing #{listing_id} has been confirmed')
    elif 'cancel' in request.form:
        cursor.execute("DELETE FROM meetings WHERE id = %s", (meeting_id,))
        cursor.execute("DELETE FROM purchases WHERE listing_id = %s", (listing_id,))
        flash("Meeting cancelled.", "info")
        if email:
                send_email(current_app._get_current_object(), email, 'Meeting Canceled', f'Your meeting for listing #{listing_id} has been canceled')
    else:
        flash("Invalid action.", "warning")

    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('my_meetings.my_meetings_page'))

@meeting_bp.route('/<int:meeting_id>', methods=["POST"])
def confirm_update(meeting_id):
    email = get_user(meeting_id)

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT seller_id, listing_id FROM meetings WHERE id = %s", (meeting_id,))
    result = cursor.fetchone()

    if not result:
        flash("Meeting not found.", "danger")
        return redirect(url_for('my_meetings.my_meetings_page'))

    listing_id = result[1]

    if 'confirm_update' in request.form:
        cursor.execute("UPDATE meetings SET status = 'confirmed' WHERE id = %s", (meeting_id,))
        flash("Meeting update confirmed!", "success")
        if email:
                send_email(current_app._get_current_object(), email, 'Meeting Update Confirmed', f'Your meeting for listing #{listing_id} has been updated')
    elif 'cancel_update' in request.form:
        cursor.execute("DELETE FROM meetings WHERE id = %s", (meeting_id,))
        cursor.execute("DELETE FROM purchases WHERE listing_id = %s", (listing_id,))
        flash("Meeting cancelled.", "info")
        if email:
                send_email(current_app._get_current_object(), email, 'Meeting Canceled', f'Your meeting for listing #{listing_id} has been canceled')
    else:
        flash("Invalid action.", "warning")

    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('my_meetings.my_meetings_page'))

