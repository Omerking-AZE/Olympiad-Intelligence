import pandas as pd


print("=" * 70)
print("OLYMPIAD INTELLIGENCE - MODEL ERROR ANALYSIS")
print("=" * 70)

predictions = pd.read_csv(
    "data/processed/difficulty_predictions.csv"
)

difficulty = pd.read_csv(
    "data/processed/mathnet_difficulty.csv"
)

# Keep useful metadata
metadata_columns = [
    "problem_id",
    "domain",
    "problem_type",
    "difficulty_label"
]

available = [
    column
    for column in metadata_columns
    if column in difficulty.columns
]

metadata = difficulty[available]

# Match by index
results = predictions.copy()

for column in available:
    results[column] = metadata.loc[
        results.index,
        column
    ].values

results["error"] = (
    results["predicted_difficulty"]
    - results["actual_difficulty"]
)

results["absolute_error"] = (
    results["error"].abs()
)

print("\nAverage absolute error:")
print(
    f"{results['absolute_error'].mean():.3f}"
)

print("\nLargest prediction errors:")

largest = results.sort_values(
    "absolute_error",
    ascending=False
).head(20)

columns_to_show = [
    column
    for column in [
        "problem_id",
        "domain",
        "problem_type",
        "difficulty_label",
        "actual_difficulty",
        "predicted_difficulty",
        "absolute_error"
    ]
    if column in largest.columns
]

print(
    largest[columns_to_show].to_string(
        index=False
    )
)

output = (
    "data/processed/"
    "difficulty_error_analysis.csv"
)

results.to_csv(
    output,
    index=False
)

print(f"\nSaved: {output}")

print("\n" + "=" * 70)
print("ERROR ANALYSIS COMPLETE")
print("=" * 70)