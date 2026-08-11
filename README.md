# Olympiad Intelligence

**Olympiad Intelligence** is a research project focused on understanding, modeling, and analyzing the difficulty of mathematical olympiad problems using data science and machine learning.

The project combines mathematical problem metadata, solution structure, reasoning patterns, and mathematical domains to build a data-driven framework for olympiad problem analysis.

## Research Goals

The main goals of Olympiad Intelligence are:

- Analyze structural characteristics of olympiad problems
- Extract meaningful features from mathematical solutions
- Develop a data-driven difficulty scoring system
- Study relationships between problem domains and difficulty
- Investigate reasoning, proof, calculation, and case-analysis patterns
- Build a foundation for future machine-learning models for olympiad mathematics

## Dataset

The current research pipeline uses the **MathNet** dataset.

MathNet contains **27,817 mathematical olympiad problems** from competitions and countries around the world.

For the current development stage, the project uses a **1,000-problem working sample**.

The dataset contains information such as:

- Problem statements
- Solutions
- Country
- Competition
- Mathematical topics
- Mathematical domains
- Problem type
- Language
- Final answers when available

## Data Processing Pipeline

The current pipeline consists of several stages:

```text
MathNet Dataset
      ↓
Dataset Conversion
      ↓
Problem Feature Engineering
      ↓
Solution Feature Extraction
      ↓
Solution Feature Analysis
      ↓
Difficulty Signal Engineering
      ↓
Difficulty Engine
      ↓
Machine Learning Research

Solution Analysis

The project extracts structural features from mathematical solutions, including:

Solution length
Number of words
Number of paragraphs
Equation count
Reasoning indicators
Proof indicators
Case analysis
Calculation indicators
Major solution steps
Equation density
Reasoning density
Proof density

In the current 1,000-problem sample:

884 problems have available solutions
116 problems do not have available solutions
Solution availability: 88.4%
Difficulty Engine

The current difficulty engine combines multiple signals instead of relying on a single measurement.

The model currently considers:

Solution complexity
Equation usage
Reasoning patterns
Proof structure
Case analysis
Major solution steps
Problem type
Mathematical domain

The engine produces:

A continuous difficulty_score
A numerical difficulty level
A difficulty label

Current labels:

Easy
Medium
Hard
Very Hard

These labels represent the project's current research methodology and are not official olympiad difficulty ratings.

Current Dataset Distribution

The current 1,000-problem working dataset contains problems from several major mathematical domains, including:

Geometry
Algebra
Discrete Mathematics
Number Theory
Statistics
Precalculus
Calculus
Mathematical Word Problems

Problem types include:

Proof and answer
Proof only
Final answer only
Multiple choice

Repository Structure
Olympiad-Intelligence/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
│
├── src/
│   ├── feature_engineering.py
│   ├── inspect_mathnet.py
│   ├── convert_mathnet.py
│   ├── extract_solution_features.py
│   ├── analyze_solution_features.py
│   └── ...
│
├── README.md
└── requirements.txt

Current Research Stage

The project has currently completed:

Initial project structure
Mathematical taxonomy
Initial dataset pipeline
Problem feature engineering
Baseline difficulty modeling
MathNet dataset integration
MathNet dataset conversion
Solution feature extraction
Solution feature analysis
Difficulty signal engineering
Initial multi-signal difficulty engine
Future Development

Planned research directions include:

Expanding the dataset beyond the current 1,000-problem sample
Improving difficulty estimation
Training machine-learning models
Comparing different model architectures
Evaluating predictions against human difficulty assessments
Developing mathematical-topic embeddings
Building problem similarity and recommendation systems
Creating an interactive olympiad problem analysis system
Studying which reasoning patterns are associated with higher difficulty
Research Philosophy

Olympiad Intelligence is intended as a research project rather than simply a collection of solved problems.

The long-term objective is to investigate whether mathematical problem difficulty can be modeled through measurable structural and reasoning characteristics while preserving the complexity of olympiad mathematics.

Status

Active Research Project

The methodology, features, datasets, and models are continuously being developed and evaluated.


# data/README.md

```markdown
# Data

This directory contains the datasets and processed data used by **Olympiad Intelligence**.

## Dataset Source

The main external dataset used by the project is **MathNet**.

MathNet contains approximately **27,817 mathematical olympiad problems**.

The current development pipeline uses a **1,000-problem working sample**.

## Dataset Information

The converted MathNet dataset contains information including:

- Problem ID
- Problem statement
- Solution information
- Country
- Competition
- Year when available
- Mathematical domain
- Subtopic
- Mathematical concepts
- Prerequisites when available
- Problem type
- Language
- Final answer when available
- Proof requirement

## Processed Files

### `features.csv`

Initial problem-level feature dataset used during the early feature-engineering stage.

### `mathnet_problems.csv`

Standardized 1,000-problem working dataset converted from MathNet.

### `mathnet_features.csv`

Dataset containing extracted structural features from MathNet problems and their solutions.

### `mathnet_model_features.csv`

Model-oriented feature dataset prepared for machine-learning experiments.

### `mathnet_difficulty.csv`

Output generated by the current difficulty engine.

It contains:

- Component difficulty signals
- `difficulty_score`
- Numerical difficulty
- `difficulty_label`

Current difficulty labels:

- Easy
- Medium
- Hard
- Very Hard

These labels are generated by the project's methodology and are not official olympiad difficulty ratings.

### `solution_feature_report.txt`

Statistical report describing the extracted solution features.

It includes:

- Missing-value analysis
- Zero-value analysis
- Variance
- Unique values
- Correlations
- Distribution statistics
- Feature relationships

## Solution Coverage

For the current 1,000-problem sample:

- Problems with solutions: **884**
- Problems without solutions: **116**
- Solution availability: **88.4%**

## Extracted Solution Features

The solution-analysis pipeline currently extracts:

- `solution_length`
- `solution_words`
- `solution_paragraphs`
- `equation_count`
- `reasoning_indicators`
- `proof_indicators`
- `case_analysis`
- `calculation_indicators`
- `solution_major_steps`
- `equation_density`
- `reasoning_density`
- `proof_density`
- `log_solution_length`
- `log_equation_count`

## Difficulty Features

The difficulty engine uses multiple signals, including:

- `length_score`
- `equation_score`
- `reasoning_score`
- `proof_score`
- `case_score`
- `steps_score`
- `problem_type_score`
- `domain_score`
- `difficulty_score`
- `difficulty`
- `difficulty_label`

## Data Quality

Some fields in MathNet are naturally missing.

Examples include:

- Year
- Final answer
- Language
- Solution information
- Certain problem metadata

Missing values are retained and handled by the processing pipeline.

Processed datasets are research artifacts and may change as the project's methodology and models improve.

## Reproducibility

The processed datasets in this directory are generated through scripts in the `src/` directory.

The intended workflow is:

```text
Raw Dataset
    ↓
Conversion
    ↓
Feature Extraction
    ↓
Feature Analysis
    ↓
Difficulty Engineering
    ↓
Machine Learning