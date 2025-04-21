from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from notifications.scheduler import schedule_email
from datetime import datetime

confirm_bp = Blueprint('confirm', __name__, template_folder="../templates")
mysql = MySQL()

@confirm_bp.route('/confirm', methods=["GET", "POST"])
def confirm_meeting():
    address = session.get('address')
    date = session.get('date')
    time = session.get('time')
    email = session.get('email')
    listing_id = session.get('listing_id')

    if request.method == 'POST':
        if 'confirm' in request.form:
            meeting_datetime_str = f"{date} {time}"
            meeting_datetime = datetime.strptime(meeting_datetime_str, "%Y-%m-%d %H:%M")

            cursor = mysql.connection.cursor()

            # Insert into meetings
            cursor.execute(
                "INSERT INTO meetings (address, date, time) VALUES (%s, %s, %s)",
                (address, date, time)
            )

            # Insert the confirmed purchase
            cursor.execute(
                "INSERT INTO purchases (buyer_id, listing_id, status) VALUES (%s, %s, %s)",
                (session.get('user_id'), listing_id, 'confirmed')
            )

            mysql.connection.commit()
            cursor.close()

            # Optional email notification
            if email:
                schedule_email(meeting_datetime, email, address)

            flash(f'Meeting Scheduled: {time} {date} at {address}', 'success')
            return redirect(url_for('home'))

        elif 'edit' in request.form:
            return redirect(url_for('address.address_page'))

    return render_template('confirm.html', address=address, date=date, time=time)
