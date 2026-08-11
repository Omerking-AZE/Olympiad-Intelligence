import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/processed/mathnet_features.csv"

REPORT_PATH = "data/processed/solution_feature_report.txt"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - SOLUTION FEATURE ANALYSIS")
print("=" * 70)

df = pd.read_csv(INPUT_PATH)

print(f"\nLoaded {len(df)} problems.")
print(f"Total columns: {len(df.columns)}")


# ============================================================
# FEATURES
# ============================================================

features = [
    "solution_length",
    "solution_words",
    "solution_paragraphs",
    "equation_count",
    "reasoning_indicators",
    "proof_indicators",
    "case_analysis",
    "calculation_indicators",
    "solution_major_steps",
]


# ============================================================
# BASIC QUALITY CHECK
# ============================================================

print("\n" + "=" * 70)
print("1. MISSING VALUES")
print("=" * 70)

print(
    df[features]
    .isna()
    .sum()
)


# ============================================================
# ZERO-RATE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("2. ZERO-RATE ANALYSIS")
print("=" * 70)

for feature in features:

    zero_count = (
        df[feature] == 0
    ).sum()

    zero_rate = (
        zero_count / len(df)
    )

    print(
        f"{feature:30s} "
        f"zeros={zero_count:4d} "
        f"rate={zero_rate:.2%}"
    )


# ============================================================
# VARIANCE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("3. VARIANCE ANALYSIS")
print("=" * 70)

for feature in features:

    variance = df[feature].var()

    unique_values = (
        df[feature]
        .nunique()
    )

    print(
        f"{feature:30s} "
        f"variance={variance:12.3f} "
        f"unique={unique_values:4d}"
    )


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("4. CORRELATION MATRIX")
print("=" * 70)

correlation = (
    df[features]
    .corr()
)

print(
    correlation
    .round(2)
    .to_string()
)


# ============================================================
# HIGH CORRELATION PAIRS
# ============================================================

print("\n" + "=" * 70)
print("5. HIGH CORRELATION PAIRS")
print("=" * 70)

found_pairs = []

for i in range(len(features)):

    for j in range(i + 1, len(features)):

        feature_a = features[i]
        feature_b = features[j]

        corr = correlation.loc[
            feature_a,
            feature_b
        ]

        if abs(corr) >= 0.75:

            found_pairs.append(
                (
                    feature_a,
                    feature_b,
                    corr
                )
            )

            print(
                f"{feature_a:30s} "
                f"<-> "
                f"{feature_b:30s} "
                f"corr={corr:.3f}"
            )


if not found_pairs:

    print(
        "No feature pairs exceeded "
        "the 0.75 correlation threshold."
    )


# ============================================================
# DISTRIBUTION SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("6. DISTRIBUTION SUMMARY")
print("=" * 70)

summary = (
    df[features]
    .describe()
    .T
)

summary[
    "zero_rate"
] = [
    (df[f] == 0).mean()
    for f in features
]

summary[
    "unique_values"
] = [
    df[f].nunique()
    for f in features
]

print(
    summary[
        [
            "count",
            "mean",
            "std",
            "min",
            "50%",
            "max",
            "zero_rate",
            "unique_values",
        ]
    ]
    .round(3)
    .to_string()
)


# ============================================================
# SAVE REPORT
# ============================================================

Path(
    "data/processed"
).mkdir(
    parents=True,
    exist_ok=True
)

with open(
    REPORT_PATH,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "OLYMPIAD INTELLIGENCE\n"
        "SOLUTION FEATURE ANALYSIS\n"
        "\n"
    )

    f.write(
        summary.to_string()
    )

    f.write(
        "\n\nHIGH CORRELATION PAIRS\n"
    )

    for pair in found_pairs:

        f.write(
            f"{pair[0]} <-> "
            f"{pair[1]}: "
            f"{pair[2]:.3f}\n"
        )


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print(
    f"\nReport saved to:\n{REPORT_PATH}"
)