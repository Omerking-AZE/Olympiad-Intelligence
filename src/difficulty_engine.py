import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# OLYMPIAD INTELLIGENCE - DIFFICULTY ENGINE
# ============================================================

INPUT_PATH = "data/processed/mathnet_model_features.csv"
OUTPUT_PATH = "data/processed/mathnet_difficulty.csv"


print("=" * 70)
print("OLYMPIAD INTELLIGENCE - DIFFICULTY ENGINE")
print("=" * 70)


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_PATH)

print(f"\nLoaded {len(df)} problems.")


# ============================================================
# 2. HELPER FUNCTION
# ============================================================

def percentile_score(series):
    """
    Convert a numerical feature into a 0-100 percentile score.
    """
    return series.rank(pct=True) * 100


# ============================================================
# 3. NORMALIZED COMPLEXITY FEATURES
# ============================================================

print("\nCalculating normalized complexity signals...")


# Solution length
df["length_score"] = percentile_score(
    df["log_solution_length"]
)


# Equation complexity
df["equation_score"] = percentile_score(
    df["log_equation_count"]
)


# Reasoning
df["reasoning_score"] = percentile_score(
    df["reasoning_indicators"]
)


# Proof structure
df["proof_score"] = percentile_score(
    df["proof_indicators"]
)


# Case analysis
df["case_score"] = percentile_score(
    df["case_analysis"]
)


# Number of solution steps
df["steps_score"] = percentile_score(
    df["solution_paragraphs"]
)


# ============================================================
# 4. PROBLEM TYPE SCORE
# ============================================================

print("Calculating problem-type complexity...")


def problem_type_score(problem_type):

    if pd.isna(problem_type):
        return 50

    problem_type = str(problem_type).lower()

    if problem_type == "proof only":
        return 100

    if problem_type == "proof and answer":
        return 90

    if problem_type == "final answer only":
        return 55

    if problem_type == "mcq":
        return 35

    return 50


df["problem_type_score"] = (
    df["problem_type"]
    .apply(problem_type_score)
)


# ============================================================
# 5. DOMAIN COMPLEXITY
# ============================================================

print("Calculating domain complexity...")


def domain_score(domain):

    if pd.isna(domain):
        return 50

    domain = str(domain).lower()

    scores = []

    if "algebra" in domain:
        scores.append(75)

    if "number theory" in domain:
        scores.append(80)

    if "geometry" in domain:
        scores.append(78)

    if "discrete" in domain:
        scores.append(82)

    if "calculus" in domain:
        scores.append(70)

    if "statistics" in domain:
        scores.append(55)

    if "precalculus" in domain:
        scores.append(60)

    if "word" in domain:
        scores.append(45)

    if not scores:
        return 50

    return np.mean(scores)


df["domain_score"] = (
    df["domain"]
    .apply(domain_score)
)


# ============================================================
# 6. SOLUTION AVAILABILITY
# ============================================================

# Missing solutions should NOT automatically mean easy.
#
# We therefore do NOT give missing solutions a difficulty penalty.
#
# This feature is kept only as metadata.

df["solution_availability_score"] = (
    df["solution_available"] * 100
)


# ============================================================
# 7. MULTI-SIGNAL DIFFICULTY SCORE
# ============================================================

print("Building multi-signal difficulty score...")


df["difficulty_score"] = (
      0.20 * df["length_score"]
    + 0.15 * df["equation_score"]
    + 0.20 * df["reasoning_score"]
    + 0.15 * df["proof_score"]
    + 0.10 * df["case_score"]
    + 0.10 * df["steps_score"]
    + 0.05 * df["problem_type_score"]
    + 0.05 * df["domain_score"]
)


# ============================================================
# 8. CLIP SCORE
# ============================================================

df["difficulty_score"] = (
    df["difficulty_score"]
    .clip(0, 100)
)


# ============================================================
# 9. CONVERT TO 1-5 DIFFICULTY
# ============================================================

def difficulty_level(score):

    if score < 20:
        return 1

    elif score < 40:
        return 2

    elif score < 60:
        return 3

    elif score < 80:
        return 4

    else:
        return 5


df["difficulty"] = (
    df["difficulty_score"]
    .apply(difficulty_level)
)


# ============================================================
# 10. DIFFICULTY LABEL
# ============================================================

def difficulty_label(level):

    labels = {
        1: "Very Easy",
        2: "Easy",
        3: "Medium",
        4: "Hard",
        5: "Very Hard"
    }

    return labels[level]


df["difficulty_label"] = (
    df["difficulty"]
    .apply(difficulty_label)
)


# ============================================================
# 11. STATISTICS
# ============================================================

print("\n" + "=" * 70)
print("DIFFICULTY DISTRIBUTION")
print("=" * 70)

print(
    df["difficulty"]
    .value_counts()
    .sort_index()
)


print("\nDifficulty labels:")

print(
    df["difficulty_label"]
    .value_counts()
)


# ============================================================
# 12. SCORE STATISTICS
# ============================================================

print("\n" + "=" * 70)
print("DIFFICULTY SCORE STATISTICS")
print("=" * 70)

print(
    df["difficulty_score"]
    .describe()
    .round(3)
)


# ============================================================
# 13. TOP 10 HARDEST
# ============================================================

print("\n" + "=" * 70)
print("TOP 10 HARDEST PROBLEMS")
print("=" * 70)

hardest = (
    df.sort_values(
        "difficulty_score",
        ascending=False
    )
    [
        [
            "problem_id",
            "domain",
            "problem_type",
            "difficulty_score",
            "difficulty_label"
        ]
    ]
    .head(10)
)

print(
    hardest.to_string(index=False)
)


# ============================================================
# 14. TOP 10 EASIEST
# ============================================================

print("\n" + "=" * 70)
print("TOP 10 EASIEST PROBLEMS")
print("=" * 70)

easiest = (
    df.sort_values(
        "difficulty_score",
        ascending=True
    )
    [
        [
            "problem_id",
            "domain",
            "problem_type",
            "difficulty_score",
            "difficulty_label"
        ]
    ]
    .head(10)
)

print(
    easiest.to_string(index=False)
)


# ============================================================
# 15. SAVE
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


# ============================================================
# 16. COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("DIFFICULTY ENGINE COMPLETE")
print("=" * 70)

print(
    f"\nRows: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)

print(
    f"\nSaved to:"
    f"\n{OUTPUT_PATH}"
)

print(
    "\nNew features:"
)

for feature in [
    "length_score",
    "equation_score",
    "reasoning_score",
    "proof_score",
    "case_score",
    "steps_score",
    "problem_type_score",
    "domain_score",
    "difficulty_score",
    "difficulty",
    "difficulty_label"
]:
    print(f"- {feature}")