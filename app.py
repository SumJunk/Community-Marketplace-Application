from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_mysqldb import MySQL
from flask_mail import Mail
from routes.listing import listings_bp
from routes.dashbaords import dashboards_bp
import os
import config

from routes.address import address_bp
from routes.date_time import date_time_bp
from routes.confirm import confirm_bp
from routes.my_meetings import meeting_bp
<<<<<<< HEAD
from routes.account import account_bp
=======
from routes.listing import listings_bp
from routes.settings import settings_bp
>>>>>>> 2cecb23804793a621895259992577f36b159b3d9

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

app.config['MYSQL_HOST'] = config.MYSQL_CONFIG['host']
app.config['MYSQL_USER'] = config.MYSQL_CONFIG['user']
app.config['MYSQL_PASSWORD'] = config.MYSQL_CONFIG['password']
app.config['MYSQL_DB'] = config.MYSQL_CONFIG['database']

mysql = MySQL(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'

mail = Mail(app)

MAX_ATTEMPTS = 5
LOCKOUT_TIME_MINUTES = 5

app.register_blueprint(address_bp, url_prefix="/address")
app.register_blueprint(date_time_bp, url_prefix="/date-time")
app.register_blueprint(listings_bp, url_prefix='/listings')
app.register_blueprint(confirm_bp, url_prefix="/confirm")
app.register_blueprint(meeting_bp, url_prefix="/my_meetings")
<<<<<<< HEAD
app.register_blueprint(account_bp, url_prefix="/account")
=======
app.register_blueprint(settings_bp, url_prefix="/settings")
>>>>>>> 2cecb23804793a621895259992577f36b159b3d9
listings_bp.upload_folder = app.config['UPLOAD_FOLDER']
app.register_blueprint(dashboards_bp, url_prefix="/dashboard")


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s", (username, password)
        )
        user = cursor.fetchone()

        if user:
            if len(user) == 6:
                user_id, username, stored_password, failed_attempts, lockout_time, email = user
            elif len(user) == 4:
                user_id, username, stored_password, email = user
                failed_attempts = 0
                lockout_time = None
            else:
                return "Unexpected user data structure."
        
            if lockout_time and datetime.now() < lockout_time:
                flash(f'Account locked. Please try again after 5 minutes.')
                return redirect(url_for('login'))


            if password == stored_password:

                cursor.execute(
                    "UPDATE users SET failed_attempts = 0, lockout_time = NULL WHERE id = %s",
                    (user_id,)
                )
                mysql.connection.commit()
                cursor.close()

  
                session['logged_in'] = True
                session['user_id'] = user[0]
                session['username'] = username
                session['email'] = email
                flash('Login successful!')
                return redirect(url_for('home'))
            else:
                failed_attempts += 1
                if failed_attempts >= MAX_ATTEMPTS:
                    lockout_time = datetime.now() + timedelta(minutes=LOCKOUT_TIME_MINUTES)
                    cursor.execute(
                        "UPDATE users SET failed_attempts = %s, lockout_time = %s WHERE id = %s",
                        (failed_attempts, lockout_time, user_id)
                    )
                    flash(f'Too many failed attempts. Your account is locked for {LOCKOUT_TIME_MINUTES} minutes.')
                else:
                    cursor.execute(
                        "UPDATE users SET failed_attempts = %s WHERE id = %s",
                        (failed_attempts, user_id)
                    )
                    flash('Invalid username or password.')

                mysql.connection.commit()
                cursor.close()
        else:
            flash('Invalid username or password.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('email', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        cursor.execute(
            "INSERT INTO users (username, password, email, failed_attempts, lockout_time) VALUES (%s, %s, %s, 0, NULL)",
            (username, password, email)
        )
        mysql.connection.commit()
        cursor.close()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True, port=5500)


