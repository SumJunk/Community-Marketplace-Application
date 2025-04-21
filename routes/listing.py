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
            image_url = f'uploads/{filename}'
            image_url = image_url.replace('\\', '/')  # Normalize for web

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO listings (seller_id, title, price, category, description, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
            (seller_id, title, price, category, description, image_url)
        )
        mysql.connection.commit()
        cursor.close()

        flash('Listing created successfully!', 'success')

        # Redirect to 'My Listings' page
        return redirect(url_for('listings.my_listings'))

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

@listings_bp.route('/', methods=['GET'])
@login_required
def all_listings():
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = """
    SELECT 
        l.id, l.title, l.price, l.category, l.description, l.image_url,
        u.username AS seller_name,
        p.id AS purchase_id,
        l.seller_id
    FROM listings l
    JOIN users u ON l.seller_id = u.id
    LEFT JOIN purchases p ON p.listing_id = l.id
    WHERE 1=1
    """
    params = []

    if category and category.lower() != 'all':
        query += " AND l.category = %s"
        params.append(category)

    if search:
        query += " AND (l.title LIKE %s OR l.description LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    cursor = mysql.connection.cursor()
    cursor.execute(query, params)
    listings = cursor.fetchall()
    cursor.close()

    return render_template('all_listings.html', listings=listings, selected_category=category or 'All', search=search or '')

@listings_bp.route('/purchase/<int:listing_id>', methods=['POST'])
@login_required
def purchase_item(listing_id):
    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()

    # Get listing and seller ID
    cursor.execute("SELECT seller_id FROM listings WHERE id = %s", (listing_id,))
    listing = cursor.fetchone()

    if not listing:
        flash("Listing not found.", "danger")
        return redirect(url_for('listings.all_listings'))

    seller_id = listing[0]
    if seller_id == user_id:
        flash("You cannot purchase your own listing.", "warning")
        return redirect(url_for('listings.all_listings'))

    # Check if already purchased
    cursor.execute("SELECT * FROM purchases WHERE listing_id = %s", (listing_id,))
    if cursor.fetchone():
        flash("This item has already been purchased.", "info")
        cursor.close()
        return redirect(url_for('listings.all_listings'))


    session['listing_id'] = listing_id
    cursor.close()
    flash("Purchase initiated. Please enter your address.", "info")
    return redirect(url_for('address.address_page'))


@listings_bp.route('/delete/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    user_id = session.get('user_id')
    conn = mysql.connection
    cursor = conn.cursor()

    # Fetch the listing to check ownership and image
    cursor.execute('SELECT seller_id, image_url FROM listings WHERE id = %s', (listing_id,))
    listing = cursor.fetchone()

    if not listing:
        flash('Listing not found.', 'error')
        cursor.close()
        return redirect(url_for('listings.all_listings'))

    seller_id, image_url = listing

    if seller_id != user_id:
        flash('You are not authorized to delete this listing.', 'error')
        cursor.close()
        return redirect(url_for('listings.all_listings'))

    # Delete listing
    cursor.execute('DELETE FROM purchases WHERE listing_id = %s', (listing_id,))
    cursor.execute('DELETE FROM listings WHERE id = %s', (listing_id,))
    conn.commit()
    cursor.close()

    # Optional cleanup: remove image file from disk
    if image_url:
        image_path = os.path.join(listings_bp.upload_folder, os.path.basename(image_url))
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"Warning: Could not delete image file. {e}")

    flash('Listing deleted successfully!', 'success')
    return redirect(url_for('listings.my_listings'))