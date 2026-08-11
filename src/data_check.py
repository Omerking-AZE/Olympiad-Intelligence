import pandas as pd

DATA_PATH = "data/problems.csv"

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("OLYMPIAD INTELLIGENCE - DATASET CHECK")
print("=" * 60)

print(f"Number of problems: {len(df)}")
print(f"Number of features: {len(df.columns)}")

print("\nDomains:")
print(df["domain"].value_counts())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate problem IDs:")
print(df["problem_id"].duplicated().sum())
required_columns = [
    "problem_id",
    "domain",
    "subtopic",
    "difficulty",
    "concepts",
    "prerequisites",
    "solution_depth",
    "estimated_time_minutes",
    "proof_required",
    "reasoning_intensity",
    "calculation_intensity",
    "major_steps",
    "data_type"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    print("\nERROR: Missing columns:")
    print(missing_columns)
else:
    print("\nAll required columns are present.")

if df["problem_id"].duplicated().any():
    print("ERROR: Duplicate problem IDs found.")
else:
    print("No duplicate problem IDs.")

if df["difficulty"].between(1, 10).all():
    print("Difficulty values are valid.")
else:
    print("ERROR: Invalid difficulty value found.")

print("\nDataset validation complete.")