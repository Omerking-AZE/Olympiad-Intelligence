import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - PREDICTION VISUALIZATION")
print("=" * 70)

INPUT = Path("data/processed/difficulty_predictions.csv")
OUTPUT_DIR = Path("data/processed/plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)

print(f"\nLoaded {len(df)} predictions.")

# Actual vs Predicted
plt.figure(figsize=(10, 7))

plt.scatter(
    df["actual_difficulty"],
    df["predicted_difficulty"],
    alpha=0.6
)

min_value = min(
    df["actual_difficulty"].min(),
    df["predicted_difficulty"].min()
)

max_value = max(
    df["actual_difficulty"].max(),
    df["predicted_difficulty"].max()
)

plt.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--"
)

plt.xlabel("Actual Difficulty")
plt.ylabel("Predicted Difficulty")
plt.title("Actual vs Predicted Difficulty")

plt.tight_layout()

output_path = OUTPUT_DIR / "actual_vs_predicted.png"
plt.savefig(output_path, dpi=300)
plt.close()

print(f"\nSaved:")
print(output_path)

print("\nVisualization complete.")