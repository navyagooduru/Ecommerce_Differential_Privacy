import sqlite3
import random


DATABASE = "shop.db"


# Product names based on category
PRODUCT_NAMES = {
    "Electronics": [
        "Smartphone",
        "Wireless Earbuds",
        "Bluetooth Speaker",
        "Smart Watch",
        "Laptop",
        "Wireless Headphones",
        "Power Bank",
        "USB Charger"
    ],

    "Clothing": [
        "Casual T-Shirt",
        "Denim Jeans",
        "Cotton Shirt",
        "Hoodie",
        "Casual Jacket",
        "Summer Dress",
        "Track Pants",
        "Formal Shirt"
    ],

    "Sports": [
        "Running Shoes",
        "Sports Shoes",
        "Football",
        "Cricket Bat",
        "Tennis Racket",
        "Gym Bag",
        "Yoga Mat",
        "Sports T-Shirt"
    ],

    "Books": [
        "Programming Basics",
        "Data Science Handbook",
        "Python Programming",
        "Machine Learning Guide",
        "Web Development Guide",
        "Computer Science Fundamentals",
        "Artificial Intelligence Basics",
        "Database Management"
    ],

    "Home": [
        "Table Lamp",
        "Wall Clock",
        "Storage Box",
        "Kitchen Organizer",
        "Bedside Lamp",
        "Cushion Set",
        "Decorative Vase",
        "Home Organizer"
    ],

    "Beauty": [
        "Face Care Kit",
        "Skin Care Set",
        "Hair Care Kit",
        "Beauty Essentials",
        "Daily Care Kit",
        "Moisturizing Cream",
        "Personal Care Set",
        "Beauty Gift Set"
    ]
}


def get_product_name(category):
    """Return a suitable product name for the category."""

    if category in PRODUCT_NAMES:
        return random.choice(PRODUCT_NAMES[category])

    return "Premium " + str(category) + " Product"
def get_description(product_name, category):

    descriptions = {

        "Electronics":
            f"{product_name} is a reliable and modern electronic product designed for everyday use. It offers useful features, convenient operation, and a practical design.",

        "Clothing":
            f"{product_name} is a comfortable and stylish choice for everyday wear. It is designed to provide a good combination of comfort, quality, and modern style.",

        "Sports":
            f"{product_name} is designed for sports and fitness activities. It offers a practical design and comfortable use for beginners as well as regular users.",

        "Books":
            f"{product_name} is a useful learning resource covering important concepts and practical knowledge. It is suitable for students, learners, and anyone interested in the subject.",

        "Home":
            f"{product_name} is a practical home product designed to make everyday activities easier and more convenient. It combines useful functionality with a simple design.",

        "Beauty":
            f"{product_name} is designed for everyday personal care and beauty needs. It is a convenient choice for maintaining a simple and comfortable daily care routine.",

        "Toys":
            f"{product_name} is designed for fun and entertainment. It provides an enjoyable experience and is suitable for recreational activities."
    }

    return descriptions.get(
        category,
        f"{product_name} is a quality product selected for your everyday shopping needs."
    )


def update_products():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, category
        FROM products
    """)

    products = cursor.fetchall()

    for product_id, category in products:

        product_name = get_product_name(category)
        description = get_description(product_name, category)
        image_name = product_name.lower().replace(" ", "_") + ".jpg"
        cursor.execute("""
            UPDATE products
            SET product_name = ?,
                image = ?,
                description = ?
            WHERE id = ?
        """, (
            product_name,
            image_name,
            description,
            product_id
        ))

    connection.commit()
    connection.close()

    print("Product names and image references added successfully!")
    print("Products updated:", len(products))


if __name__ == "__main__":
    update_products()