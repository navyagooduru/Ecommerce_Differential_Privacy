import sqlite3
from differential_privacy import add_laplace_noise


# =========================================================
# DATABASE
# =========================================================

DATABASE = "shop.db"

# Privacy parameter
EPSILON = 1.0

# Sensitivity for counting users
SENSITIVITY = 1


# =========================================================
# GENERATE DIFFERENTIAL PRIVACY ANALYTICS
# =========================================================

def generate_dp_analytics():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    # Create table for DP results
    connection.execute("""
        CREATE TABLE IF NOT EXISTS privacy_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            product_name TEXT,
            activity_type TEXT,
            original_count INTEGER,
            protected_count REAL,
            epsilon REAL
        )
    """)

    # Remove old DP results
    connection.execute("""
        DELETE FROM privacy_analytics
    """)

    # Get all products
    products = connection.execute("""
        SELECT
            product_id,
            product_name
        FROM products
    """).fetchall()

    # Activities we want to analyse
    activities = [
        "view",
        "add_to_cart",
        "purchase"
    ]

    # Process every product
    for product in products:

        for activity in activities:

            result = connection.execute("""
                SELECT COUNT(DISTINCT user_id) AS user_count
                FROM interactions
                WHERE product_id = ?
                AND interaction_type = ?
            """, (
                product["product_id"],
                activity
            )).fetchone()

            original_count = result["user_count"]

            # Apply Laplace mechanism
            protected_count = add_laplace_noise(
                original_count,
                sensitivity=SENSITIVITY,
                epsilon=EPSILON
            )

            # Prevent negative counts
            protected_count = max(0, round(protected_count))
            # Store result
            connection.execute("""
                INSERT INTO privacy_analytics
                (
                    product_id,
                    product_name,
                    activity_type,
                    original_count,
                    protected_count,
                    epsilon
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                product["product_id"],
                product["product_name"],
                activity,
                original_count,
                round(protected_count, 2),
                EPSILON
            ))

    connection.commit()

    connection.close()

    print()
    print("==============================================")
    print("Differential Privacy Analytics Generated")
    print("==============================================")
    print("Epsilon:", EPSILON)
    print("Sensitivity:", SENSITIVITY)
    print("Laplace Scale:", SENSITIVITY / EPSILON)
    print()
    print("Data stored in: privacy_analytics")
    print("==============================================")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    generate_dp_analytics()