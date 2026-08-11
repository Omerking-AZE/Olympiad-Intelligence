import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - DIFFICULTY MODEL ANALYSIS")
print("=" * 70)

DATA_PATH = Path("data/processed/difficulty_predictions.csv")

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

print(f"\nLoaded {len(df)} problems.")
print(f"Total columns: {len(df.columns)}")

print("\n" + "=" * 70)
print("1. DATASET OVERVIEW")
print("=" * 70)

print("\nColumns:")
for column in df.columns:
    print(f"- {column}")

print("\nMissing values:")
print(df.isna().sum())

print("\nDifficulty distribution:")

if "difficulty_label" in df.columns:
    print(df["difficulty_label"].value_counts())

elif "difficulty" in df.columns:
    print(df["difficulty"].value_counts())


print("\n" + "=" * 70)
print("2. PREDICTION ANALYSIS")
print("=" * 70)

actual = df["actual_difficulty"]
predicted = df["predicted_difficulty"]

error = predicted - actual
absolute_error = df["absolute_error"]

print(f"\nMean error: {error.mean():.4f}")
print(f"Mean absolute error: {absolute_error.mean():.4f}")
print(f"Maximum absolute error: {absolute_error.max():.4f}")

print("\nLargest prediction errors:")

cols = [
    col for col in [
        "actual_difficulty",
        "predicted_difficulty",
        "absolute_error"
    ]
    if col in df.columns
]

print(
    df.nlargest(10, "absolute_error")[cols].to_string(index=False)
)

prediction_columns = [
    "difficulty_score",
    "predicted_difficulty_score"
]

available_prediction_columns = [
    col for col in prediction_columns if col in df.columns
]

if len(available_prediction_columns) >= 2:

    actual = df["difficulty_score"]
    predicted = df["predicted_difficulty_score"]

    error = predicted - actual

    print(f"\nMean error: {error.mean():.4f}")
    print(f"Mean absolute error: {error.abs().mean():.4f}")
    print(f"Maximum absolute error: {error.abs().max():.4f}")

    df["prediction_error"] = error
    df["absolute_error"] = error.abs()

    print("\nLargest prediction errors:")

    cols = [
        col for col in [
            "problem_id",
            "domain",
            "problem_type",
            "difficulty_score",
            "predicted_difficulty_score",
            "absolute_error"
        ]
        if col in df.columns
    ]

    print(
        df.nlargest(10, "absolute_error")[cols].to_string(index=False)
    )


print("\n" + "=" * 70)
print("3. DIFFICULTY SCORE DISTRIBUTION")
print("=" * 70)

if "difficulty_score" in df.columns:

    print("\nDescriptive statistics:")
    print(df["difficulty_score"].describe())

    print("\nScore intervals:")

    bins = [0, 25, 40, 55, 70, 85, 100]

    labels = [
        "0-25",
        "25-40",
        "40-55",
        "55-70",
        "70-85",
        "85-100"
    ]

    score_groups = pd.cut(
        df["difficulty_score"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    print(score_groups.value_counts().sort_index())


print("\n" + "=" * 70)
print("4. DOMAIN ANALYSIS")
print("=" * 70)

if "domain" in df.columns and "difficulty_score" in df.columns:

    domain_analysis = (
        df.groupby("domain", dropna=False)
        .agg(
            problems=("difficulty_score", "count"),
            mean_difficulty=("difficulty_score", "mean"),
            median_difficulty=("difficulty_score", "median"),
            min_difficulty=("difficulty_score", "min"),
            max_difficulty=("difficulty_score", "max")
        )
        .sort_values("mean_difficulty", ascending=False)
    )

    print(domain_analysis.to_string())


print("\n" + "=" * 70)
print("5. PROBLEM TYPE ANALYSIS")
print("=" * 70)

if "problem_type" in df.columns and "difficulty_score" in df.columns:

    type_analysis = (
        df.groupby("problem_type", dropna=False)
        .agg(
            problems=("difficulty_score", "count"),
            mean_difficulty=("difficulty_score", "mean"),
            median_difficulty=("difficulty_score", "median")
        )
        .sort_values("mean_difficulty", ascending=False)
    )

    print(type_analysis.to_string())


print("\n" + "=" * 70)
print("6. DIFFICULTY LABEL ANALYSIS")
print("=" * 70)

if "difficulty_label" in df.columns:

    label_counts = df["difficulty_label"].value_counts()

    print("\nCounts:")
    print(label_counts)

    print("\nPercentages:")
    print(
        (label_counts / len(df) * 100)
        .round(2)
        .astype(str)
        .add("%")
    )


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)