import pandas as pd
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - SIMILARITY RESEARCH REPORT")
print("=" * 70)

base = Path("data/processed")

problems = pd.read_csv(
    base / "mathnet_difficulty.csv"
)

similarity = pd.read_csv(
    base / "problem_similarity.csv"
)

evaluation = pd.read_csv(
    base / "similarity_evaluation.csv"
)

recommendations = pd.read_csv(
    base / "domain_recommendations.csv"
)

report = []

report.append("# Olympiad Intelligence — Day 8 Similarity Analysis")
report.append("")

report.append("## Dataset")
report.append("")
report.append(
    f"- Problems analyzed: {len(problems)}"
)
report.append(
    f"- Similarity records: {len(similarity)}"
)
report.append(
    "- Nearest neighbors per problem: 10"
)

report.append("")

report.append("## Similarity Features")
report.append("")

features = [
    "length_score",
    "equation_score",
    "reasoning_score",
    "proof_score",
    "case_score",
    "steps_score",
    "problem_type_score",
    "domain_score",
    "difficulty_score",
]

for feature in features:
    if feature in problems.columns:
        report.append(f"- `{feature}`")

report.append("")

report.append("## Evaluation")
report.append("")

same_domain = evaluation["same_domain"].mean()
same_difficulty = evaluation["same_difficulty"].mean()

report.append(
    f"- Same-domain rate: {same_domain:.4f}"
)

report.append(
    f"- Same-difficulty rate: {same_difficulty:.4f}"
)

report.append("")

report.append("## Interpretation")
report.append("")

report.append(
    "The similarity engine identifies problems with similar "
    "engineered structural and difficulty features."
)

report.append(
    "The current evaluation measures structural similarity "
    "and domain consistency rather than semantic mathematical "
    "equivalence."
)

report.append(
    "Future versions should incorporate mathematical text "
    "embeddings, concepts, subtopics, and problem statements "
    "to improve semantic similarity."
)

output = base / "day8_similarity_report.md"

output.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print(f"\nSaved:")
print(output)

print("\nDay 8 similarity analysis complete.")