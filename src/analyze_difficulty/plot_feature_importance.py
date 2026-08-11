import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - FEATURE IMPORTANCE VISUALIZATION")
print("=" * 70)

# Paths
DATA_PATH = Path("data/processed/difficulty_predictions.csv")
OUTPUT_DIR = Path("data/processed/plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Feature importance from the trained model
importance_data = {
    "feature": [
        "length_score",
        "proof_score",
        "equation_score",
        "reasoning_score",
        "case_score",
        "steps_score",
        "domain_score",
        "problem_type_score"
    ],
    "importance": [
        0.714917,
        0.117450,
        0.092998,
        0.054117,
        0.011677,
        0.005800,
        0.001526,
        0.001515
    ]
}

df = pd.DataFrame(importance_data)

# Sort by importance
df = df.sort_values("importance", ascending=True)

print("\nFeature importance:")
print(df.to_string(index=False))

# Plot
plt.figure(figsize=(10, 6))

plt.barh(
    df["feature"],
    df["importance"]
)

plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Difficulty Prediction - Feature Importance")

plt.tight_layout()

output_path = OUTPUT_DIR / "feature_importance.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.close()

print("\nSaved:")
print(output_path)

print("\nFeature importance visualization complete.")