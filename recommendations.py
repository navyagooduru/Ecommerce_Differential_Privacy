import pandas as pd
from database import get_connection
from differential_privacy import add_laplace_noise


def get_recommendations(user_id, current_product_id=None, limit=5):

    connection = get_connection()

    # Get user's interactions
    rows = connection.execute("""
        SELECT
            interactions.product_id,
            interactions.interaction_type,
            products.category
        FROM interactions
        JOIN products
        ON interactions.product_id = products.product_id
        WHERE interactions.user_id = ?
    """, (user_id,)).fetchall()

    if not rows:
        connection.close()
        return []

    data = [dict(row) for row in rows]
    df_user = pd.DataFrame(data)

    # ---------------------------------------------------------
    # Count user's views by category
    # ---------------------------------------------------------

    view_data = df_user[
        df_user["interaction_type"] == "view"
    ]

    category_counts = (
        view_data
        .groupby("category")
        .size()
    )

    if category_counts.empty:
        connection.close()
        return []

    # ---------------------------------------------------------
    # Apply Differential Privacy
    # ---------------------------------------------------------

    protected_categories = {}

    for category, count in category_counts.items():

        protected_count = add_laplace_noise(
            count,
            sensitivity=1,
            epsilon=2.0
        )

        protected_categories[category] = max(
            0,
            protected_count
        )

    # ---------------------------------------------------------
    # Select privacy-protected preferred category
    # ---------------------------------------------------------

    preferred_category = max(
        protected_categories,
        key=protected_categories.get
    )

    # ---------------------------------------------------------
    # Get products from preferred category
    # ---------------------------------------------------------

    products = connection.execute("""
        SELECT
            product_id,
            product_name,
            category,
            price,
            image
        FROM products
        WHERE category = ?
        AND product_id != ?
    """, (
        preferred_category,
        current_product_id
    )).fetchall()

    connection.close()

    if not products:
        return []

    # ---------------------------------------------------------
    # Read Kaggle dataset
    # ---------------------------------------------------------

    dataset = pd.read_csv(
        "Ecommerce_Personalized_Recommendation_Dataset.csv"
    )

    product_counts = dataset["Product_ID"].value_counts()

    recommendations = []

    # ---------------------------------------------------------
    # Apply Differential Privacy to product popularity
    # ---------------------------------------------------------

    for product in products:

        original_count = product_counts.get(
            product["product_id"],
            0
        )

        protected_score = add_laplace_noise(
            original_count,
            sensitivity=1,
            epsilon=1.0
        )

        protected_score = max(
            0,
            protected_score
        )

        recommendations.append({
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "category": product["category"],
            "price": product["price"],
            "image": product["image"],
            "recommendation_score": round(
                protected_score,
                2
            )
        })

    # Sort by privacy-protected popularity
    recommendations.sort(
        key=lambda x: x["recommendation_score"],
        reverse=True
    )

    return recommendations[:limit]