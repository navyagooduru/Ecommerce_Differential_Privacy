from flask import Flask, render_template, request, redirect, url_for, session

from database import get_connection, create_tables
from differential_privacy import add_laplace_noise
from recommendations import get_recommendations


app = Flask(__name__)


# =========================================================
# FLASK SETTINGS
# =========================================================

app.secret_key = "shopsmart-secret-key"


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

create_tables()


# =========================================================
# HOME RECOMMENDATIONS
# =========================================================

def get_home_recommendations():

    # User must be logged in
    if "user_id" not in session:
        return []

    user_id = session["user_id"]

    connection = get_connection()

    # Find the user's latest interaction
    latest_interaction = connection.execute(
        """
        SELECT product_id
        FROM interactions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    ).fetchone()

    connection.close()

    # If the user has shopping activity,
    # generate personalized recommendations
    if latest_interaction:

        try:

            recommendations = get_recommendations(
                user_id=user_id,
                current_product_id=latest_interaction["product_id"],
                limit=5
            )

            if recommendations:
                return recommendations

        except Exception:
            pass

    # If there is no recommendation yet,
    # show popular products
    connection = get_connection()

    popular_products = connection.execute(
        """
        SELECT
            products.product_id,
            products.product_name,
            products.category,
            products.price,
            products.image,
            products.description,
            COUNT(interactions.id) AS interaction_count
        FROM products
        LEFT JOIN interactions
        ON products.product_id = interactions.product_id
        GROUP BY
            products.product_id,
            products.product_name,
            products.category,
            products.price,
            products.image,
            products.description
        ORDER BY
            interaction_count DESC,
            products.id ASC
        LIMIT 5
        """
    ).fetchall()

    connection.close()

    return popular_products


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    search_query = request.args.get(
        "search",
        ""
    ).strip()

    connection = get_connection()

    # -----------------------------------------------------
    # SEARCH PRODUCTS
    # -----------------------------------------------------

    if search_query:

        search_pattern = f"%{search_query}%"

        products = connection.execute(
            """
            SELECT
                product_id,
                product_name,
                category,
                price,
                image,
                description
            FROM products
            WHERE LOWER(product_name) LIKE LOWER(?)
               OR LOWER(category) LIKE LOWER(?)
               OR LOWER(brand) LIKE LOWER(?)
               OR LOWER(description) LIKE LOWER(?)
            ORDER BY product_name ASC
            """,
            (
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern
            )
        ).fetchall()

    # -----------------------------------------------------
    # NORMAL HOME PAGE PRODUCTS
    # -----------------------------------------------------

    else:

        products = connection.execute(
            """
            SELECT
                product_id,
                product_name,
                category,
                price,
                image,
                description
            FROM products
            ORDER BY id
            LIMIT 12
            """
        ).fetchall()

    connection.close()

    # -----------------------------------------------------
    # RECOMMENDATIONS
    # -----------------------------------------------------

    recommendations = []

    if not search_query:
        recommendations = get_home_recommendations()

    return render_template(
        "home.html",
        products=products,
        recommendations=recommendations,
        search_query=search_query
    )


# =========================================================
# CATEGORY PAGE
# =========================================================

@app.route("/category/<category_name>")
def category(category_name):

    connection = get_connection()

    products = connection.execute(
        """
        SELECT
            product_id,
            product_name,
            category,
            price,
            image,
            description
        FROM products
        WHERE LOWER(category) = LOWER(?)
        ORDER BY id
        """,
        (category_name,)
    ).fetchall()

    connection.close()

    return render_template(
        "category.html",
        products=products,
        category_name=category_name
    )


# =========================================================
# PRODUCT DETAILS
# =========================================================

@app.route("/product/<product_id>")
def product_details(product_id):

    connection = get_connection()

    product = connection.execute(
        """
        SELECT
            product_id,
            product_name,
            category,
            price,
            image,
            description
        FROM products
        WHERE product_id = ?
        """,
        (product_id,)
    ).fetchone()

    connection.close()

    if not product:
        return "Product not found."

    # -----------------------------------------------------
    # RECORD PRODUCT VIEW
    # -----------------------------------------------------

    if "user_id" in session:

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO interactions
            (
                user_id,
                product_id,
                interaction_type
            )
            VALUES (?, ?, ?)
            """,
            (
                session["user_id"],
                product_id,
                "view"
            )
        )

        connection.commit()
        connection.close()

        # -------------------------------------------------
        # GENERATE RECOMMENDATIONS
        # -------------------------------------------------

        recommendations = get_recommendations(
            user_id=session["user_id"],
            current_product_id=product_id,
            limit=5
        )

    else:

        recommendations = []

    return render_template(
        "product_details.html",
        product=product,
        recommendations=recommendations
    )


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not name:
            return "Please enter your name."

        if not email:
            return "Please enter your email."

        if not password:
            return "Please enter your password."

        connection = get_connection()

        # -------------------------------------------------
        # CHECK EXISTING USER
        # -------------------------------------------------

        existing_user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:

            connection.close()

            return "Email already registered."

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        connection.execute(
            """
            INSERT INTO users
            (
                user_id,
                name,
                email,
                password
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                email,
                name,
                email,
                password
            )
        )

        connection.commit()
        connection.close()

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_connection()

        user = connection.execute(
            """
            SELECT
                user_id,
                name,
                email,
                password
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        # -------------------------------------------------
        # LOGIN SUCCESS
        # -------------------------------------------------

        if user and user["password"] == password:

            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]

            return redirect(
                url_for("home")
            )

        return "Invalid email or password."

    return render_template(
        "login.html"
    )


# =========================================================
# ADD TO CART
# =========================================================

@app.route(
    "/add_to_cart/<product_id>",
    methods=["POST"]
)
def add_to_cart(product_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    connection = get_connection()

    # -----------------------------------------------------
    # CHECK PRODUCT
    # -----------------------------------------------------

    product = connection.execute(
        """
        SELECT product_id
        FROM products
        WHERE product_id = ?
        """,
        (product_id,)
    ).fetchone()

    if not product:

        connection.close()

        return "Product not found."

    # -----------------------------------------------------
    # CHECK EXISTING CART ITEM
    # -----------------------------------------------------

    existing_item = connection.execute(
        """
        SELECT quantity
        FROM cart
        WHERE user_id = ?
        AND product_id = ?
        """,
        (
            user_id,
            product_id
        )
    ).fetchone()

    if existing_item:

        connection.execute(
            """
            UPDATE cart
            SET quantity = quantity + 1
            WHERE user_id = ?
            AND product_id = ?
            """,
            (
                user_id,
                product_id
            )
        )

    else:

        connection.execute(
            """
            INSERT INTO cart
            (
                user_id,
                product_id,
                quantity
            )
            VALUES (?, ?, 1)
            """,
            (
                user_id,
                product_id
            )
        )

    # -----------------------------------------------------
    # RECORD SHOPPING BEHAVIOUR
    # -----------------------------------------------------

    connection.execute(
        """
        INSERT INTO interactions
        (
            user_id,
            product_id,
            interaction_type
        )
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            product_id,
            "add_to_cart"
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("cart")
    )


# =========================================================
# INCREASE CART QUANTITY
# =========================================================

@app.route(
    "/increase/<product_id>",
    methods=["POST"]
)
def increase_quantity(product_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    connection.execute(
        """
        UPDATE cart
        SET quantity = quantity + 1
        WHERE user_id = ?
        AND product_id = ?
        """,
        (
            session["user_id"],
            product_id
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("cart")
    )


# =========================================================
# DECREASE CART QUANTITY
# =========================================================

@app.route(
    "/decrease/<product_id>",
    methods=["POST"]
)
def decrease_quantity(product_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    item = connection.execute(
        """
        SELECT quantity
        FROM cart
        WHERE user_id = ?
        AND product_id = ?
        """,
        (
            session["user_id"],
            product_id
        )
    ).fetchone()

    if item:

        if item["quantity"] > 1:

            connection.execute(
                """
                UPDATE cart
                SET quantity = quantity - 1
                WHERE user_id = ?
                AND product_id = ?
                """,
                (
                    session["user_id"],
                    product_id
                )
            )

        else:

            connection.execute(
                """
                DELETE FROM cart
                WHERE user_id = ?
                AND product_id = ?
                """,
                (
                    session["user_id"],
                    product_id
                )
            )

    connection.commit()
    connection.close()

    return redirect(
        url_for("cart")
    )


# =========================================================
# CART PAGE
# =========================================================

@app.route("/cart")
def cart():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    items = connection.execute(
        """
        SELECT
            products.product_id,
            products.product_name,
            products.category,
            products.price,
            products.image,
            products.description,
            cart.quantity
        FROM cart
        JOIN products
        ON cart.product_id = products.product_id
        WHERE cart.user_id = ?
        """,
        (
            session["user_id"],
        )
    ).fetchall()

    # -----------------------------------------------------
    # CALCULATE TOTAL
    # -----------------------------------------------------

    total = 0

    for item in items:

        total += (
            item["price"]
            * item["quantity"]
        )

    connection.close()

    return render_template(
        "cart.html",
        items=items,
        total=total
    )


# =========================================================
# CHECKOUT
# =========================================================

@app.route("/checkout")
def checkout():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    cart_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM cart
        WHERE user_id = ?
        """,
        (
            session["user_id"],
        )
    ).fetchone()[0]

    connection.close()

    if cart_count == 0:

        return redirect(
            url_for("cart")
        )

    return render_template(
        "checkout.html"
    )


# =========================================================
# PLACE ORDER
# =========================================================

@app.route(
    "/place_order",
    methods=["POST"]
)
def place_order():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    # -----------------------------------------------------
    # GET CHECKOUT DETAILS
    # -----------------------------------------------------

    address = request.form.get(
        "address",
        ""
    ).strip()

    city = request.form.get(
        "city",
        ""
    ).strip()

    pincode = request.form.get(
        "pincode",
        ""
    ).strip()

    payment_method = request.form.get(
        "payment_method",
        ""
    ).strip()

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not address:
        return "Please enter your delivery address."

    if not city:
        return "Please enter your city."

    if not pincode:
        return "Please enter your PIN code."

    if not payment_method:
        return "Please select a payment method."

    connection = get_connection()

    # -----------------------------------------------------
    # GET CART ITEMS
    # -----------------------------------------------------

    cart_items = connection.execute(
        """
        SELECT
            product_id,
            quantity
        FROM cart
        WHERE user_id = ?
        """,
        (
            user_id,
        )
    ).fetchall()

    if not cart_items:

        connection.close()

        return redirect(
            url_for("cart")
        )

    # -----------------------------------------------------
    # CALCULATE TOTAL
    # -----------------------------------------------------

    total_price = 0

    for item in cart_items:

        product = connection.execute(
            """
            SELECT price
            FROM products
            WHERE product_id = ?
            """,
            (
                item["product_id"],
            )
        ).fetchone()

        if product:

            total_price += (
                product["price"]
                * item["quantity"]
            )

    # -----------------------------------------------------
    # CREATE ORDER
    # -----------------------------------------------------

    cursor = connection.execute(
        """
        INSERT INTO orders
        (
            user_id,
            total_price,
            address,
            city,
            pincode,
            payment_method
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            total_price,
            address,
            city,
            pincode,
            payment_method
        )
    )

    order_id = cursor.lastrowid

    # -----------------------------------------------------
    # ADD PRODUCTS TO ORDER
    # -----------------------------------------------------

    for item in cart_items:

        product = connection.execute(
            """
            SELECT price
            FROM products
            WHERE product_id = ?
            """,
            (
                item["product_id"],
            )
        ).fetchone()

        if product:

            connection.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    price
                )
                VALUES (?, ?, ?)
                """,
                (
                    order_id,
                    item["product_id"],
                    product["price"]
                )
            )

    # -----------------------------------------------------
    # RECORD PURCHASES AS INTERACTIONS
    # -----------------------------------------------------

    for item in cart_items:

        connection.execute(
            """
            INSERT INTO interactions
            (
                user_id,
                product_id,
                interaction_type
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                item["product_id"],
                "purchase"
            )
        )

    # -----------------------------------------------------
    # CLEAR CART
    # -----------------------------------------------------

    connection.execute(
        """
        DELETE FROM cart
        WHERE user_id = ?
        """,
        (
            user_id,
        )
    )

    connection.commit()
    connection.close()

    return render_template(
        "order_success.html",
        order_id=order_id
    )


# =========================================================
# MY ORDERS
# =========================================================

@app.route("/orders")
def orders():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    orders_data = connection.execute(
        """
        SELECT
            id,
            total_price,
            order_date,
            address,
            city,
            pincode,
            payment_method
        FROM orders
        WHERE user_id = ?
        ORDER BY order_date DESC
        """,
        (
            session["user_id"],
        )
    ).fetchall()

    connection.close()

    return render_template(
        "orders.html",
        orders=orders_data
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# USER INTERACTIONS
# =========================================================

@app.route("/interactions")
def interactions():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            products.product_name,
            products.category,
            interactions.interaction_type,
            COUNT(*) AS times
        FROM interactions
        JOIN products
        ON interactions.product_id = products.product_id
        WHERE interactions.user_id = ?
        GROUP BY
            products.product_name,
            products.category,
            interactions.interaction_type
        ORDER BY times DESC
        """,
        (
            session["user_id"],
        )
    ).fetchall()

    connection.close()

    return render_template(
        "interactions.html",
        interactions=rows
    )


# =========================================================
# PRIVACY ANALYTICS
# =========================================================

@app.route(
    "/privacy-analytics",
    methods=["GET", "POST"]
)
def privacy_analytics():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    # -----------------------------------------------------
    # SHOW ANALYTICS KEY PAGE
    # -----------------------------------------------------

    if request.method == "GET":

        return render_template(
            "analytics_key.html"
        )

    # -----------------------------------------------------
    # GET ENTERED KEY
    # -----------------------------------------------------

    key = request.form.get(
        "key",
        ""
    )

    if key != "ADMIN2026":

        return "Invalid Privacy Analytics Key."

    connection = get_connection()

    # -----------------------------------------------------
    # COLLECT RAW CATEGORY ANALYTICS
    # -----------------------------------------------------

    rows = connection.execute(
        """
        SELECT
            products.category,

            SUM(
                CASE
                    WHEN interactions.interaction_type = 'view'
                    THEN 1
                    ELSE 0
                END
            ) AS views,

            SUM(
                CASE
                    WHEN interactions.interaction_type = 'add_to_cart'
                    THEN 1
                    ELSE 0
                END
            ) AS add_to_cart,

            SUM(
                CASE
                    WHEN interactions.interaction_type = 'purchase'
                    THEN 1
                    ELSE 0
                END
            ) AS purchases

        FROM interactions

        JOIN products
        ON interactions.product_id = products.product_id

        GROUP BY products.category

        ORDER BY products.category
        """
    ).fetchall()

    connection.close()

    analytics = []

    # -----------------------------------------------------
    # APPLY DIFFERENTIAL PRIVACY
    # -----------------------------------------------------

    for row in rows:

        protected_views = add_laplace_noise(
            row["views"],
            sensitivity=1,
            epsilon=2.0
        )

        protected_cart = add_laplace_noise(
            row["add_to_cart"],
            sensitivity=1,
            epsilon=2.0
        )

        protected_purchases = add_laplace_noise(
            row["purchases"],
            sensitivity=1,
            epsilon=2.0
        )

        analytics.append(
            {
                "category": row["category"],

                "views": row["views"],

                "protected_views": round(
                    max(
                        0,
                        protected_views
                    ),
                    2
                ),

                "add_to_cart": row["add_to_cart"],

                "protected_cart": round(
                    max(
                        0,
                        protected_cart
                    ),
                    2
                ),

                "purchases": row["purchases"],

                "protected_purchases": round(
                    max(
                        0,
                        protected_purchases
                    ),
                    2
                )
            }
        )

    return render_template(
        "privacy_analytics.html",
        analytics=analytics
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )