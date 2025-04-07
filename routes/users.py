from flask import Blueprint, request, jsonify
from config import mysql

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/', methods=['GET'])
def get_users():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, first_name, last_name FROM users")
        users = cursor.fetchall()
        cursor.close()

        user_list = [{'id': user[0], 'first_name': user[1], 'last_name': user[2]} for user in users]

        return jsonify({'users': user_list})
    except Exception as e:
        return jsonify({'error': str(e)})
 
@users_bp.route('/', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if not first_name or not last_name:
            return jsonify({'error': 'Both first_name and last_name are required!'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (first_name, last_name) VALUES (%s, %s)", (first_name, last_name))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': 'User added successfully!', 'first_name': first_name, 'last_name': last_name})
    except Exception as e:
        return jsonify({'error': str(e)})

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': f'User ID {user_id} deleted successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)})
