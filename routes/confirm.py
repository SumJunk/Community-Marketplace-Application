from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from notifications.email_scheduler import schedule_email
from flask import current_app
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
    seller_id = session.get('seller_id')

    if request.method == 'POST':
        if 'confirm' in request.form:
            meeting_datetime_str = f"{date} {time}"
            meeting_datetime = datetime.strptime(meeting_datetime_str, "%Y-%m-%d %H:%M")

            cursor = mysql.connection.cursor()

            # Insert into meetings
            cursor.execute(
                "INSERT INTO meetings (address, date, time, status, buyer_id, seller_id, listing_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (address, date, time, 'pending', session.get('user_id'), seller_id, listing_id)
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
                schedule_email(current_app._get_current_object(), meeting_datetime, email, address, immediate=True)

            flash(f'Meeting Scheduled: {time} {date} at {address}', 'success')
            return redirect(url_for('home'))

        elif 'edit' in request.form:
            return redirect(url_for('address.address_page'))

    return render_template('confirm.html', address=address, date=date, time=time)
