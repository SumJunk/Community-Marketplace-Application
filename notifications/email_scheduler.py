from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, datetime
from flask_mail import Message
from notifications.extensions import mail

scheduler = BackgroundScheduler()
scheduler.start()

def send_email(app, email, subject, body):
    with app.app_context():
        msg = Message(subject, recipients=[email])
        msg.body = body
        mail.send(msg)

def schedule_email(app, meeting_time, email, address, immediate):
    if immediate:
        scheduler.add_job(
            func=lambda: send_email(
                app._get_current_object(),
                email,
                "Meeting Confirmed",
                f"Your meeting is confirmed for {meeting_time.strftime('%Y-%m-%d %H:%M')} at {address}."
            ),
            trigger='date',
            run_date=datetime.now() + timedelta(seconds=1)  # run almost immediately
        )

    reminder_time_one = meeting_time - timedelta(minutes=180)
    reminder_time_two = meeting_time - timedelta(minutes=30)

    if reminder_time_one:
        scheduler.add_job(
            func=lambda: send_email(
                app,
                email,
                "Meeting Reminder",
                f"Your meeting at {address} is in 3 hours, scheduled at {meeting_time}."
            ),
            trigger='date',
            run_date=reminder_time_one
        )

    if reminder_time_two:
        scheduler.add_job(
            func=lambda: send_email(
                app,
                email,
                "Meeting Reminder",
                f"Your meeting at {address} is in 30 minutes, scheduled at {meeting_time}."
            ),
            trigger='date',
            run_date=reminder_time_two
        )
