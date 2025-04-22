from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
import requests

# Create a Blueprint for address routes
address_bp = Blueprint("address", __name__, template_folder="../templates")

def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            flash('You need to login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@address_bp.route("/", methods=["GET"])
@login_required
def address_page():
    return render_template("address.html")

@address_bp.route("/search_address", methods=["GET"])
def search_address():
    """Get address suggestions from OpenStreetMap"""
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "countrycodes": "us",
        "limit": 5
    }
    headers = {"User-Agent": "YourAppName/1.0"}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        results = response.json()
        filtered_results = []
        seen_addresses = set()

        for item in results:
            address = item.get("address", {})
            if address.get("country_code") != "us":
                continue

            house_number = address.get("house_number", "")
            street_name = address.get("road") or address.get("pedestrian") or address.get("footway") or ""

            full_street = f"{house_number} {street_name}".strip()
            city = address.get("city") or address.get("town") or address.get("village")
            state = address.get("state")
            postcode = address.get("postcode")

            unique_key = f"{full_street}-{city}-{state}-{postcode}"

            if unique_key in seen_addresses:
                continue

            seen_addresses.add(unique_key)

            filtered_results.append({
                "display_name": item.get("display_name"),
                "street": full_street,
                "city": city,
                "state": state,
                "postcode": postcode
            })

        if not filtered_results:
            return jsonify({"error": "Invalid or unknown location. Please try again."}), 404
        
        return jsonify(filtered_results)
    
    return jsonify({"error": "Failed to fetch data"}), 500

