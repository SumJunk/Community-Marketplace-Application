from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename

listings_bp = Blueprint('listings', __name__)

mysql = MySQL()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            flash('You need to login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap


@listings_bp.route('/create-listing', methods=['GET', 'POST'])
@login_required
def create_listing_page():
    if request.method == 'POST':
        seller_id = session.get('user_id')

        if not seller_id:
            flash('Error: Please log in.')
            return redirect(url_for('login'))

        title = request.form['title']
        price = request.form['price']
        category = request.form['category']
        description = request.form['description']
        
        image = request.files['image']
        image_url = None
        
        upload_folder = listings_bp.upload_folder

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(upload_folder, filename))
            image_url = os.path.join('uploads', filename)

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO listings (seller_id, title, price, category, description, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
            (seller_id, title, price, category, description, image_url)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': 'Listing created successfully'}), 201

    return render_template('create_listing.html')


@listings_bp.route('/my-listings', methods=['GET'])
@login_required
def my_listings():
    seller_id = session.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, title, price, category, description, image_url FROM listings WHERE seller_id = %s", (seller_id,))
    listings = cursor.fetchall()
    cursor.close()

    return render_template('my_listings.html', listings=listings)

@listings_bp.route('/edit-listing/<int:listing_id>', methods=['GET', 'POST'], endpoint='edit_listing')
@login_required
def edit_listing(listing_id):
    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM listings WHERE id = %s AND seller_id = %s", (listing_id, user_id))
    listing = cursor.fetchone()

    if not listing:
        flash("Listing not found or you don't have permission to edit it.", "danger")
        return redirect(url_for('listings.my_listings'))

    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        category = request.form['category']
        description = request.form['description']

        cursor.execute(
            "UPDATE listings SET title = %s, price = %s, category = %s, description = %s WHERE id = %s",
            (title, price, category, description, listing_id)
        )
        mysql.connection.commit()
        flash('Listing updated successfully.', 'success')
        return redirect(url_for('listings.my_listings'))

    return render_template('edit_listings.html', listing=listing)
