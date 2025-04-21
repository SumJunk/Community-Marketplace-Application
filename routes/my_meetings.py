from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL

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

@meeting_bp.route("/my-meetings", methods=["GET"])
@login_required
def my_meetings_page():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, address, date, time FROM meetings") 
    meetings = cursor.fetchall()
    cursor.close()

    # Convert to list of dicts
    meeting_list = [{'id': m[0], 'address': m[1], 'date': m[2], 'time': m[3]} for m in meetings]
    return render_template("my_meetings.html", meetings=meeting_list)
    
# Edit meeting
@meeting_bp.route('/<int:meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    try:
        address = request.form.get('query')
        date = request.form.get('date')
        time = request.form.get('time')

        print(f"Updating meeting {meeting_id} with: {address}, {date}, {time}")

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE meetings SET address = %s, date = %s, time = %s WHERE id = %s", 
                       (address, date, time, meeting_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': f'Meeting #{meeting_id} update waiting for approval'})
    except Exception as e:
        print("Error during update:", e)
        return jsonify({'error': str(e)})

# Cancel meeting
# TODO: Add validation for both parties
@meeting_bp.route('/<int:meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    try:
        print(f"Deleting meeting {meeting_id}")
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM meetings WHERE id = %s", (meeting_id,))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': f'Meeting #{meeting_id} removed successfully!'})
    except Exception as e:
        print("Error during delete:", e)
        return jsonify({'error': str(e)})
