import pandas as pd
from database import get_connection
from differential_privacy import add_laplace_noise


def get_recommendations(
    user_id,
    current_product_id=None,
    limit=5
):

    connection = get_connection()

    # -----------------------------------------
    # 1. Get user's complete shopping behaviour
    # -----------------------------------------

    user_rows = connection.execute("""
        SELECT
            interactions.product_id,
            interactions.interaction_type,
            products.category
        FROM interactions
        JOIN products
        ON interactions.product_id = products.product_id
        WHERE interactions.user_id = ?
    """, (user_id,)).fetchall()

    if not user_rows:
        connection.close()
        return []

    # -----------------------------------------
    # 2. Calculate user's category preference
    # -----------------------------------------

    category_scores = {}

    for row in user_rows:

        category = row["category"]
        interaction = row["interaction_type"]

        if interaction == "purchase":
            score = 3

        elif interaction == "add_to_cart":
            score = 2

        elif interaction == "view":
            score = 1

        else:
            score = 0

        category_scores[category] = (
            category_scores.get(category, 0) + score
        )

    # Strongest category
    preferred_category = max(
        category_scores,
        key=category_scores.get
    )

    print("\n================================")
    print("USER:", user_id)
    print("CATEGORY SCORES:", category_scores)
    print("PREFERRED CATEGORY:", preferred_category)
    print("================================\n")


    # -----------------------------------------
    # 3. Get ONLY products from that category
    # -----------------------------------------

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


    # -----------------------------------------
    # 4. Load Kaggle dataset
    # -----------------------------------------

    df = pd.read_csv(
        "Ecommerce_Personalized_Recommendation_Dataset.csv"
    )


    # -----------------------------------------
    # 5. Count product popularity
    # -----------------------------------------

    product_counts = (
        df["Product_ID"]
        .value_counts()
        .to_dict()
    )


    # -----------------------------------------
    # 6. Create recommendations
    # -----------------------------------------

    recommendations = []

    for product in products:

        original_count = product_counts.get(
            product["product_id"],
            0
        )

        # Differential Privacy
        protected_count = add_laplace_noise(
            original_count,
            sensitivity=1,
            epsilon=1.0
        )

        protected_count = max(
            0,
            protected_count
        )

        recommendations.append({

            "product_id":
                product["product_id"],

            "product_name":
                product["product_name"],

            "category":
                product["category"],

            "price":
                product["price"],

            "image":
                product["image"],

            "recommendation_score":
                round(protected_count, 2)
        })


    # -----------------------------------------
    # 7. Sort by privacy-protected popularity
    # -----------------------------------------

    recommendations.sort(
        key=lambda x: x["recommendation_score"],
        reverse=True
    )


    # -----------------------------------------
    # 8. Return top products
    # -----------------------------------------

    return recommendations[:limit]