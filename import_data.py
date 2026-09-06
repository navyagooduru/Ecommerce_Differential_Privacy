import pandas as pd
import sqlite3

DATABASE = "shop.db"
CSV_FILE = "Ecommerce_Personalized_Recommendation_Dataset.csv"


def import_products():
    # Read Kaggle dataset
    df = pd.read_csv(CSV_FILE)

    # Connect to SQLite database
    connection = sqlite3.connect(DATABASE)

    # Select the product information we need
    products = df[
        [
            "Product_ID",
            "Category",
            "Brand",
            "Product_Price"
        ]
    ].copy()

    # Remove duplicate products
    products = products.drop_duplicates(subset=["Product_ID"])

    # Rename columns to match our database
    products.columns = [
        "product_id",
        "category",
        "brand",
        "price"
    ]

    # Add products to database
    products.to_sql(
        "products",
        connection,
        if_exists="append",
        index=False
    )

    connection.close()

    print("Products imported successfully!")
    print("Number of products:", len(products))


if __name__ == "__main__":
    import_products()