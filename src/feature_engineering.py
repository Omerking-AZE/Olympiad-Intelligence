import pandas as pd
from pathlib import Path

INPUT_PATH = "data/problems.csv"
OUTPUT_PATH = "data/processed/features.csv"

# Load dataset
df = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("OLYMPIAD INTELLIGENCE - FEATURE ENGINEERING")
print("=" * 60)

print(f"Loaded {len(df)} problems.")
print(f"Original columns: {len(df.columns)}")

# ---------------------------------------------------------
# 1. Check required columns
# ---------------------------------------------------------

required_columns = [
    "proof_required",
    "solution_depth",
    "reasoning_intensity",
    "calculation_intensity",
    "major_steps",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# ---------------------------------------------------------
# 2. Clean proof_required
# ---------------------------------------------------------

# Convert different possible values into True/False
df["proof_required"] = (
    df["proof_required"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map({
        "true": 1,
        "false": 0,
        "1": 1,
        "0": 0,
        "yes": 1,
        "no": 0,
    })
)

# Check whether conversion created missing values
if df["proof_required"].isna().any():
    missing_count = df["proof_required"].isna().sum()

    print(
        f"\nWarning: {missing_count} problem(s) have "
        "an invalid or missing proof_required value."
    )

    # For this initial synthetic dataset,
    # use 0 as the neutral fallback.
    df["proof_required"] = df["proof_required"].fillna(0)

# Convert to integer
df["proof_required"] = df["proof_required"].astype(int)

# ---------------------------------------------------------
# 3. Create reasoning score
# ---------------------------------------------------------

df["reasoning_score"] = (
    df["reasoning_intensity"] * 0.5
    + df["solution_depth"] * 0.3
    + df["major_steps"] * 0.2
)

# ---------------------------------------------------------
# 4. Create complexity score
# ---------------------------------------------------------

df["complexity_score"] = (
    df["reasoning_intensity"]
    + df["calculation_intensity"]
    + df["solution_depth"]
)

# ---------------------------------------------------------
# 5. Check numerical features
# ---------------------------------------------------------

numeric_features = [
    "solution_depth",
    "estimated_time_minutes",
    "reasoning_intensity",
    "calculation_intensity",
    "major_steps",
    "difficulty",
]

for column in numeric_features:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Report missing numerical values
missing_numeric = df[numeric_features].isna().sum()

if missing_numeric.any():
    print("\nMissing numerical values:")
    print(missing_numeric[missing_numeric > 0])

# ---------------------------------------------------------
# 6. Create output directory
# ---------------------------------------------------------

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

# ---------------------------------------------------------
# 7. Save processed dataset
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nFeature engineering complete.")
print(f"Saved: {OUTPUT_PATH}")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\nNew features:")
print("- reasoning_score")
print("- complexity_score")