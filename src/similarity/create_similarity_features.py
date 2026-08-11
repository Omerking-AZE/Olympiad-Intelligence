import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - SIMILARITY FEATURE ENGINEERING")
print("=" * 70)

INPUT = Path("data/processed/mathnet_difficulty.csv")
OUTPUT = Path("data/processed/similarity_features.csv")

df = pd.read_csv(INPUT)

print(f"\nLoaded {len(df)} problems.")

# Numeric features useful for similarity
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

available = [f for f in features if f in df.columns]

print(f"\nSimilarity features: {len(available)}")

# Normalize each numerical feature to 0-1
similarity_df = df[
    ["problem_id", "domain", "subtopic", "concepts", "problem_type"]
    + available
].copy()

for feature in available:
    min_value = similarity_df[feature].min()
    max_value = similarity_df[feature].max()

    if max_value > min_value:
        similarity_df[feature] = (
            similarity_df[feature] - min_value
        ) / (max_value - min_value)
    else:
        similarity_df[feature] = 0.0

similarity_df.to_csv(OUTPUT, index=False)

print("\nNormalized feature statistics:")
print(similarity_df[available].describe().to_string())

print(f"\nSaved:")
print(OUTPUT)