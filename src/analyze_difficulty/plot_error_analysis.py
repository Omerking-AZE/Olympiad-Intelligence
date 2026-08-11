import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - ERROR ANALYSIS VISUALIZATION")
print("=" * 70)

INPUT = Path("data/processed/prediction_error_analysis.csv")
OUTPUT_DIR = Path("data/processed/plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)

print(f"\nLoaded {len(df)} prediction error records.")

# --------------------------------------------------
# 1. Error group distribution
# --------------------------------------------------

group_counts = df["error_group"].value_counts()

plt.figure(figsize=(10, 6))
group_counts.plot(kind="bar")
plt.title("Prediction Error Groups")
plt.xlabel("Error Group")
plt.ylabel("Number of Problems")
plt.xticks(rotation=20)
plt.tight_layout()

path = OUTPUT_DIR / "error_group_distribution.png"
plt.savefig(path, dpi=200)
plt.close()

print(f"Saved: {path}")

# --------------------------------------------------
# 2. Absolute error vs actual difficulty
# --------------------------------------------------

plt.figure(figsize=(10, 6))
plt.scatter(
    df["actual_difficulty"],
    df["absolute_error"],
    alpha=0.7
)

plt.xlabel("Actual Difficulty")
plt.ylabel("Absolute Prediction Error")
plt.title("Prediction Error vs Difficulty")
plt.tight_layout()

path = OUTPUT_DIR / "error_vs_difficulty.png"
plt.savefig(path, dpi=200)
plt.close()

print(f"Saved: {path}")

# --------------------------------------------------
# 3. Feature values vs error
# --------------------------------------------------

features = [
    "length_score",
    "equation_score",
    "reasoning_score",
    "proof_score",
    "case_score",
    "steps_score",
    "problem_type_score",
    "domain_score",
]

for feature in features:
    plt.figure(figsize=(9, 6))

    plt.scatter(
        df[feature],
        df["absolute_error"],
        alpha=0.6
    )

    plt.xlabel(feature)
    plt.ylabel("Absolute Prediction Error")
    plt.title(f"{feature} vs Prediction Error")
    plt.tight_layout()

    path = OUTPUT_DIR / f"{feature}_vs_error.png"
    plt.savefig(path, dpi=200)
    plt.close()

print("\nError analysis visualizations complete.")