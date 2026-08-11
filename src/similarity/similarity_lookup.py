import pandas as pd
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - SIMILARITY LOOKUP")
print("=" * 70)

INPUT = Path("data/processed/problem_similarity.csv")
OUTPUT = Path("data/processed/similarity_lookup.csv")

df = pd.read_csv(INPUT)

lookup = (
    df.sort_values(
        ["problem_id", "rank"]
    )
    .groupby("problem_id")
    .agg({
        "similar_problem_id": lambda x: " | ".join(x.astype(str)),
        "similarity_score": lambda x: " | ".join(
            f"{v:.4f}" for v in x
        )
    })
    .reset_index()
)

lookup.to_csv(OUTPUT, index=False)

print(f"\nProblems with similarity results: {len(lookup)}")

print("\nExample:")
print(lookup.head(5).to_string(index=False))

print(f"\nSaved:")
print(OUTPUT)