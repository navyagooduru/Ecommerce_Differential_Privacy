import pandas as pd
from differential_privacy import add_laplace_noise


# Load the shopping dataset
df = pd.read_csv("Ecommerce_Personalized_Recommendation_Dataset.csv")


# Count records for each product
product_counts = df["Product_ID"].value_counts()


# Take the 10 most frequently appearing products
top_products = product_counts.head(10)


# Store privacy-protected results
protected_data = []


# Apply Differential Privacy
for product_id, count in top_products.items():

    protected_count = add_laplace_noise(
        count,
        sensitivity=1,
        epsilon=1.0
    )

    protected_data.append({
        "Product_ID": product_id,
        "Original_Count": count,
        "Protected_Count": round(protected_count, 2)
    })


# Create a DataFrame
protected_df = pd.DataFrame(protected_data)


# Save the privacy-protected product data
protected_df.to_csv(
    "protected_product_data.csv",
    index=False
)


print("\nTop 10 Products:")
print(protected_df)

print("\nSaved as protected_product_data.csv")