import pandas as pd
from differential_privacy import add_laplace_noise


# Load the shopping dataset
df = pd.read_csv("Ecommerce_Personalized_Recommendation_Dataset.csv")


# Count records for each category
category_counts = df["Category"].value_counts()


# Different privacy levels
epsilon_values = [0.1, 0.5, 1.0, 2.0]


print("\nOriginal Category Counts:")
print(category_counts)


# Test different epsilon values
for epsilon in epsilon_values:

    print("\n--------------------------------")
    print("Epsilon =", epsilon)
    print("--------------------------------")

    for category, count in category_counts.items():

        protected_count = add_laplace_noise(
            count,
            sensitivity=1,
            epsilon=epsilon
        )

        print(
            category,
            "-> Original:",
            count,
            "| Protected:",
            round(protected_count, 2)
        )