import pandas as pd
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - DIFFICULT TO PREDICT CASES")
print("=" * 70)

INPUT = Path("data/processed/prediction_error_analysis.csv")
OUTPUT = Path("data/processed/hard_prediction_cases.csv")

df = pd.read_csv(INPUT)

hard_cases = df.sort_values(
    "absolute_error",
    ascending=False
).head(50)

hard_cases.to_csv(OUTPUT, index=False)

print(f"\nSelected {len(hard_cases)} highest-error problems.")

print("\nTop 10 difficult-to-predict cases:")
print(
    hard_cases[
        [
            "actual_difficulty",
            "predicted_difficulty",
            "absolute_error",
            "length_score",
            "equation_score",
            "reasoning_score",
            "proof_score",
            "case_score",
            "steps_score",
        ]
    ].head(10).to_string(index=False)
)

print(f"\nSaved:")
print(OUTPUT)