import os
import sqlite3
from PIL import Image, ImageDraw

DATABASE = "shop.db"
IMAGE_FOLDER = os.path.join("static", "images", "products")

os.makedirs(IMAGE_FOLDER, exist_ok=True)


def draw_product(product_name, category, product_id):

    img = Image.new("RGB", (600, 600), "white")
    draw = ImageDraw.Draw(img)

    name = product_name.lower()
    category = category.lower()

    # Default product box
    x1, y1 = 150, 150
    x2, y2 = 450, 450

    # ELECTRONICS
    if "electronics" in category:

        if "headphone" in name or "earbud" in name:
            draw.ellipse((170, 150, 430, 410), outline="black", width=25)
            draw.rectangle((190, 270, 250, 390), fill="black")
            draw.rectangle((350, 270, 410, 390), fill="black")

        elif "laptop" in name:
            draw.rectangle((150, 150, 450, 360), outline="black", width=15)
            draw.rectangle((120, 370, 480, 410), fill="black")

        elif "watch" in name:
            draw.rectangle((240, 100, 360, 500), fill="black")
            draw.rounded_rectangle(
                (200, 190, 400, 410),
                radius=35,
                outline="black",
                width=15
            )

        else:
            draw.rounded_rectangle(
                (150, 170, 450, 430),
                radius=30,
                outline="black",
                width=15
            )

    # CLOTHING
    elif "clothing" in category:

        if "jacket" in name:
            draw.polygon(
                [(250, 150), (180, 230), (120, 430),
                 (240, 430), (300, 280), (360, 430),
                 (480, 430), (420, 230), (350, 150)],
                outline="black"
            )

        elif "dress" in name:
            draw.polygon(
                [(250, 140), (350, 140), (390, 280),
                 (470, 450), (130, 450), (210, 280)],
                outline="black"
            )

        elif "pant" in name or "jean" in name:
            draw.polygon(
                [(180, 140), (420, 140), (370, 300),
                 (450, 480), (320, 480), (300, 320),
                 (280, 480), (150, 480), (230, 300)],
                outline="black"
            )

        else:
            draw.rectangle(
                (190, 150, 410, 450),
                outline="black",
                width=15
            )

    # SPORTS
    elif "sports" in category:

        if "bat" in name:
            draw.rounded_rectangle(
                (250, 100, 350, 450),
                radius=30,
                outline="black",
                width=15
            )
            draw.rectangle((275, 430, 325, 520), fill="black")

        elif "shoe" in name:
            draw.polygon(
                [(130, 350), (260, 300), (350, 380),
                 (480, 410), (450, 470),
                 (150, 470)],
                outline="black"
            )

        elif "mat" in name:
            draw.rounded_rectangle(
                (150, 130, 450, 470),
                radius=30,
                outline="black",
                width=15
            )

        elif "racket" in name:
            draw.ellipse(
                (170, 100, 430, 360),
                outline="black",
                width=15
            )
            draw.line(
                (300, 350, 300, 500),
                fill="black",
                width=25
            )

        elif "bag" in name:
            draw.rounded_rectangle(
                (160, 180, 440, 450),
                radius=40,
                outline="black",
                width=15
            )
            draw.arc(
                (220, 100, 380, 250),
                180,
                360,
                fill="black",
                width=15
            )

        else:
            draw.ellipse(
                (150, 150, 450, 450),
                outline="black",
                width=15
            )

    # BEAUTY
    elif "beauty" in category:

        if "skin" in name or "cream" in name:
            draw.rounded_rectangle(
                (210, 200, 390, 430),
                radius=30,
                outline="black",
                width=15
            )
            draw.rectangle((230, 150, 370, 210), outline="black", width=12)

        elif "makeup" in name:
            draw.ellipse(
                (150, 170, 450, 470),
                outline="black",
                width=15
            )

        else:
            draw.rounded_rectangle(
                (220, 120, 380, 470),
                radius=30,
                outline="black",
                width=15
            )

    # BOOKS
    elif "book" in category:

        draw.rectangle(
            (170, 120, 430, 470),
            outline="black",
            width=15
        )
        draw.line(
            (300, 130, 300, 460),
            fill="black",
            width=8
        )

    # TOYS
    elif "toy" in category:

        draw.ellipse(
            (160, 170, 440, 450),
            outline="black",
            width=15
        )
        draw.ellipse((220, 260, 250, 290), fill="black")
        draw.ellipse((350, 260, 380, 290), fill="black")

    # HOME
    elif "home" in category:

        draw.polygon(
            [(120, 280), (300, 120), (480, 280),
             (430, 280), (430, 470), (170, 470),
             (170, 280)],
            outline="black"
        )

    # OTHER
    else:

        draw.rounded_rectangle(
            (150, 150, 450, 450),
            radius=40,
            outline="black",
            width=15
        )

    # Small product ID at bottom
    draw.text(
        (20, 560),
        product_id,
        fill="gray"
    )

    return img


connection = sqlite3.connect(DATABASE)
connection.row_factory = sqlite3.Row

products = connection.execute("""
    SELECT product_id, product_name, category
    FROM products
    ORDER BY product_id
""").fetchall()

print()
print("Creating product images...")
print("--------------------------------")

for product in products:

    product_id = product["product_id"]
    product_name = product["product_name"]
    category = product["category"]

    image = draw_product(
        product_name,
        category,
        product_id
    )

    filename = f"{product_id}.jpg"
    filepath = os.path.join(
        IMAGE_FOLDER,
        filename
    )

    image.save(filepath, "JPEG", quality=95)

    connection.execute("""
        UPDATE products
        SET image = ?
        WHERE product_id = ?
    """, (
        filename,
        product_id
    ))

    print(
        f"Created {product_id} - {product_name}"
    )

connection.commit()
connection.close()

print()
print("================================")
print("ALL PRODUCT IMAGES CREATED")
print("================================")
print(f"Total images: {len(products)}")