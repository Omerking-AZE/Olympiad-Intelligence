import pandas as pd
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - MODEL ERROR SUMMARY")
print("=" * 70)

INPUT = Path("data/processed/prediction_error_analysis.csv")
OUTPUT = Path("data/processed/model_error_summary.csv")

df = pd.read_csv(INPUT)

summary = {
    "prediction_samples": len(df),
    "mean_error": df["predicted_difficulty"].sub(
        df["actual_difficulty"]
    ).mean(),
    "mae": df["absolute_error"].mean(),
    "max_error": df["absolute_error"].max(),
    "low_error_count": (df["absolute_error"] <= 2).sum(),
    "moderate_error_count": (
        (df["absolute_error"] > 2) &
        (df["absolute_error"] <= 5)
    ).sum(),
    "high_error_count": (
        (df["absolute_error"] > 5) &
        (df["absolute_error"] <= 10)
    ).sum(),
    "very_high_error_count": (
        df["absolute_error"] > 10
    ).sum(),
}

result = pd.DataFrame([summary])

result.to_csv(OUTPUT, index=False)

print("\nModel error summary:")
print(result.to_string(index=False))

print(f"\nSaved:")
print(OUTPUT)