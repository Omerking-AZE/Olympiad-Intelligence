# Olympiad Intelligence — Day 7 Model Analysis

## Dataset

Prediction samples: 200
Features: 8

## Model Performance

- Mean Error: 0.0783
- MAE: 1.7260
- Maximum Absolute Error: 10.4265

## Error Groups

- Low error (<=2): 131
- Moderate error (2-5): 63
- High error (5-10): 5
- Very high error (>10): 1

## Feature/Error Correlations

- equation_score: 0.3325
- length_score: 0.2946
- reasoning_score: 0.2228
- case_score: 0.2225
- steps_score: 0.2175
- proof_score: 0.1744
- problem_type_score: 0.0608
- domain_score: 0.0242

## Interpretation

The model is evaluated against the engineered difficulty score produced by the current difficulty methodology.
This analysis measures the model's ability to reproduce the existing difficulty-engine score.
It does not establish agreement with human olympiad experts or official competition difficulty ratings.