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
# DATASET SCHEMA
# ============================================================

print("\nAvailable dataset fields:")

try:
    print(dataset.column_names)
except Exception:
    print("Could not read dataset column names.")


# ============================================================
# SAMPLE
# ============================================================

sample_size = min(
    SAMPLE_SIZE,
    len(dataset)
)

print(
    f"\nSelecting first "
    f"{sample_size} problems..."
)

sample = dataset.select(
    range(sample_size)
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_get(problem, key, default=None):
    """
    Safely read a field from a MathNet record.

    MathNet v0 does not contain some richer metadata
    fields such as year/problem_number/section.
    """

    try:
        return problem.get(
            key,
            default
        )
    except AttributeError:
        try:
            return problem[key]
        except Exception:
            return default


def normalize_text(value):
    """
    Convert missing values to None and
    normalize empty strings.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def build_problem_title(
    competition,
    year=None,
    problem_number=None,
):
    """
    Build the user-facing problem title.

    Preferred format:

        IMO 2023 P2

    When year/problem number are unavailable,
    fall back to the competition name.
    """

    competition = normalize_text(
        competition
    )

    year = normalize_text(
        year
    )

    problem_number = normalize_text(
        problem_number
    )

    if (
        competition
        and year
        and problem_number
    ):
        return (
            f"{competition} "
            f"{year} "
            f"P{problem_number}"
        )

    if competition and problem_number:
        return (
            f"{competition} "
            f"P{problem_number}"
        )

    if competition and year:
        return (
            f"{competition} "
            f"{year}"
        )

    if competition:
        return competition

    return "Olympiad Problem"


def flatten_topics(topics):
    """
    Convert MathNet hierarchical topics
    into domain/subtopic/concept fields.
    """

    if not topics:
        return (
            None,
            None,
            None,
        )

    parsed_topics = []

    for topic in topics:

        if not topic:
            continue

        parts = [
            part.strip()
            for part in str(topic).split(">")
            if part.strip()
        ]

        if parts:
            parsed_topics.append(
                parts
            )

    if not parsed_topics:
        return (
            None,
            None,
            None,
        )

    # --------------------------------------------------------
    # Domains
    # --------------------------------------------------------

    domains = sorted({
        parts[0]
        for parts in parsed_topics
        if len(parts) >= 1
    })

    domain = (
        " | ".join(domains)
        if domains
        else None
    )

    # --------------------------------------------------------
    # Subtopics
    # --------------------------------------------------------

    subtopics = sorted({
        parts[1]
        for parts in parsed_topics
        if len(parts) >= 2
    })

    subtopic = (
        " | ".join(subtopics)
        if subtopics
        else None
    )

    # --------------------------------------------------------
    # Concepts
    # --------------------------------------------------------

    concept_list = []

    for parts in parsed_topics:

        if len(parts) >= 3:

            concept = (
                " > ".join(parts[2:])
            )

            if (
                concept
                and concept not in concept_list
            ):
                concept_list.append(
                    concept
                )

    concepts = (
        " | ".join(concept_list)
        if concept_list
        else None
    )

    return (
        domain,
        subtopic,
        concepts,
    )


def calculate_proof_required(
    problem_type
):
    """
    Infer whether a written proof is required
    from the MathNet problem type annotation.
    """

    if problem_type is None:
        return None

    normalized = str(
        problem_type
    ).strip().lower()

    if normalized in {
        "proof and answer",
        "proof only",
    }:
        return True

    if normalized in {
        "final answer only",
        "answer only",
        "mcq",
    }:
        return False

    return None


# ============================================================
# CONVERSION
# ============================================================

records = []


for index, problem in enumerate(sample):

    # --------------------------------------------------------
    # Basic metadata
    # --------------------------------------------------------

    problem_id = normalize_text(
        safe_get(
            problem,
            "id"
        )
    )

    country = normalize_text(
        safe_get(
            problem,
            "country"
        )
    )

    competition = normalize_text(
        safe_get(
            problem,
            "competition"
        )
    )

    # These are available in richer MathNet releases,
    # but are absent from the current v0 dataset.
    year = normalize_text(
        safe_get(
            problem,
            "year"
        )
    )

    problem_number = normalize_text(
        safe_get(
            problem,
            "problem_number"
        )
    )

    section = normalize_text(
        safe_get(
            problem,
            "section"
        )
    )

    language = normalize_text(
        safe_get(
            problem,
            "language"
        )
    )

    problem_type = normalize_text(
        safe_get(
            problem,
            "problem_type"
        )
    )

    source_booklet = normalize_text(
        safe_get(
            problem,
            "source_booklet"
        )
    )

    booklet_source = normalize_text(
        safe_get(
            problem,
            "booklet_source"
        )
    )

    # --------------------------------------------------------
    # User-facing problem title
    # --------------------------------------------------------

    problem_title = build_problem_title(
        competition=competition,
        year=year,
        problem_number=problem_number,
    )

    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    topics = safe_get(
        problem,
        "topics_flat",
        []
    )

    (
        domain,
        subtopic,
        concepts,
    ) = flatten_topics(
        topics
    )

    # --------------------------------------------------------
    # Proof requirement
    # --------------------------------------------------------

    proof_required = (
        calculate_proof_required(
            problem_type
        )
    )

    # --------------------------------------------------------
    # Problem text
    # --------------------------------------------------------

    problem_text = normalize_text(
        safe_get(
            problem,
            "problem_markdown"
        )
    )

    # --------------------------------------------------------
    # Final answer
    # --------------------------------------------------------

    final_answer = normalize_text(
        safe_get(
            problem,
            "final_answer"
        )
    )

    # --------------------------------------------------------
    # Create record
    # --------------------------------------------------------

    record = {

        # Internal stable identifier
        "problem_id":
            f"MATHNET-{problem_id}",

        # Dataset source
        "source":
            "MathNet",

        # Original metadata
        "competition":
            competition,

        "year":
            year,

        "problem_number":
            problem_number,

        "section":
            section,

        "country":
            country,

        "source_booklet":
            source_booklet,

        "booklet_source":
            booklet_source,

        # User-facing title
        "problem_title":
            problem_title,

        # Mathematical taxonomy
        "domain":
            domain,

        "subtopic":
            subtopic,

        "concepts":
            concepts,

        # Difficulty fields are filled later
        # by the difficulty engine.
        "difficulty":
            None,

        "difficulty_source":
            "unknown",

        # Existing / future feature fields
        "prerequisites":
            None,

        "solution_depth":
            None,

        "estimated_time_minutes":
            None,

        "proof_required":
            proof_required,

        "reasoning_intensity":
            None,

        "calculation_intensity":
            None,

        "major_steps":
            None,

        # Problem classification
        "problem_type":
            problem_type,

        "language":
            language,

        "data_type":
            "real",

        # Actual problem content
        "problem_text":
            problem_text,

        "final_answer":
            final_answer,
    }

    records.append(
        record
    )


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(
    records
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

Path(
    "data/processed"
).mkdir(
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

print(
    "\n"
    + "=" * 70
)

print(
    "CONVERSION COMPLETE"
)

print(
    "=" * 70
)

print(
    f"\nRows: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)

print(
    "\nSaved to:"
)

print(
    OUTPUT_PATH
)


print(
    "\nMetadata coverage:"
)

print(
    f"Year available: "
    f"{df['year'].notna().sum()} / {len(df)}"
)

print(
    f"Problem number available: "
    f"{df['problem_number'].notna().sum()} / {len(df)}"
)

print(
    f"Section available: "
    f"{df['section'].notna().sum()} / {len(df)}"
)


print(
    "\nDomain distribution:"
)

print(
    df["domain"]
    .value_counts(
        dropna=False
    )
)


print(
    "\nProblem type distribution:"
)

print(
    df["problem_type"]
    .value_counts(
        dropna=False
    )
)


print(
    "\nCompetition distribution:"
)

print(
    df["competition"]
    .value_counts(
        dropna=False
    ).head(20)
)


print(
    "\nMissing values:"
)

print(
    df.isna()
    .sum()
    .sort_values(
        ascending=False
    )
)


print(
    "\nFirst converted problem:"
)

print(
    df.iloc[0].to_string()
)


print(
    "\nFirst problem title:"
)

print(
    df.iloc[0]["problem_title"]
)


print(
    "\n"
    + "=" * 70
)