import pandas as pd
import matplotlib.pyplot as plt


# Load privacy-protected category data
df = pd.read_csv("protected_category_data.csv")


# Create the bar chart
plt.figure(figsize=(10, 6))

plt.bar(
    df["Category"],
    df["Protected_Count"]
)

plt.title("Popular Shopping Categories (Privacy-Protected Data)")
plt.xlabel("Product Category")
plt.ylabel("Privacy-Protected Shopping Count")

plt.xticks(rotation=30)

plt.tight_layout()


# Save the chart
plt.savefig("category_analysis.png")

plt.show()