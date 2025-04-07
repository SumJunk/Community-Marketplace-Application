import unittest
from flask import Flask
from unittest.mock import patch

# Import the Blueprint from your routes directory
from routes.account import account_bp

class TestAccount(unittest.TestCase):
    def setUp(self):
        "Setup test app to use the testing configuration and register blueprints"
        self.app = Flask(__name__)
        self.app.register_blueprint(account_bp, url_prefix="/account")
        self.client = self.app.test_client()

    @patch('routes.account.mysql.connection')
    def test_check_funds_sufficient(self, mock_connection):
        "Test checking funds with sufficient balance"
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = [100]  # Assuming the balance is 100

        response = self.client.get('/account/check_funds/1/50')
        self.assertIn('Funds are sufficient', response.data.decode())

    @patch('routes.account.mysql.connection')
    def test_add_funds(self, mock_connection):
        "Test adding funds"
        response = self.client.post('/account/add_funds/1', json={'amount': 50})
        self.assertIn('Funds added successfully', response.data.decode())

if __name__ == '__main__':
    unittest.main()
