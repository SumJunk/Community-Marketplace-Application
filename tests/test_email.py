from unittest.mock import patch
import pytest
from app import app
from notifications.email_scheduler import send_email

@patch('notifications.email_scheduler.mail.send')  # Mocking Flask-Mail's send method
def test_send_email_reminder(mock_send):
    to = "agraber1@charlotte.edu"
    subject = "Test Subject"
    body = "Test Body"
    
    # Set up the application context to allow Flask-Mail to work
    with app.app_context():
        # Call the function
        send_email(app, to, subject, body)

        # Assert that the send method was called once with the expected message
        mock_send.assert_called_once()
        msg = mock_send.call_args[0][0]  # Extract the message from the call
        assert msg.subject == subject
        assert msg.recipients == [to]
        assert msg.body == body
