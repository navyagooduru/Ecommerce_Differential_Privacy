import sqlite3


DATABASE = "shop.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # =========================================================
    # USERS TABLE
    # =========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # =========================================================
    # PRODUCTS TABLE
    # =========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT UNIQUE NOT NULL,
            category TEXT,
            brand TEXT,
            price REAL
        )
    """)

    # Check product columns
    cursor.execute("PRAGMA table_info(products)")
    product_columns = [row[1] for row in cursor.fetchall()]

    if "product_name" not in product_columns:
        cursor.execute("""
            ALTER TABLE products
            ADD COLUMN product_name TEXT
        """)

    if "image" not in product_columns:
        cursor.execute("""
            ALTER TABLE products
            ADD COLUMN image TEXT
        """)

    if "description" not in product_columns:
        cursor.execute("""
            ALTER TABLE products
            ADD COLUMN description TEXT
        """)

    # =========================================================
    # INTERACTIONS TABLE
    # =========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            product_id TEXT,
            interaction_type TEXT
        )
    """)

    # =========================================================
    # CART TABLE
    # =========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            UNIQUE(user_id, product_id)
        )
    """)

    # =========================================================
    # ORDERS TABLE
    # =========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            total_price REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check order columns
    cursor.execute("PRAGMA table_info(orders)")
    order_columns = [row[1] for row in cursor.fetchall()]

    if "address" not in order_columns:
        cursor.execute("""
            ALTER TABLE orders
            ADD COLUMN address TEXT
        """)

    if "city" not in order_columns:
        cursor.execute("""
            ALTER TABLE orders
            ADD COLUMN city TEXT
        """)

    if "pincode" not in order_columns:
        cursor.execute("""
            ALTER TABLE orders
            ADD COLUMN pincode TEXT
        """)

    if "payment_method" not in order_columns:
        cursor.execute("""
            ALTER TABLE orders
            ADD COLUMN payment_method TEXT
        """)

    # =========================================================
    # ORDER ITEMS TABLE
    # =========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    connection.commit()
    connection.close()