from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash, current_app
from MySQLdb.cursors import DictCursor

account_bp = Blueprint('account', __name__, template_folder="../templates")

# View account balance page
@account_bp.route('/my-account', methods=['GET'])
def my_account_page():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to login first.', 'warning')
        return redirect(url_for('login'))

    cursor = current_app.extensions['mysql'].connection.cursor(DictCursor)
    cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash('Account not found.', 'danger')
        return redirect(url_for('home'))

    return render_template('my_account.html', balance=user['balance'])

# Add funds (using a form)
@account_bp.route('/my-account/add', methods=['POST'])
def add_funds():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to login first.', 'warning')
        return redirect(url_for('login'))

    amount = float(request.form['amount'])

    if amount <= 0:
        flash('Amount must be positive.', 'danger')
        return redirect(url_for('account.my_account_page'))

    cursor = current_app.extensions['mysql'].connection.cursor()
    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
    current_app.extensions['mysql'].connection.commit()
    cursor.close()

    flash(f'${amount:.2f} added to your account.', 'success')
    return redirect(url_for('account.my_account_page'))

# Insufficient funds page
@account_bp.route('/insufficient-funds')
def insufficient_funds():
    return render_template('insufficient_funds.html')
