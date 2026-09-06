from flask import Flask, render_template, request, redirect, url_for, session
from database import get_connection, create_tables

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
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    connection = get_connection()

    products = connection.execute("""
        SELECT
            product_id,
            product_name,
            category,
            price,
            image,
            description
        FROM products
    """).fetchall()

    connection.close()

    return render_template(
        "home.html",
        products=products,
        recommendations=[]
    )

# =========================================================
# PRODUCT DETAILS
# =========================================================

@app.route("/product/<product_id>")
def product_details(product_id):

    connection = get_connection()

    product = connection.execute("""
        SELECT
            product_id,
            product_name,
            category,
            price,
            image,
            description
        FROM products
        WHERE product_id = ?
    """, (product_id,)).fetchone()

    connection.close()

    if not product:
        return "Product not found."

    # Record that the logged-in user viewed this product
    if "user_id" in session:

        connection = get_connection()

        connection.execute("""
            INSERT INTO interactions
            (user_id, product_id, interaction_type)
            VALUES (?, ?, ?)
        """, (
            session["user_id"],
            product_id,
            "view"
        ))

        connection.commit()
        connection.close()

        # Get recommendations specifically for this user
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

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        connection = get_connection()

        existing_user = connection.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        if existing_user:
            connection.close()
            return "Email already registered."

        connection.execute("""
            INSERT INTO users
            (
                user_id,
                name,
                email,
                password
            )
            VALUES (?, ?, ?, ?)
        """, (
            email,
            name,
            email,
            password
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        connection = get_connection()

        user = connection.execute("""
            SELECT
                user_id,
                name,
                email,
                password
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        connection.close()

        if user and user["password"] == password:

            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]

            return redirect(url_for("home"))

        return "Invalid email or password."

    return render_template("login.html")


# =========================================================
# ADD TO CART
# =========================================================

@app.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    connection = get_connection()

    # Check product
    product = connection.execute("""
        SELECT product_id
        FROM products
        WHERE product_id = ?
    """, (product_id,)).fetchone()

    if not product:
        connection.close()
        return "Product not found."

    # Check whether product is already in cart
    existing_item = connection.execute("""
        SELECT quantity
        FROM cart
        WHERE user_id = ?
        AND product_id = ?
    """, (
        user_id,
        product_id
    )).fetchone()

    if existing_item:

        connection.execute("""
            UPDATE cart
            SET quantity = quantity + 1
            WHERE user_id = ?
            AND product_id = ?
        """, (
            user_id,
            product_id
        ))

    else:

        connection.execute("""
            INSERT INTO cart
            (
                user_id,
                product_id,
                quantity
            )
            VALUES (?, ?, 1)
        """, (
            user_id,
            product_id
        ))

    # Record shopping interaction
    connection.execute("""
        INSERT INTO interactions
        (
            user_id,
            product_id,
            interaction_type
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        product_id,
        "add_to_cart"
    ))

    connection.commit()
    connection.close()

    return redirect(url_for("cart"))


# =========================================================
# INCREASE QUANTITY
# =========================================================

@app.route("/increase/<product_id>", methods=["POST"])
def increase_quantity(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    connection.execute("""
        UPDATE cart
        SET quantity = quantity + 1
        WHERE user_id = ?
        AND product_id = ?
    """, (
        session["user_id"],
        product_id
    ))

    connection.commit()
    connection.close()

    return redirect(url_for("cart"))


# =========================================================
# DECREASE QUANTITY
# =========================================================

@app.route("/decrease/<product_id>", methods=["POST"])
def decrease_quantity(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    item = connection.execute("""
        SELECT quantity
        FROM cart
        WHERE user_id = ?
        AND product_id = ?
    """, (
        session["user_id"],
        product_id
    )).fetchone()

    if item:

        if item["quantity"] > 1:

            connection.execute("""
                UPDATE cart
                SET quantity = quantity - 1
                WHERE user_id = ?
                AND product_id = ?
            """, (
                session["user_id"],
                product_id
            ))

        else:

            connection.execute("""
                DELETE FROM cart
                WHERE user_id = ?
                AND product_id = ?
            """, (
                session["user_id"],
                product_id
            ))

    connection.commit()
    connection.close()

    return redirect(url_for("cart"))


# =========================================================
# CART PAGE
# =========================================================

@app.route("/cart")
def cart():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    items = connection.execute("""
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
    """, (
        session["user_id"],
    )).fetchall()

    total = 0

    for item in items:
        total += item["price"] * item["quantity"]

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
        return redirect(url_for("login"))

    connection = get_connection()

    cart_count = connection.execute("""
        SELECT COUNT(*)
        FROM cart
        WHERE user_id = ?
    """, (
        session["user_id"],
    )).fetchone()[0]

    connection.close()

    if cart_count == 0:
        return redirect(url_for("cart"))

    return render_template("checkout.html")


# =========================================================
# PLACE ORDER
# =========================================================

@app.route("/place_order", methods=["POST"])
def place_order():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    address = request.form.get("address", "").strip()
    city = request.form.get("city", "").strip()
    pincode = request.form.get("pincode", "").strip()
    payment_method = request.form.get("payment_method", "").strip()

    if not address:
        return "Please enter your delivery address."

    if not city:
        return "Please enter your city."

    if not pincode:
        return "Please enter your PIN code."

    if not payment_method:
        return "Please select a payment method."

    connection = get_connection()

    cart_items = connection.execute("""
        SELECT product_id, quantity
        FROM cart
        WHERE user_id = ?
    """, (user_id,)).fetchall()

    if not cart_items:
        connection.close()
        return redirect(url_for("cart"))

    total_price = 0

    for item in cart_items:
        product = connection.execute("""
            SELECT price
            FROM products
            WHERE product_id = ?
        """, (item["product_id"],)).fetchone()

        if product:
            total_price += product["price"] * item["quantity"]

    cursor = connection.execute("""
        INSERT INTO orders
        (user_id, total_price, address, city, pincode, payment_method)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        total_price,
        address,
        city,
        pincode,
        payment_method
    ))

    order_id = cursor.lastrowid

    # Save products included in the order
    for item in cart_items:

        product = connection.execute("""
            SELECT price
            FROM products
            WHERE product_id = ?
        """, (item["product_id"],)).fetchone()

        if product:

            connection.execute("""
                INSERT INTO order_items
                (order_id, product_id, price)
                VALUES (?, ?, ?)
            """, (
                order_id,
                item["product_id"],
                product["price"]
            ))

    # Record purchased products as shopping behaviour
    for item in cart_items:

        connection.execute("""
            INSERT INTO interactions
            (user_id, product_id, interaction_type)
            VALUES (?, ?, ?)
        """, (
            user_id,
            item["product_id"],
            "purchase"
        ))

    # Clear the cart after successful purchase
    connection.execute("""
        DELETE FROM cart
        WHERE user_id = ?
    """, (user_id,))

    connection.commit()
    connection.close()

    return render_template(
        "order_success.html",
        order_id=order_id
    )
    # =====================================================
    # CALCULATE TOTAL
    # =====================================================

    total_price = 0

    for item in cart_items:

        product = connection.execute("""
            SELECT price
            FROM products
            WHERE product_id = ?
        """, (
            item["product_id"],
        )).fetchone()

        if product:
            total_price += product["price"] * item["quantity"]


    # =====================================================
    # CREATE ORDER
    # =====================================================

    cursor = connection.execute("""
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
    """, (
        user_id,
        total_price,
        address,
        city,
        pincode,
        payment_method
    ))

    order_id = cursor.lastrowid


    # =====================================================
    # ADD ORDER ITEMS
    # =====================================================

    for item in cart_items:

        product = connection.execute("""
            SELECT price
            FROM products
            WHERE product_id = ?
        """, (
            item["product_id"],
        )).fetchone()

        if product:

            connection.execute("""
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    price
                )
                VALUES (?, ?, ?)
            """, (
                order_id,
                item["product_id"],
                product["price"]
            ))


    # =====================================================
    # CLEAR CART
    # =====================================================

    connection.execute("""
        DELETE FROM cart
        WHERE user_id = ?
    """, (
        user_id,
    ))

    connection.commit()
    connection.close()


    # =====================================================
    # ORDER SUCCESS
    # =====================================================

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
        return redirect(url_for("login"))

    connection = get_connection()

    orders_data = connection.execute("""
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
    """, (
        session["user_id"],
    )).fetchall()

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

    return redirect(url_for("home"))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)