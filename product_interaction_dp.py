import pandas as pd
from database import get_connection
from differential_privacy import add_laplace_noise


# Connect to the database
connection = get_connection()

rows = connection.execute("""
    SELECT product_id, interaction_type
    FROM interactions
""").fetchall()

connection.close()


# Convert database records to DataFrame
data = [dict(row) for row in rows]
df = pd.DataFrame(data)


# Check if interaction data exists
if df.empty:
    print("No website interactions found.")
    exit()


# Count interactions for each product
product_interactions = (
    df.groupby(["product_id", "interaction_type"])
      .size()
      .reset_index(name="Original_Count")
)


# Use our selected privacy level
epsilon = 1.0
sensitivity = 1


protected_data = []


# Apply Differential Privacy
for _, row in product_interactions.iterrows():

    protected_count = add_laplace_noise(
    row["Original_Count"],
    sensitivity=sensitivity,
    epsilon=epsilon
)

# Shopping counts cannot be negative
protected_count = max(0, protected_count)

protected_data.append({
        "Product_ID": row["product_id"],
        "Interaction_Type": row["interaction_type"],
        "Original_Count": row["Original_Count"],
        "Protected_Count": round(protected_count, 2)
    })


# Create protected DataFrame
protected_df = pd.DataFrame(protected_data)


# Sort by protected count
protected_df = protected_df.sort_values(
    by="Protected_Count",
    ascending=False
)


# Save the results
protected_df.to_csv(
    "protected_product_interactions.csv",
    index=False
)


print("\nPrivacy-Protected Product Interactions:")
print(protected_df.to_string(index=False))

print("\nSaved as protected_product_interactions.csv")