# 🧠 Olympiad Intelligence

### An AI/ML Framework for Understanding Mathematical Olympiad Problems

**Olympiad Intelligence** is a research-oriented machine learning project designed to analyze mathematical olympiad problems, extract structural and linguistic features from their statements and solutions, estimate problem difficulty, and eventually develop intelligent systems for mathematical problem classification, difficulty prediction, and adaptive problem recommendation.

The long-term goal is to build an intelligent mathematical problem analysis system that can understand not only *what topic a problem belongs to*, but also *why it is difficult* and *what type of reasoning is required to solve it*.

---

## 🚀 Project Status

| Stage | Status |
|---|---|
| Project architecture | ✅ Complete |
| Initial dataset pipeline | ✅ Complete |
| Mathematical taxonomy | ✅ Complete |
| Feature engineering | ✅ Complete |
| Baseline difficulty model | ✅ Complete |
| MathNet integration | ✅ Complete |
| Solution feature extraction | ✅ Complete |
| Difficulty engine | ✅ Complete |
| ML difficulty prediction | 🔄 In Progress |
| Automated problem analysis | ⏳ Planned |
| Adaptive recommendation system | ⏳ Planned |
| Student skill profiling | ⏳ Planned |

**Current milestone: Day 4 — MathNet Integration & Difficulty Engine**

---

# 🎯 Motivation

Mathematical olympiad problems are fundamentally different from conventional educational exercises.

Two problems may belong to the same mathematical domain while requiring completely different levels of reasoning.

For example, difficulty can depend on:

- conceptual depth
- number of reasoning steps
- proof requirements
- case analysis
- algebraic manipulation
- solution length
- number of equations
- problem type
- mathematical domain
- interaction between multiple concepts

Traditional difficulty labels often fail to capture these differences.

This project explores whether these characteristics can be quantified and combined to create a computational model of olympiad problem difficulty.

---

# 🔬 Research Questions

The project investigates several questions:

1. Can mathematical olympiad problem difficulty be estimated from structural features?

2. Which characteristics of a problem are most strongly associated with difficulty?

3. How does solution structure correlate with problem complexity?

4. Can mathematical domains and problem types be used as predictive signals?

5. Can machine learning predict the difficulty of an unseen olympiad problem?

6. Can mathematical problems be automatically classified by domain and subtopic?

7. Can solution structure provide useful information about the reasoning required by a problem?

8. Can these models eventually support personalized olympiad training?

---

# 🏗️ Current Architecture

```text
                    ┌─────────────────────┐
                    │ Mathematical        │
                    │ Olympiad Problems    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Data Collection &    │
                    │ Standardization      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Mathematical        │
                    │ Taxonomy             │
                    │                      │
                    │ Algebra              │
                    │ Geometry             │
                    │ Number Theory       │
                    │ Combinatorics       │
                    │ etc.                │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Feature Engineering  │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ Problem Features │          │ Solution Features│
       └────────┬────────┘          └────────┬────────┘
                │                            │
                └──────────────┬─────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Difficulty Engine   │
                    └──────────┬──────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │ Easy │ Medium │ Hard │ Very Hard│
              └────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ ML Prediction Model │
                    │       (Next)         │
                    └─────────────────────┘