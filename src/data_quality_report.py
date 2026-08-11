import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/processed/mathnet_problems.csv"

REPORT_DIR = Path("reports")

REPORT_PATH = REPORT_DIR / "mathnet_quality_report.txt"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - DATA QUALITY REPORT")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(INPUT_PATH)

print(f"Loaded {len(df)} problems.")


# ============================================================
# CREATE REPORT
# ============================================================

report = []

report.append("=" * 70)
report.append("OLYMPIAD INTELLIGENCE - MATHNET DATA QUALITY REPORT")
report.append("=" * 70)

report.append("")
report.append(f"Total problems: {len(df)}")
report.append(f"Total columns: {len(df.columns)}")


# ============================================================
# DUPLICATE IDS
# ============================================================

duplicate_ids = df["problem_id"].duplicated().sum()

report.append("")
report.append("=" * 70)
report.append("1. DUPLICATE PROBLEM IDS")
report.append("=" * 70)

report.append(
    f"Duplicate IDs: {duplicate_ids}"
)


# ============================================================
# DUPLICATE PROBLEM TEXT
# ============================================================

duplicate_text = df["problem_text"].duplicated().sum()

report.append("")
report.append("=" * 70)
report.append("2. DUPLICATE PROBLEM TEXT")
report.append("=" * 70)

report.append(
    f"Duplicate problem texts: {duplicate_text}"
)


# ============================================================
# MISSING VALUES
# ============================================================

report.append("")
report.append("=" * 70)
report.append("3. MISSING VALUES")
report.append("=" * 70)

missing = df.isna().sum()

missing = missing.sort_values(
    ascending=False
)

for column, count in missing.items():

    percentage = (
        count / len(df) * 100
    )

    report.append(
        f"{column}: {count} ({percentage:.1f}%)"
    )


# ============================================================
# DOMAIN DISTRIBUTION
# ============================================================

report.append("")
report.append("=" * 70)
report.append("4. DOMAIN DISTRIBUTION")
report.append("=" * 70)

domain_counts = (
    df["domain"]
    .value_counts(dropna=False)
)

for domain, count in domain_counts.items():

    percentage = (
        count / len(df) * 100
    )

    report.append(
        f"{domain}: {count} ({percentage:.1f}%)"
    )


# ============================================================
# PROBLEM TYPE
# ============================================================

report.append("")
report.append("=" * 70)
report.append("5. PROBLEM TYPE DISTRIBUTION")
report.append("=" * 70)

problem_type_counts = (
    df["problem_type"]
    .value_counts(dropna=False)
)

for problem_type, count in problem_type_counts.items():

    percentage = (
        count / len(df) * 100
    )

    report.append(
        f"{problem_type}: {count} ({percentage:.1f}%)"
    )


# ============================================================
# PROOF REQUIRED
# ============================================================

report.append("")
report.append("=" * 70)
report.append("6. PROOF REQUIREMENT")
report.append("=" * 70)

proof_counts = (
    df["proof_required"]
    .value_counts(dropna=False)
)

for value, count in proof_counts.items():

    percentage = (
        count / len(df) * 100
    )

    report.append(
        f"{value}: {count} ({percentage:.1f}%)"
    )


# ============================================================
# COUNTRY DISTRIBUTION
# ============================================================

report.append("")
report.append("=" * 70)
report.append("7. COUNTRY DISTRIBUTION")
report.append("=" * 70)

country_counts = (
    df["country"]
    .value_counts()
    .head(20)
)

for country, count in country_counts.items():

    report.append(
        f"{country}: {count}"
    )


# ============================================================
# COMPETITION DISTRIBUTION
# ============================================================

report.append("")
report.append("=" * 70)
report.append("8. TOP COMPETITIONS")
report.append("=" * 70)

competition_counts = (
    df["competition"]
    .value_counts()
    .head(20)
)

for competition, count in competition_counts.items():

    report.append(
        f"{competition}: {count}"
    )


# ============================================================
# LANGUAGE DISTRIBUTION
# ============================================================

report.append("")
report.append("=" * 70)
report.append("9. LANGUAGE DISTRIBUTION")
report.append("=" * 70)

language_counts = (
    df["language"]
    .value_counts(dropna=False)
)

for language, count in language_counts.items():

    report.append(
        f"{language}: {count}"
    )


# ============================================================
# MULTI-TOPIC ANALYSIS
# ============================================================

report.append("")
report.append("=" * 70)
report.append("10. MULTI-TOPIC ANALYSIS")
report.append("=" * 70)

multi_topic_count = (
    df["subtopic"]
    .fillna("")
    .apply(
        lambda x: "|" in str(x)
    )
    .sum()
)

multi_topic_percentage = (
    multi_topic_count / len(df) * 100
)

report.append(
    f"Problems with multiple subtopics: "
    f"{multi_topic_count} "
    f"({multi_topic_percentage:.1f}%)"
)


# ============================================================
# PROBLEM TEXT LENGTH
# ============================================================

report.append("")
report.append("=" * 70)
report.append("11. PROBLEM TEXT LENGTH")
report.append("=" * 70)

text_lengths = (
    df["problem_text"]
    .fillna("")
    .astype(str)
    .str.len()
)

report.append(
    f"Minimum characters: {text_lengths.min()}"
)

report.append(
    f"Maximum characters: {text_lengths.max()}"
)

report.append(
    f"Mean characters: {text_lengths.mean():.1f}"
)

report.append(
    f"Median characters: {text_lengths.median():.1f}"
)


# ============================================================
# FINAL ANSWER COVERAGE
# ============================================================

report.append("")
report.append("=" * 70)
report.append("12. FINAL ANSWER COVERAGE")
report.append("=" * 70)

missing_answers = df["final_answer"].isna().sum()

answer_percentage = (
    (len(df) - missing_answers)
    / len(df)
    * 100
)

report.append(
    f"Problems with final answer: "
    f"{len(df) - missing_answers} "
    f"({answer_percentage:.1f}%)"
)

report.append(
    f"Missing final answers: "
    f"{missing_answers}"
)


# ============================================================
# SAVE REPORT
# ============================================================

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    REPORT_PATH,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(report)
    )


# ============================================================
# PRINT REPORT
# ============================================================

print(
    "\n".join(report)
)

print("\n" + "=" * 70)
print("REPORT SAVED")
print("=" * 70)

print(f"\nSaved to:")
print(REPORT_PATH)