from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import os

# Create a Blueprint for the date-time routes
date_time_bp = Blueprint('date_time', __name__, template_folder="../templates")

@date_time_bp.route('/set-date-time', methods=["GET", "POST"])
def set_date_time():
    # Get the address from the query parameters
    address = request.args.get('address')

    if 'edit' in request.form:
            return redirect(url_for('address.address_page')) # redirect to address
    elif request.method == 'POST':
        # Handle form submission (date and time)
        date = request.form.get('date')
        time = request.form.get('time')

        if not date or not time:
            flash("Please provide both a date and time.", "warning")
            return render_template('set_date_time.html', address=address, date=date, time=time)

        session['address'] = address
        session['date'] = date
        session['time'] = time

        return redirect(url_for('confirm.confirm_meeting')) # redirect to confirmation

    # Render the form template for GET requests
    return render_template('set_date_time.html', address=address)
