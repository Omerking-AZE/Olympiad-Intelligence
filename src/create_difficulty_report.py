import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/difficulty_predictions.csv")
OUTPUT_PATH = Path("data/processed/difficulty_analysis_report.txt")

df = pd.read_csv(DATA_PATH)

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - DIFFICULTY ANALYSIS REPORT")
print("=" * 70)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:

    f.write("=" * 70 + "\n")
    f.write("OLYMPIAD INTELLIGENCE - DIFFICULTY ANALYSIS REPORT\n")
    f.write("=" * 70 + "\n\n")

    f.write(f"Problems analyzed: {len(df)}\n")
    f.write(f"Features: {len(df.columns)}\n\n")

    # Prediction statistics
    actual = df["actual_difficulty"]
    predicted = df["predicted_difficulty"]
    error = predicted - actual
    absolute_error = df["absolute_error"]

    f.write("PREDICTION PERFORMANCE\n")
    f.write("-" * 50 + "\n")
    f.write(f"Mean error: {error.mean():.4f}\n")
    f.write(f"Mean absolute error: {absolute_error.mean():.4f}\n")
    f.write(f"Maximum absolute error: {absolute_error.max():.4f}\n")
    f.write(f"Median absolute error: {absolute_error.median():.4f}\n")
    f.write(f"Std absolute error: {absolute_error.std():.4f}\n\n")

    # Actual score statistics
    f.write("ACTUAL DIFFICULTY STATISTICS\n")
    f.write("-" * 50 + "\n")
    f.write(actual.describe().to_string())
    f.write("\n\n")

    # Predicted score statistics
    f.write("PREDICTED DIFFICULTY STATISTICS\n")
    f.write("-" * 50 + "\n")
    f.write(predicted.describe().to_string())
    f.write("\n\n")

    # Largest errors
    f.write("LARGEST PREDICTION ERRORS\n")
    f.write("-" * 50 + "\n")

    largest_errors = df.nlargest(10, "absolute_error")[
        [
            "actual_difficulty",
            "predicted_difficulty",
            "absolute_error"
        ]
    ]

    f.write(largest_errors.to_string(index=False))
    f.write("\n\n")

    # Feature statistics
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

    available_features = [
        feature for feature in features
        if feature in df.columns
    ]

    f.write("FEATURE STATISTICS\n")
    f.write("-" * 50 + "\n")
    f.write(
        df[available_features]
        .describe()
        .to_string()
    )
    f.write("\n")

print("\nReport saved to:")
print(OUTPUT_PATH)