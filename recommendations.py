import sqlite3


DATABASE = "shop.db"


def get_recommendations(
    user_id,
    current_product_id=None,
    limit=5
):
    """
    Generate personalized product recommendations
    based on the user's recent shopping activity.

    Interaction weights:

    purchase     = 5
    add_to_cart  = 3
    view         = 1

    The most recently preferred category is given
    priority so that recommendations match what the
    user is currently shopping for.
    """

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row


    # =====================================================
    # STEP 1
    # FIND THE USER'S MOST RECENT INTERACTION
    # =====================================================

    latest_interaction = connection.execute(
        """
        SELECT
            interactions.product_id,
            interactions.interaction_type,
            products.category
        FROM interactions

        JOIN products
        ON interactions.product_id = products.product_id

        WHERE interactions.user_id = ?

        ORDER BY interactions.id DESC

        LIMIT 1
        """,
        (user_id,)
    ).fetchone()


    # If the user has no shopping activity,
    # return an empty recommendation list.

    if not latest_interaction:

        connection.close()

        return []


    preferred_category = latest_interaction["category"]


    # =====================================================
    # STEP 2
    # FIND PRODUCTS THE USER HAS ALREADY INTERACTED WITH
    # =====================================================

    interacted_products = connection.execute(
        """
        SELECT DISTINCT product_id
        FROM interactions
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchall()


    interacted_ids = [
        row["product_id"]
        for row in interacted_products
    ]


    # =====================================================
    # STEP 3
    # CREATE PLACEHOLDERS FOR SQL QUERY
    # =====================================================

    if interacted_ids:

        placeholders = ",".join(
            ["?"] * len(interacted_ids)
        )

    else:

        placeholders = "''"


    # =====================================================
    # STEP 4
    # RECOMMEND PRODUCTS FROM THE USER'S
    # CURRENTLY PREFERRED CATEGORY
    # =====================================================

    query_parameters = [
        preferred_category
    ]

    if interacted_ids:

        query_parameters.extend(
            interacted_ids
        )


    recommendations = connection.execute(
        f"""
        SELECT
            products.product_id,
            products.product_name,
            products.category,
            products.price,
            products.image,
            products.description,

            COALESCE(
                SUM(
                    CASE
                        WHEN interactions.interaction_type = 'purchase'
                        THEN 5

                        WHEN interactions.interaction_type = 'add_to_cart'
                        THEN 3

                        WHEN interactions.interaction_type = 'view'
                        THEN 1

                        ELSE 0
                    END
                ),
                0
            ) AS popularity_score

        FROM products

        LEFT JOIN interactions
        ON products.product_id = interactions.product_id

        WHERE products.category = ?

        AND products.product_id NOT IN ({placeholders})

        GROUP BY
            products.product_id,
            products.product_name,
            products.category,
            products.price,
            products.image,
            products.description

        ORDER BY
            popularity_score DESC,
            products.product_name ASC

        LIMIT ?
        """,
        query_parameters + [limit]
    ).fetchall()


    # =====================================================
    # STEP 5
    # IF NOT ENOUGH PRODUCTS ARE FOUND,
    # FILL WITH OTHER PRODUCTS FROM SAME CATEGORY
    # =====================================================

    if len(recommendations) < limit:

        existing_ids = [
            row["product_id"]
            for row in recommendations
        ]


        excluded_ids = interacted_ids + existing_ids


        if current_product_id:
            excluded_ids.append(
                current_product_id
            )


        excluded_ids = list(
            dict.fromkeys(excluded_ids)
        )


        if excluded_ids:

            placeholders = ",".join(
                ["?"] * len(excluded_ids)
            )

            remaining = limit - len(
                recommendations
            )


            extra_products = connection.execute(
                f"""
                SELECT
                    product_id,
                    product_name,
                    category,
                    price,
                    image,
                    description

                FROM products

                WHERE category = ?

                AND product_id NOT IN ({placeholders})

                ORDER BY product_name ASC

                LIMIT ?
                """,
                [preferred_category]
                + excluded_ids
                + [remaining]
            ).fetchall()


        else:

            remaining = limit - len(
                recommendations
            )


            extra_products = connection.execute(
                """
                SELECT
                    product_id,
                    product_name,
                    category,
                    price,
                    image,
                    description

                FROM products

                WHERE category = ?

                ORDER BY product_name ASC

                LIMIT ?
                """,
                (
                    preferred_category,
                    remaining
                )
            ).fetchall()


        recommendations = (
            list(recommendations)
            + list(extra_products)
        )


    connection.close()


    return recommendations[:limit]