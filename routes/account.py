from flask import Blueprint, request, jsonify
from flask_mysqldb import MySQL

account_bp = Blueprint('account', __name__)

# Check funds for a purchase
@account_bp.route('/check_funds/<int:user_id>/<float:item_price>', methods=['GET'])
def check_funds(user_id, item_price):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_id,))
        balance = cursor.fetchone()
        if balance is None:
            return jsonify({'error': 'Account not found'}), 404

        balance = balance[0]
        if balance >= item_price:
            return jsonify({'can_purchase': True, 'message': 'Funds are sufficient for the purchase.'})
        else:
            return jsonify({'can_purchase': False, 'message': 'Insufficient funds. Please add money to your account.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

# Add funds to the account
@account_bp.route('/add_funds/<int:user_id>', methods=['POST'])
def add_funds(user_id):
    try:
        data = request.get_json()
        amount = data.get('amount')
        if amount <= 0:
            return jsonify({'error': 'Invalid amount. Please enter a positive number.'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': 'Funds added successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

