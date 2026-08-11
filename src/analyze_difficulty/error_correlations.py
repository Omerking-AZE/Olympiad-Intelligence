import pandas as pd
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - ERROR CORRELATION ANALYSIS")
print("=" * 70)

INPUT = Path("data/processed/prediction_error_analysis.csv")
OUTPUT = Path("data/processed/error_correlations.csv")

df = pd.read_csv(INPUT)

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

correlations = []

for feature in features:
    corr = df[feature].corr(df["absolute_error"])

    correlations.append({
        "feature": feature,
        "error_correlation": corr
    })

result = pd.DataFrame(correlations)

result["absolute_correlation"] = (
    result["error_correlation"].abs()
)

result = result.sort_values(
    "absolute_correlation",
    ascending=False
)

result.to_csv(OUTPUT, index=False)

print("\nFeature/Error correlations:")
print(
    result[
        ["feature", "error_correlation"]
    ].to_string(index=False)
)

print(f"\nSaved:")
print(OUTPUT)