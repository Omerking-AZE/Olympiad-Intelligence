import pandas as pd
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - DAY 7 RESEARCH REPORT")
print("=" * 70)

base = Path("data/processed")

predictions = pd.read_csv(
    base / "difficulty_predictions.csv"
)

errors = pd.read_csv(
    base / "prediction_error_analysis.csv"
)

correlations = pd.read_csv(
    base / "error_correlations.csv"
)

report = []

report.append("# Olympiad Intelligence — Day 7 Model Analysis")
report.append("")
report.append("## Dataset")
report.append("")
report.append(
    f"Prediction samples: {len(predictions)}"
)
report.append(
    f"Features: 8"
)
report.append("")

report.append("## Model Performance")
report.append("")

mean_error = (
    predictions["predicted_difficulty"]
    - predictions["actual_difficulty"]
).mean()

mae = predictions["absolute_error"].mean()

report.append(f"- Mean Error: {mean_error:.4f}")
report.append(f"- MAE: {mae:.4f}")
report.append(
    f"- Maximum Absolute Error: "
    f"{predictions['absolute_error'].max():.4f}"
)

report.append("")

report.append("## Error Groups")
report.append("")

groups = errors["error_group"].value_counts()

for group, count in groups.items():
    report.append(f"- {group}: {count}")

report.append("")

report.append("## Feature/Error Correlations")
report.append("")

for _, row in correlations.iterrows():
    report.append(
        f"- {row['feature']}: "
        f"{row['error_correlation']:.4f}"
    )

report.append("")

report.append("## Interpretation")
report.append("")

report.append(
    "The model is evaluated against the engineered difficulty "
    "score produced by the current difficulty methodology."
)

report.append(
    "This analysis measures the model's ability to reproduce "
    "the existing difficulty-engine score."
)

report.append(
    "It does not establish agreement with human olympiad "
    "experts or official competition difficulty ratings."
)

output = base / "day7_model_analysis.md"

output.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print(f"\nSaved:")
print(output)

print("\nDay 7 analysis complete.")