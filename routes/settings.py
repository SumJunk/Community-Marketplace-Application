from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from datetime import datetime

# Create a Blueprint for the date-time routes
settings_bp = Blueprint('settings', __name__, template_folder="../templates")

mysql = MySQL()

def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            flash('You need to login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@settings_bp.route('/settings', methods=["GET"])
@login_required
def settings_page():
    user_id = session.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username, email FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, address, date, TIME_FORMAT(time, '%H:%i') as time FROM prior_meetings")
    cursor.execute("SELECT listing_id, purchase_date, status FROM purchases")
    meetings = cursor.fetchall()

    prior_meetings = []
    purchases = []

    for m in meetings:
        meeting_id, address, date_str, time_str = m
        meeting_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        formatted_time = meeting_datetime.strftime("%I:%M %p")

        prior_meetings.append({
            'id': meeting_id,
            'address': address,
            'date': date_str,
            'time': formatted_time
        })

    for p in purchases:
        listing_id, purchase_date, status = p

        purchases.append({
            'listing_id': listing_id,
            'purchase_date': purchase_date,
            'status': status
        })

    cursor.close()

    if result:
        username, email = result
        return render_template('settings.html', username=username, email=email, prior_meetings=prior_meetings, purchases=purchases)
    else:
        flash("User not found", "danger")
        return redirect(url_for('login'))


@settings_bp.route('/edit_account', methods=["PUT"])
def edit_account():
    try:
        user_id = session.get('user_id')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET username = %s, password = %s, email = %s WHERE id = %s", 
                       (username, password, email, user_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': f'Updated account details'})
    except Exception as e:
        print("Error during update:", e)
        return jsonify({'error': str(e)})


@settings_bp.route('/delete_account', methods=['DELETE'])
def delete_account():
    try:
        user_id = session.get('user_id')

        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': f'Deleted account'})
    except Exception as e:
        print("Error during delete:", e)
        return jsonify({'error': str(e)})
