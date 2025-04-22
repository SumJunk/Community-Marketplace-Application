from flask import Blueprint, render_template, session, redirect, url_for, flash
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

dashboards_bp = Blueprint('dashboards', __name__, template_folder="../templates")
mysql = MySQL()

@dashboards_bp.route('/dashboard/reviews', methods=['GET'])
def review_dashboard():
    user_id = session.get('user_id')
    role = session.get('role')  # Make sure you store this in session during login

    if not user_id or role not in ['seller', 'admin']:
        flash('Access denied. Sellers or Admins only.', 'danger')
        return redirect(url_for('home'))

    cursor = mysql.connection.cursor(DictCursor)

    if role == 'seller':
        query = """
            SELECT l.id AS listing_id, l.title,
                   COUNT(r.id) AS review_count,
                   ROUND(AVG(r.rating), 2) AS average_rating
            FROM listings l
            JOIN reviews r ON r.seller_id = l.seller_id
            WHERE l.seller_id = %s
            GROUP BY l.id
        """
        cursor.execute(query, (user_id,))
    else:
        query = """
            SELECT l.id AS listing_id, l.title,
                   COUNT(r.id) AS review_count,
                   ROUND(AVG(r.rating), 2) AS average_rating
            FROM listings l
            JOIN reviews r ON r.seller_id = l.seller_id
            GROUP BY l.id
        """
        cursor.execute(query)

    data = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', data=data)
