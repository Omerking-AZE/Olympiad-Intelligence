import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path("data/processed/difficulty_predictions.csv")
OUTPUT_DIR = Path("data/processed/plots")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - DIFFICULTY VISUALIZATION")
print("=" * 70)

# 1. Actual difficulty distribution

plt.figure(figsize=(10, 6))

plt.hist(df["actual_difficulty"], bins=25)

plt.xlabel("Actual Difficulty Score")
plt.ylabel("Number of Problems")
plt.title("Distribution of Actual Difficulty Scores")

plt.tight_layout()

path = OUTPUT_DIR / "actual_difficulty_distribution.png"
plt.savefig(path, dpi=150)
plt.close()

print(f"Saved: {path}")


# 2. Actual vs predicted

plt.figure(figsize=(8, 8))

plt.scatter(
    df["actual_difficulty"],
    df["predicted_difficulty"],
    alpha=0.6
)

minimum = min(
    df["actual_difficulty"].min(),
    df["predicted_difficulty"].min()
)

maximum = max(
    df["actual_difficulty"].max(),
    df["predicted_difficulty"].max()
)

plt.plot(
    [minimum, maximum],
    [minimum, maximum],
    linestyle="--"
)

plt.xlabel("Actual Difficulty")
plt.ylabel("Predicted Difficulty")
plt.title("Actual vs Predicted Difficulty")

plt.tight_layout()

path = OUTPUT_DIR / "actual_vs_predicted.png"
plt.savefig(path, dpi=150)
plt.close()

print(f"Saved: {path}")


# 3. Prediction error distribution

plt.figure(figsize=(10, 6))

plt.hist(df["absolute_error"], bins=25)

plt.xlabel("Absolute Prediction Error")
plt.ylabel("Number of Problems")
plt.title("Prediction Error Distribution")

plt.tight_layout()

path = OUTPUT_DIR / "prediction_error_distribution.png"
plt.savefig(path, dpi=150)
plt.close()

print(f"Saved: {path}")


# 4. Feature distributions

features = [
    "length_score",
    "equation_score",
    "reasoning_score",
    "proof_score",
    "case_score",
    "steps_score",
    "problem_type_score",
    "domain_score"
]

for feature in features:

    if feature not in df.columns:
        continue

    plt.figure(figsize=(9, 6))

    plt.hist(df[feature], bins=20)

    plt.xlabel(feature)
    plt.ylabel("Number of Problems")
    plt.title(f"Distribution of {feature}")

    plt.tight_layout()

    path = OUTPUT_DIR / f"{feature}_distribution.png"
    plt.savefig(path, dpi=150)
    plt.close()

    print(f"Saved: {path}")


print("\n" + "=" * 70)
print("VISUALIZATION COMPLETE")
print("=" * 70)