from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from notifications.scheduler import schedule_email
from datetime import datetime

# Create a Blueprint for the date-time routes
confirm_bp = Blueprint('confirm', __name__, template_folder="../templates")

mysql = MySQL()

@confirm_bp.route('/confirm', methods=["GET", "POST"])
def confirm_meeting():
    address = session.get('address')
    date = session.get('date')
    time = session.get('time')
    email = session.get('email')

    if request.method == 'POST':
        if 'confirm' in request.form:
            # Combine date and time into a datetime object
            meeting_datetime_str = f"{date} {time}"
            meeting_datetime = datetime.strptime(meeting_datetime_str, "%Y-%m-%d %H:%M")

            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO meetings (address, date, time) VALUES (%s, %s, %s)",
                (address, date, time)
            )
            mysql.connection.commit()
            cursor.close()

            # Schedule reminder emails
            if email:
                schedule_email(meeting_datetime, email, address, immediate=True)

            flash(f'Meeting Scheduled:{time} {date} at {address}', 'success')
            return redirect(url_for('home'))
        
        elif 'edit' in request.form:
            return redirect(url_for('address.address_page')) # redirect to address

    # Render the form template for GET requests
    return render_template('confirm.html', address=address, date=date, time=time)
