from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash, current_app
from MySQLdb.cursors import DictCursor

reviews_bp = Blueprint('reviews', __name__, template_folder='../templates')

# -------------------------------
# HTML Page: View and Submit Reviews
# -------------------------------
@reviews_bp.route('/listing/<int:seller_id>', methods=['GET', 'POST'])
def listing_reviews(seller_id):
    cursor = current_app.extensions['mysql'].connection.cursor(DictCursor)

    # Handle new review submission
    if request.method == 'POST':
        rating = request.form['rating']
        review_text = request.form['review_text']
        customer_id = session.get('user_id')

        cursor.execute(
            "INSERT INTO reviews (seller_id, customer_id, rating, review_text) VALUES (%s, %s, %s, %s)",
            (seller_id, customer_id, rating, review_text)
        )
        current_app.extensions['mysql'].connection.commit()
        flash('Review submitted successfully!')
        return redirect(url_for('reviews.listing_reviews', seller_id=seller_id))

    # Fetch all reviews for the seller
    cursor.execute("SELECT * FROM reviews WHERE seller_id = %s", (seller_id,))
    reviews = cursor.fetchall()

    # Fetch responses for each review
    enriched_reviews = []
    for review in reviews:
        cursor.execute("SELECT response_text FROM responses WHERE review_id = %s", (review['id'],))
        responses = cursor.fetchall()
        review['responses'] = responses
        enriched_reviews.append(review)

    cursor.close()
    return render_template('reviews.html', reviews=enriched_reviews, seller_id=seller_id)

# -------------------------------
# Respond to a review
# -------------------------------
@reviews_bp.route('/<int:review_id>/responses', methods=['POST'])
def add_response(review_id):
    try:
        data = request.form
        seller_id = data.get('seller_id')
        response_text = data.get('response_text')

        cursor = current_app.extensions['mysql'].connection.cursor()
        cursor.execute(
            "INSERT INTO responses (review_id, seller_id, response_text, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
            (review_id, seller_id, response_text)
        )
        current_app.extensions['mysql'].connection.commit()
        cursor.close()

        flash('Response submitted successfully!')
        return redirect(request.referrer)
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------
# API: Get all reviews (JSON)
# -------------------------------
@reviews_bp.route('/api', methods=['GET'])
def get_reviews_json():
    try:
        cursor = current_app.extensions['mysql'].connection.cursor()
        cursor.execute("SELECT id, seller_id, customer_id, rating, review_text FROM reviews")
        reviews = cursor.fetchall()
        cursor.close()

        review_list = [
            {'id': r[0], 'seller_id': r[1], 'customer_id': r[2], 'rating': r[3], 'review_text': r[4]}
            for r in reviews
        ]
        return jsonify({'reviews': review_list})
    except Exception as e:
        return jsonify({'error': str(e)})

# -------------------------------
# API: Add new review (JSON)
# -------------------------------
@reviews_bp.route('/api', methods=['POST'])
def add_review_json():
    try:
        data = request.get_json()
        seller_id = data.get('seller_id')
        customer_id = data.get('customer_id')
        rating = data.get('rating')
        review_text = data.get('review_text')

        cursor = current_app.extensions['mysql'].connection.cursor()
        cursor.execute(
            "INSERT INTO reviews (seller_id, customer_id, rating, review_text) VALUES (%s, %s, %s, %s)",
            (seller_id, customer_id, rating, review_text)
        )
        current_app.extensions['mysql'].connection.commit()
        cursor.close()

        return jsonify({'message': 'Review added successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)})

@reviews_bp.route('/add', methods=['POST'])
def add_review():
    try:
        rating = request.form['rating']
        review_text = request.form['review_text']
        seller_id = request.form['seller_id']
        customer_id = session.get('user_id')

        cursor = current_app.extensions['mysql'].connection.cursor()
        cursor.execute(
            "INSERT INTO reviews (seller_id, customer_id, rating, review_text) VALUES (%s, %s, %s, %s)",
            (seller_id, customer_id, rating, review_text)
        )
        current_app.extensions['mysql'].connection.commit()
        cursor.close()

        flash('Review submitted successfully!')
        return redirect(url_for('reviews.listing_reviews', seller_id=seller_id))

    except Exception as e:
        return f"Error: {str(e)}"
