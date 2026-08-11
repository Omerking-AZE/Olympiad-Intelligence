from datasets import load_dataset
import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_PATH = "data/processed/mathnet_problems.csv"

SAMPLE_SIZE = 1000


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - MATHNET CONVERTER")
print("=" * 70)

print("\nLoading MathNet...")

dataset = load_dataset(
    "ShadenA/MathNet",
    split="train",
)

print(f"Loaded {len(dataset)} problems.")


# ============================================================
# SAMPLE
# ============================================================

sample_size = min(SAMPLE_SIZE, len(dataset))

print(f"\nSelecting first {sample_size} problems...")

sample = dataset.select(range(sample_size))


# ============================================================
# CONVERSION
# ============================================================

records = []

for index, problem in enumerate(sample):

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    problem_id = str(problem["id"])

    country = problem["country"]
    competition = problem["competition"]
    language = problem["language"]
    problem_type = problem["problem_type"]

    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    topics = problem["topics_flat"]

    domain = None
    subtopic = None
    concepts = None

    if topics:

        parsed_topics = []

        for topic in topics:

            parts = [
                part.strip()
                for part in topic.split(">")
                if part.strip()
            ]

            if parts:
                parsed_topics.append(parts)

        if parsed_topics:

            # ------------------------------------------------
            # Domains
            # ------------------------------------------------

            domains = sorted({
                parts[0]
                for parts in parsed_topics
                if len(parts) >= 1
            })

            domain = " | ".join(domains)

            # ------------------------------------------------
            # Subtopics
            # ------------------------------------------------

            subtopics = sorted({
                parts[1]
                for parts in parsed_topics
                if len(parts) >= 2
            })

            subtopic = " | ".join(subtopics)

            # ------------------------------------------------
            # Concepts
            # ------------------------------------------------

            concept_list = []

            for parts in parsed_topics:

                if len(parts) >= 3:

                    concept = " > ".join(parts[2:])

                    if concept not in concept_list:
                        concept_list.append(concept)

            concepts = " | ".join(concept_list)

    # --------------------------------------------------------
    # Proof required
    # --------------------------------------------------------

    proof_required = None

    if problem_type in [
        "proof and answer",
        "proof only"
    ]:
        proof_required = True

    elif problem_type in [
        "final answer only",
        "MCQ"
    ]:
        proof_required = False

    # --------------------------------------------------------
    # Create record
    # --------------------------------------------------------

    record = {

        "problem_id": f"MATHNET-{problem_id}",

        "source": "MathNet",

        "competition": competition,

        "year": None,

        "country": country,

        "domain": domain,

        "subtopic": subtopic,

        "difficulty": None,

        "difficulty_source": "unknown",

        "concepts": concepts,

        "prerequisites": None,

        "solution_depth": None,

        "estimated_time_minutes": None,

        "proof_required": proof_required,

        "reasoning_intensity": None,

        "calculation_intensity": None,

        "major_steps": None,

        "problem_type": problem_type,

        "language": language,

        "data_type": "real",

        "problem_text": problem["problem_markdown"],

        "final_answer": problem["final_answer"],
    }

    records.append(record)


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(records)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 70)
print("CONVERSION COMPLETE")
print("=" * 70)

print(f"\nRows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\nSaved to:")
print(OUTPUT_PATH)

print("\nDomain distribution:")

print(
    df["domain"]
    .value_counts(dropna=False)
)

print("\nProblem type distribution:")

print(
    df["problem_type"]
    .value_counts(dropna=False)
)

print("\nMissing values:")

print(
    df.isna()
    .sum()
    .sort_values(ascending=False)
)

print("\nFirst converted problem:")

print(
    df.iloc[0].to_string()
)