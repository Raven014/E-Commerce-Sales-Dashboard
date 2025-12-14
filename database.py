import sqlite3
from datetime import datetime
import pandas as pd
from datetime import datetime

DB_PATH = '../data/sales.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            sold INTEGER NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')

    conn.commit()
    conn.close()

def seed_sample_data():
    """
    Insert products and recent monthly sales around the current year.
    Uses current year and previous year for more data.
    """
    conn = get_connection()
    c = conn.cursor()

    products = [
        ('Red T-Shirt', 'Clothing'),
        ('Blue Jeans', 'Clothing'),
        ('Black Hoodie', 'Clothing'),
        ('Wireless Mouse', 'Electronics'),
        ('Mechanical Keyboard', 'Electronics'),
        ('Gaming Headset', 'Electronics'),
        ('Water Bottle 1L', 'Home'),
        ('Coffee Mug', 'Home'),
        ('Office Chair', 'Furniture'),
        ('Study Table', 'Furniture')
    ]

    # Insert products if not present
    for name, category in products:
        c.execute(
            'INSERT OR IGNORE INTO products (name, category) VALUES (?, ?)',
            (name, category)
        )

    # Clear old sales so we reseed cleanly (optional but easier)
    c.execute('DELETE FROM sales')

    # Use current year and previous year
    current_year = datetime.now().year
    years = [current_year - 1, current_year]

    product_rows = c.execute('SELECT id, name FROM products').fetchall()

    for pid, name in product_rows:
        for year in years:
            for month in range(1, 13):
                # Only insert months up to current month in current year
                if year == current_year and month > datetime.now().month:
                    continue

                date = f'{year}-{month:02d}-01'

                # Base sold depends on product
                base = 50
                if 'T-Shirt' in name:
                    base = 80
                elif 'Jeans' in name:
                    base = 110
                elif 'Hoodie' in name:
                    base = 90
                elif 'Mouse' in name:
                    base = 130
                elif 'Keyboard' in name:
                    base = 120
                elif 'Headset' in name:
                    base = 140
                elif 'Bottle' in name:
                    base = 75
                elif 'Mug' in name:
                    base = 65
                elif 'Chair' in name:
                    base = 55
                elif 'Table' in name:
                    base = 60

                # Add monthly growth and yearly bump
                sold = base + month * 6 + (year - (current_year - 1)) * 25

                c.execute(
                    'INSERT INTO sales (product_id, date, sold) VALUES (?, ?, ?)',
                    (pid, date, sold)
                )

    conn.commit()
    conn.close()


def get_product_sales_by_name(product_name: str) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT p.id, p.name, p.category, s.date, s.sold
        FROM products p
        JOIN sales s ON p.id = s.product_id
        WHERE p.name = ?
        ORDER BY s.date
    """
    df = pd.read_sql_query(query, conn, params=(product_name,))
    conn.close()
    return df
