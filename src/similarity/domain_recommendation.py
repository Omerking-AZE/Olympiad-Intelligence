import pandas as pd
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - DOMAIN RECOMMENDATION ENGINE")
print("=" * 70)

PROBLEMS = Path("data/processed/mathnet_difficulty.csv")
SIMILARITY = Path("data/processed/problem_similarity.csv")

problems = pd.read_csv(PROBLEMS)
similarity = pd.read_csv(SIMILARITY)

meta = problems[
    [
        "problem_id",
        "domain",
        "subtopic",
        "difficulty_label",
    ]
]

df = similarity.merge(
    meta,
    on="problem_id",
    how="left"
)

df = df.merge(
    meta.add_prefix("similar_"),
    left_on="similar_problem_id",
    right_on="similar_problem_id",
    how="left"
)

recommended = df[
    df["domain"] == df["similar_domain"]
].copy()

recommended = recommended.sort_values(
    "similarity_score",
    ascending=False
)

OUTPUT = Path(
    "data/processed/domain_recommendations.csv"
)

recommended.to_csv(
    OUTPUT,
    index=False
)

print(
    f"\nSame-domain recommendations: "
    f"{len(recommended)}"
)

print("\nTop recommendations:")
print(
    recommended[
        [
            "problem_id",
            "similar_problem_id",
            "similarity_score",
            "domain",
            "subtopic",
            "similar_difficulty_label",
        ]
    ]
    .head(20)
    .to_string(index=False)
)

print(f"\nSaved:")
print(OUTPUT)