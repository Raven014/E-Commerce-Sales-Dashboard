# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pandas as pd
# from database import init_db, seed_sample_data, get_product_sales_by_name, get_connection
# from forecaster import build_monthly_forecast

# app = Flask(__name__)
# CORS(app)

# # Initialize DB and seed data (only if empty)
# init_db()
# seed_sample_data()

# from flask import render_template

# @app.route('/')
# def dashboard():
#     return render_template('dashboard.html')


# @app.route('/api/products', methods=['GET'])
# def list_products():
#     """Return all product names for the dropdown."""
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT name FROM products ORDER BY name")
#     rows = cur.fetchall()
#     conn.close()
#     names = [r[0] for r in rows]
#     return jsonify({'products': names})

# @app.route('/api/product-sales', methods=['POST'])
# def product_sales():
#     data = request.get_json()
#     product_name = data.get('product_name')

#     if not product_name:
#         return jsonify({'error': 'product_name is required'}), 400

#     df = get_product_sales_by_name(product_name)

#     if df.empty:
#         return jsonify({'error': 'Product not found or no sales data'}), 404

#     df['date'] = pd.to_datetime(df['date'])

#     # Monthly totals
#     monthly = df.groupby(df['date'].dt.to_period('M'))['sold'].sum().reset_index()
#     monthly['date'] = monthly['date'].dt.to_timestamp()

#     # Yearly total (all years)
#     yearly_total = int(df['sold'].sum())

#     # Use shared forecaster helper for next 3, 6, 12 months
#     future_list, totals = build_monthly_forecast(monthly, periods=12)

#     response = {
#         'product': {
#             'name': df['name'].iloc[0],
#             'category': df['category'].iloc[0]
#         },
#         'monthly': [
#             {'date': d.strftime('%Y-%m'), 'sold': int(s)}
#             for d, s in zip(monthly['date'], monthly['sold'])
#         ],
#         'yearly_total': yearly_total,
#         'forecast_monthly': future_list,
#         'forecast_totals': totals
#     }

#     return jsonify(response)

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)


# from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS
# import os
# import pandas as pd
# from database import init_db, seed_sample_data, get_product_sales_by_name, get_connection
# from forecaster import build_monthly_forecast

# app = Flask(__name__)
# CORS(app)


from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import pandas as pd
from database import init_db, seed_sample_data, get_product_sales_by_name, get_connection
from forecaster import build_monthly_forecast

app = Flask(__name__)

# Allow your local file / Netlify origin while testing
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

API_PASSWORD = os.environ.get("API_PASSWORD", "raven-secret")

@app.before_request
def check_api_password():
    # 1) Allow non-API routes without auth
    if not request.path.startswith("/api/"):
        return

    # 2) Allow CORS preflight (OPTIONS) without auth
    if request.method == "OPTIONS":
        # Let Flask-CORS handle the response
        return

    # 3) Check API key for real API calls
    header_pwd = request.headers.get("X-API-KEY")
    if header_pwd != API_PASSWORD:
        # Optional: debug print
        print("Unauthorized: header:", header_pwd, "expected:", API_PASSWORD)
        return jsonify({"error": "Unauthorized"}), 401


# --------- SIMPLE API PASSWORD PROTECTION ---------
# API_PASSWORD = os.environ.get("API_PASSWORD", "raven-secret")

# @app.before_request
# def check_api_password():
#     # Protect only API routes, not the root "/"
#     if request.path.startswith("/api/"):
#         header_pwd = request.headers.get("X-API-KEY")
#         if header_pwd != API_PASSWORD:
#             return jsonify({"error": "Unauthorized"}), 401
        
# API_PASSWORD = os.environ.get("API_PASSWORD", "raven-secret")

# @app.before_request
# def check_api_password():
#     # Allow non-API routes (like "/") without auth
#     if not request.path.startswith("/api/"):
#         return

#     # Allow CORS preflight (OPTIONS) without auth
#     if request.method == "OPTIONS":
#         return

#     # Check API key for real API calls
#     header_pwd = request.headers.get("X-API-KEY")
#     if header_pwd != API_PASSWORD:
#         return jsonify({"error": "Unauthorized"}), 401


# ---------------------------------------------------

# Initialize DB and seed data (only if empty)
init_db()
seed_sample_data()

@app.route("/")
def dashboard():
    # This is only for local templates; in production, Netlify serves index.html
    return render_template("dashboard.html")

@app.route("/api/products", methods=["GET"])
def list_products():
    """Return all product names for the dropdown."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM products ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    names = [r[0] for r in rows]
    return jsonify({"products": names})

@app.route("/api/product-sales", methods=["POST"])
def product_sales():
    data = request.get_json()
    product_name = data.get("product_name")

    if not product_name:
        return jsonify({"error": "product_name is required"}), 400

    df = get_product_sales_by_name(product_name)

    if df.empty:
        return jsonify({"error": "Product not found or no sales data"}), 404

    df["date"] = pd.to_datetime(df["date"])

    # Monthly totals
    monthly = df.groupby(df["date"].dt.to_period("M"))["sold"].sum().reset_index()
    monthly["date"] = monthly["date"].dt.to_timestamp()

    # Yearly total (all years)
    yearly_total = int(df["sold"].sum())

    # Use shared forecaster helper for next 3, 6, 12 months
    future_list, totals = build_monthly_forecast(monthly, periods=12)

    response = {
        "product": {
            "name": df["name"].iloc[0],
            "category": df["category"].iloc[0],
        },
        "monthly": [
            {"date": d.strftime("%Y-%m"), "sold": int(s)}
            for d, s in zip(monthly["date"], monthly["sold"])
        ],
        "yearly_total": yearly_total,
        "forecast_monthly": future_list,
        "forecast_totals": totals,
    }

    return jsonify(response)

if __name__ == "__main__":
    # For local testing; Render will run via gunicorn
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

