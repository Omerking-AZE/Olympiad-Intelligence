import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - PROBLEM SIMILARITY ENGINE")
print("=" * 70)

INPUT = Path("data/processed/similarity_features.csv")
OUTPUT = Path("data/processed/problem_similarity.csv")

df = pd.read_csv(INPUT)

print(f"\nLoaded {len(df)} problems.")

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

features = [f for f in features if f in df.columns]

X = df[features].fillna(0).values

results = []

# Compare every problem against every other problem.
# For 1000 problems this is manageable.
for i in range(len(df)):
    distances = np.linalg.norm(X - X[i], axis=1)

    # Convert distance to similarity.
    similarity = 1 / (1 + distances)

    # Exclude itself.
    similarity[i] = -1

    nearest = np.argsort(similarity)[-10:][::-1]

    for rank, j in enumerate(nearest, start=1):
        results.append({
            "problem_id": df.iloc[i]["problem_id"],
            "similar_problem_id": df.iloc[j]["problem_id"],
            "similarity_score": similarity[j],
            "rank": rank,
        })

result = pd.DataFrame(results)

result.to_csv(OUTPUT, index=False)

print(f"\nSimilarity pairs generated: {len(result)}")

print("\nTop similarity pairs:")
print(
    result.sort_values(
        "similarity_score",
        ascending=False
    ).head(20).to_string(index=False)
)

print(f"\nSaved:")
print(OUTPUT)