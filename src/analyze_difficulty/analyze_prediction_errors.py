import pandas as pd
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - PREDICTION ERROR ANALYSIS")
print("=" * 70)

DATA_PATH = Path("data/processed/difficulty_predictions.csv")
OUTPUT_PATH = Path(
    "data/processed/prediction_error_analysis.csv"
)

df = pd.read_csv(DATA_PATH)

print(f"\nLoaded {len(df)} predictions.")

# Absolute error groups
df["error_group"] = pd.cut(
    df["absolute_error"],
    bins=[-1, 2, 5, 10, float("inf")],
    labels=[
        "Low error (<=2)",
        "Moderate error (2-5)",
        "High error (5-10)",
        "Very high error (>10)"
    ]
)

print("\nError group distribution:")
print(df["error_group"].value_counts().sort_index())

# Feature columns
feature_columns = [
    "length_score",
    "equation_score",
    "reasoning_score",
    "proof_score",
    "case_score",
    "steps_score",
    "problem_type_score",
    "domain_score"
]

print("\nAverage features by error group:")
group_stats = df.groupby(
    "error_group",
    observed=False
)[feature_columns + ["absolute_error"]].mean()

print(group_stats.to_string())

# Largest errors
largest = df.sort_values(
    "absolute_error",
    ascending=False
).head(20)

print("\nTop 20 prediction errors:")
print(
    largest[
        [
            "actual_difficulty",
            "predicted_difficulty",
            "absolute_error"
        ] + feature_columns
    ].to_string(index=False)
)

# Save
df.to_csv(OUTPUT_PATH, index=False)

print("\nSaved:")
print(OUTPUT_PATH)

print("\nPrediction error analysis complete.")