from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from config import mysql  # MySQL instance from config.py

responses_bp = Blueprint('responses', __name__, template_folder='../templates')

# -------------------------------
# API: Get all responses (JSON)
# -------------------------------
@responses_bp.route('/', methods=['GET'])
def get_responses():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, review_id, seller_id, response_text FROM responses")
        responses = cursor.fetchall()
        cursor.close()

        response_list = [{'id': r[0], 'review_id': r[1], 'seller_id': r[2], 'response_text': r[3]} for r in responses]
        return jsonify({'responses': response_list})
    except Exception as e:
        return jsonify({'error': str(e)})

# -------------------------------
# API: Add a new response (JSON)
# -------------------------------
@responses_bp.route('/', methods=['POST'])
def add_response():
    try:
        data = request.get_json()
        review_id = data.get('review_id')
        seller_id = data.get('seller_id')
        response_text = data.get('response_text')

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO responses (review_id, seller_id, response_text) VALUES (%s, %s, %s)",
                       (review_id, seller_id, response_text))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': 'Response added successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)})

# -------------------------------
# API: Update a response (JSON)
# -------------------------------
@responses_bp.route('/<int:response_id>', methods=['PUT'])
def update_response(response_id):
    try:
        data = request.get_json()
        response_text = data.get('response_text')

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE responses SET response_text = %s WHERE id = %s", (response_text, response_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': f'Response ID {response_id} updated successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)})

# -------------------------------
# API: Delete a response (JSON)
# -------------------------------
@responses_bp.route('/<int:response_id>', methods=['DELETE'])
def delete_response(response_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM responses WHERE id = %s", (response_id,))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': f'Response ID {response_id} deleted successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)})

# -------------------------------
# HTML: View and submit responses
# -------------------------------
@responses_bp.route('/view', methods=['GET', 'POST'])
def view_responses():
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        review_id = request.form['review_id']
        seller_id = request.form['seller_id']
        response_text = request.form['response_text']

        cursor.execute(
            "INSERT INTO responses (review_id, seller_id, response_text, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
            (review_id, seller_id, response_text)
        )
        mysql.connection.commit()
        return redirect(url_for('responses.view_responses'))

    cursor.execute("SELECT id, review_id, seller_id, response_text FROM responses")
    responses = cursor.fetchall()
    cursor.close()
    return render_template('responses.html', responses=responses)
