from flask import Blueprint, render_template, session, redirect, url_for, flash
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

dashboards_bp = Blueprint('dashboards', __name__, template_folder="../templates")
mysql = MySQL()

@dashboards_bp.route('/reviews', methods=['GET'])
def review_dashboard():
    user_id = session.get('user_id')

    # ✅ Only check if user is logged in
    if not user_id:
        flash('Access denied. Please login first.', 'danger')
        return redirect(url_for('home'))

    cursor = mysql.connection.cursor(DictCursor)

    # ✅ Show all listings with review counts and average ratings
    query = """
        SELECT l.id AS listing_id, l.title,
           COUNT(r.id) AS review_count,
           ROUND(AVG(r.rating), 2) AS average_rating
        FROM listings l
        LEFT JOIN reviews r ON r.reviewee_id = l.seller_id
        GROUP BY l.id
    """
    cursor.execute(query)

    data = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', data=data)
