import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/processed/mathnet_features.csv"

OUTPUT_PATH = "data/processed/mathnet_model_features.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - PREPARE MODEL FEATURES")
print("=" * 70)

df = pd.read_csv(INPUT_PATH)

print(f"\nLoaded {len(df)} problems.")


# ============================================================
# SELECT FINAL FEATURES
# ============================================================

selected_features = [
    "solution_length",
    "solution_paragraphs",
    "equation_count",
    "reasoning_indicators",
    "proof_indicators",
    "case_analysis",
    "calculation_indicators",
]


# ============================================================
# SOLUTION AVAILABILITY
# ============================================================

df["solution_available"] = (
    df["solution_length"] > 0
).astype(int)


# ============================================================
# SOLUTION DENSITY FEATURES
# ============================================================

# Avoid division by zero.

df["equation_density"] = (
    df["equation_count"]
    / df["solution_words"].clip(lower=1)
)

df["reasoning_density"] = (
    df["reasoning_indicators"]
    / df["solution_words"].clip(lower=1)
)

df["proof_density"] = (
    df["proof_indicators"]
    / df["solution_words"].clip(lower=1)
)


# ============================================================
# LOG TRANSFORM
# ============================================================

import numpy as np

df["log_solution_length"] = np.log1p(
    df["solution_length"]
)

df["log_equation_count"] = np.log1p(
    df["equation_count"]
)


# ============================================================
# FINAL FEATURE LIST
# ============================================================

final_features = [
    "solution_available",

    "solution_length",
    "solution_paragraphs",
    "equation_count",

    "reasoning_indicators",
    "proof_indicators",
    "case_analysis",
    "calculation_indicators",

    "equation_density",
    "reasoning_density",
    "proof_density",

    "log_solution_length",
    "log_equation_count",
]


# ============================================================
# DATA QUALITY REPORT
# ============================================================

print("\n" + "=" * 70)
print("SOLUTION AVAILABILITY")
print("=" * 70)

print(
    df["solution_available"]
    .value_counts()
    .sort_index()
)

available = (
    df["solution_available"]
    .sum()
)

missing = (
    len(df) - available
)

print(
    f"\nSolutions available: {available}"
)

print(
    f"Solutions missing:   {missing}"
)

print(
    f"Availability rate:   "
    f"{available / len(df):.2%}"
)


# ============================================================
# FEATURE STATISTICS
# ============================================================

print("\n" + "=" * 70)
print("FINAL FEATURE STATISTICS")
print("=" * 70)

print(
    df[final_features]
    .describe()
    .round(3)
    .to_string()
)


# ============================================================
# SAVE
# ============================================================

Path(
    "data/processed"
).mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\n" + "=" * 70)
print("PREPARATION COMPLETE")
print("=" * 70)

print(
    f"\nFinal features: "
    f"{len(final_features)}"
)

for feature in final_features:
    print(f"- {feature}")

print(
    f"\nSaved to:\n{OUTPUT_PATH}"
)