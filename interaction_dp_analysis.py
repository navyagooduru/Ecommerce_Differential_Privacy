import pandas as pd
from database import get_connection
from differential_privacy import add_laplace_noise


# Connect to the database
connection = get_connection()

# Read website shopping interactions
rows = connection.execute("""
    SELECT user_id, product_id, interaction_type
    FROM interactions
""").fetchall()

connection.close()


# Convert database records into a DataFrame
data = [dict(row) for row in rows]
df = pd.DataFrame(data)


# Check if there is any interaction data
if df.empty:
    print("No website interactions found.")
    exit()


# Count each type of shopping interaction
interaction_counts = df["interaction_type"].value_counts()


print("\nOriginal Website Interaction Counts:")
print(interaction_counts)


# Apply Differential Privacy
epsilon = 1.0
sensitivity = 1

protected_data = []


for interaction_type, count in interaction_counts.items():

    protected_count = add_laplace_noise(
        count,
        sensitivity=sensitivity,
        epsilon=epsilon
    )

    protected_data.append({
        "Interaction_Type": interaction_type,
        "Original_Count": count,
        "Protected_Count": round(protected_count, 2)
    })


# Create protected DataFrame
protected_df = pd.DataFrame(protected_data)


print("\nPrivacy-Protected Website Interactions:")
print(protected_df)


# Save the protected results
protected_df.to_csv(
    "protected_interaction_data.csv",
    index=False
)


print("\nSaved as protected_interaction_data.csv")