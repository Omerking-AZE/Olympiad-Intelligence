import pandas as pd
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - SIMILARITY EVALUATION")
print("=" * 70)

SIMILARITY = Path("data/processed/problem_similarity.csv")
PROBLEMS = Path("data/processed/mathnet_difficulty.csv")

similarity = pd.read_csv(SIMILARITY)
problems = pd.read_csv(PROBLEMS)

print(f"\nSimilarity records: {len(similarity)}")
print(f"Problems: {len(problems)}")

meta = problems[
    [
        "problem_id",
        "domain",
        "subtopic",
        "difficulty",
        "difficulty_label",
    ]
].copy()

similarity = similarity.merge(
    meta,
    on="problem_id",
    how="left"
)

similarity = similarity.merge(
    meta.add_prefix("similar_"),
    left_on="similar_problem_id",
    right_on="similar_problem_id",
    how="left"
)

similarity["same_domain"] = (
    similarity["domain"]
    == similarity["similar_domain"]
)

similarity["same_difficulty"] = (
    similarity["difficulty"]
    == similarity["similar_difficulty"]
)

domain_rate = similarity["same_domain"].mean()
difficulty_rate = similarity["same_difficulty"].mean()

print("\nSimilarity evaluation:")
print(f"Same-domain rate:      {domain_rate:.3f}")
print(f"Same-difficulty rate:  {difficulty_rate:.3f}")

print("\nTop similarities:")
print(
    similarity[
        [
            "problem_id",
            "similar_problem_id",
            "similarity_score",
            "domain",
            "similar_domain",
            "same_domain",
            "difficulty_label",
            "similar_difficulty_label",
        ]
    ]
    .head(20)
    .to_string(index=False)
)

OUTPUT = Path(
    "data/processed/similarity_evaluation.csv"
)

similarity.to_csv(OUTPUT, index=False)

print(f"\nSaved:")
print(OUTPUT)