import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/difficulty_predictions.csv")
OUTPUT_PATH = Path("data/processed/difficulty_correlations.csv")

df = pd.read_csv(DATA_PATH)

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

correlations = []

for feature in available_features:

    correlation = df[feature].corr(
        df["actual_difficulty"]
    )

    correlations.append({
        "feature": feature,
        "correlation_with_difficulty": correlation
    })

result = pd.DataFrame(correlations)

result["absolute_correlation"] = (
    result["correlation_with_difficulty"]
    .abs()
)

result = result.sort_values(
    "absolute_correlation",
    ascending=False
)

result.to_csv(
    OUTPUT_PATH,
    index=False
)

print("=" * 70)
print("DIFFICULTY CORRELATION ANALYSIS")
print("=" * 70)

print("\nCorrelation with actual difficulty:")
print(
    result[
        [
            "feature",
            "correlation_with_difficulty"
        ]
    ].to_string(index=False)
)

print("\nSaved:")
print(OUTPUT_PATH)