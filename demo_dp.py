import sqlite3
from differential_privacy import add_laplace_noise


# Connect to database
connection = sqlite3.connect("shop.db")

# Get category-wise original interaction counts
rows = connection.execute("""
    SELECT
        products.category,
        COUNT(*) AS original_count
    FROM interactions
    JOIN products
    ON interactions.product_id = products.product_id
    GROUP BY products.category
    ORDER BY original_count DESC
""").fetchall()

connection.close()


print("\n==============================================")
print(" DIFFERENTIAL PRIVACY DEMONSTRATION")
print("==============================================")

print("\nCategory              Original    Protected")
print("----------------------------------------------")


for category, original_count in rows:

    protected_count = add_laplace_noise(
        original_count,
        sensitivity=1,
        epsilon=2.0
    )

    protected_count = max(0, protected_count)

    print(
        f"{category:<20} "
        f"{original_count:<11} "
        f"{protected_count:.2f}"
    )


print("----------------------------------------------")
print("Sensitivity = 1")
print("Epsilon     = 2.0")
print("Mechanism   = Laplace")
print("==============================================")