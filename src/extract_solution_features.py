import pandas as pd
import re
from datasets import load_dataset
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/processed/mathnet_problems.csv"

OUTPUT_PATH = "data/processed/mathnet_features.csv"

SAMPLE_SIZE = 1000


# ============================================================
# LOAD CONVERTED DATA
# ============================================================

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - SOLUTION FEATURE EXTRACTION")
print("=" * 70)

print("\nLoading converted dataset...")

df = pd.read_csv(INPUT_PATH)

print(f"Loaded {len(df)} problems.")


# ============================================================
# LOAD ORIGINAL MATHNET
# ============================================================

print("\nLoading original MathNet solutions...")

dataset = load_dataset(
    "ShadenA/MathNet",
    split="train"
)

sample = dataset.select(
    range(min(SAMPLE_SIZE, len(dataset)))
)

print(f"Loaded {len(sample)} original problems.")


# ============================================================
# FEATURE EXTRACTION FUNCTIONS
# ============================================================

def count_equations(text):

    if not text:
        return 0

    inline_equations = len(
        re.findall(r"\$.*?\$", text)
    )

    display_equations = len(
        re.findall(
            r"\\\[.*?\\\]",
            text,
            flags=re.DOTALL
        )
    )

    return inline_equations + display_equations


def count_reasoning_indicators(text):

    if not text:
        return 0

    patterns = [
        r"\btherefore\b",
        r"\bhence\b",
        r"\bthus\b",
        r"\bit follows\b",
        r"\bconsequently\b",
        r"\bwe conclude\b",
        r"\bimplies\b",
        r"\bobserve\b",
        r"\bnotice\b",
        r"\bclaim\b",
    ]

    count = 0

    for pattern in patterns:

        count += len(
            re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )
        )

    return count


def count_proof_indicators(text):

    if not text:
        return 0

    patterns = [
        r"\bproof\b",
        r"\bsuppose\b",
        r"\bassume\b",
        r"\bcontradiction\b",
        r"\bcontrary\b",
        r"\bif and only if\b",
        r"\biff\b",
        r"\bwe prove\b",
        r"\bit remains to show\b",
    ]

    count = 0

    for pattern in patterns:

        count += len(
            re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )
        )

    return count


def count_case_analysis(text):

    if not text:
        return 0

    patterns = [
        r"\bcase\s+\d+\b",
        r"\bcase\s+[A-Z]\b",
        r"\bconsider the case\b",
        r"\bif\b",
        r"\botherwise\b",
    ]

    count = 0

    for pattern in patterns:

        count += len(
            re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )
        )

    return count


def count_calculation_indicators(text):

    if not text:
        return 0

    patterns = [
        r"\bcalculate\b",
        r"\bcompute\b",
        r"\bevaluate\b",
        r"\bsimplify\b",
        r"\bexpand\b",
        r"\bfactor\b",
        r"\bsum\b",
        r"\bproduct\b",
    ]

    count = 0

    for pattern in patterns:

        count += len(
            re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )
        )

    return count


def estimate_major_steps(text):

    if not text:
        return 0

    # Numbered steps
    numbered_steps = len(
        re.findall(
            r"(?:^|\n)\s*(?:\d+[\.\)]|Step\s+\d+)",
            text,
            flags=re.IGNORECASE
        )
    )

    # Paragraphs as a secondary structural signal
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    paragraph_count = len(paragraphs)

    return max(
        numbered_steps,
        min(paragraph_count, 20)
    )


# ============================================================
# CREATE FEATURE RECORDS
# ============================================================

features = []


for index, problem in enumerate(sample):

    solution = problem["solutions_markdown"]

    # --------------------------------------------------------
    # Handle solution format
    # --------------------------------------------------------

    if isinstance(solution, list):

        solution_text = "\n\n".join(
            str(item)
            for item in solution
            if item
        )

    elif solution:

        solution_text = str(solution)

    else:

        solution_text = ""


    # --------------------------------------------------------
    # Basic text features
    # --------------------------------------------------------

    solution_length = len(solution_text)

    solution_words = len(
        solution_text.split()
    )

    paragraphs = [
        p.strip()
        for p in re.split(
            r"\n\s*\n",
            solution_text
        )
        if p.strip()
    ]

    solution_paragraphs = len(
        paragraphs
    )


    # --------------------------------------------------------
    # NLP / structural features
    # --------------------------------------------------------

    equation_count = count_equations(
        solution_text
    )

    reasoning_indicators = (
        count_reasoning_indicators(
            solution_text
        )
    )

    proof_indicators = (
        count_proof_indicators(
            solution_text
        )
    )

    case_analysis = (
        count_case_analysis(
            solution_text
        )
    )

    calculation_indicators = (
        count_calculation_indicators(
            solution_text
        )
    )

    major_steps = estimate_major_steps(
        solution_text
    )


    # --------------------------------------------------------
    # Create record
    # --------------------------------------------------------

    features.append({

        "problem_id":
            f"MATHNET-{problem['id']}",

        "solution_length":
            solution_length,

        "solution_words":
            solution_words,

        "solution_paragraphs":
            solution_paragraphs,

        "equation_count":
            equation_count,

        "reasoning_indicators":
            reasoning_indicators,

        "proof_indicators":
            proof_indicators,

        "case_analysis":
            case_analysis,

        "calculation_indicators":
            calculation_indicators,

        "solution_major_steps":
            major_steps,
    })


# ============================================================
# CREATE FEATURE DATAFRAME
# ============================================================

feature_df = pd.DataFrame(
    features
)


# ============================================================
# MERGE WITH EXISTING DATA
# ============================================================

df = df.merge(
    feature_df,
    on="problem_id",
    how="left"
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


# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 70)
print("FEATURE EXTRACTION COMPLETE")
print("=" * 70)

print(f"\nRows: {len(df)}")

print(
    f"Columns: {len(df.columns)}"
)

print("\nNew features:")

new_features = [
    "solution_length",
    "solution_paragraphs",
    "equation_count",
    "reasoning_indicators",
    "proof_indicators",
    "case_analysis",
    "calculation_indicators",
]

for feature in new_features:

    print(f"- {feature}")


print("\nFeature statistics:")

# Check actual column names after merge
print("\nFeature columns found:")

for feature in new_features:

    if feature in df.columns:
        print(f"✓ {feature}")

    elif f"{feature}_x" in df.columns:
        print(f"✓ {feature}_x")

    elif f"{feature}_y" in df.columns:
        print(f"✓ {feature}_y")

    else:
        print(f"✗ {feature} NOT FOUND")


# Build list of available feature columns
available_features = []

for feature in new_features:

    if feature in df.columns:

        available_features.append(feature)

    elif f"{feature}_y" in df.columns:

        available_features.append(
            f"{feature}_y"
        )

    elif f"{feature}_x" in df.columns:

        available_features.append(
            f"{feature}_x"
        )


print("\nStatistics:")

print(
    df[available_features]
    .describe()
)

print("\nSaved to:")

print(OUTPUT_PATH)