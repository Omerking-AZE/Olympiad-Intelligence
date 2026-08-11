import pandas as pd
import matplotlib.pyplot as plt


print("=" * 70)
print("OLYMPIAD INTELLIGENCE - PREDICTION ANALYSIS")
print("=" * 70)

df = pd.read_csv(
    "data/processed/difficulty_predictions.csv"
)

actual = df["actual_difficulty"]
predicted = df["predicted_difficulty"]

plt.figure(figsize=(8, 8))

plt.scatter(
    actual,
    predicted,
    alpha=0.6
)

minimum = min(actual.min(), predicted.min())
maximum = max(actual.max(), predicted.max())

plt.plot(
    [minimum, maximum],
    [minimum, maximum],
    linestyle="--"
)

plt.xlabel("Actual Difficulty Score")
plt.ylabel("Predicted Difficulty Score")
plt.title("Actual vs Predicted Difficulty")

plt.tight_layout()

output = "data/processed/actual_vs_predicted.png"

plt.savefig(
    output,
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {output}")