import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - ERROR DISTRIBUTION")
print("=" * 70)

INPUT = Path("data/processed/difficulty_predictions.csv")
OUTPUT_DIR = Path("data/processed/plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)

print(f"\nLoaded {len(df)} predictions.")

errors = df["actual_difficulty"] - df["predicted_difficulty"]

print("\nError statistics:")
print(f"Mean error: {errors.mean():.4f}")
print(f"Mean absolute error: {errors.abs().mean():.4f}")
print(f"Maximum absolute error: {errors.abs().max():.4f}")

plt.figure(figsize=(10, 7))

plt.hist(errors, bins=30)

plt.axvline(
    0,
    linestyle="--",
    linewidth=2
)

plt.xlabel("Prediction Error (Actual - Predicted)")
plt.ylabel("Number of Problems")
plt.title("Difficulty Prediction Error Distribution")

plt.tight_layout()

output_path = OUTPUT_DIR / "prediction_error_distribution.png"
plt.savefig(output_path, dpi=300)
plt.close()

print(f"\nSaved:")
print(output_path)

print("\nError distribution analysis complete.")