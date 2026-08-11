# Data Dictionary

## Problem Identification

| Feature | Description |
|---|---|
| problem_id | Unique identifier |
| source | Dataset or competition source |
| year | Competition year |
| country | Country associated with competition |
| competition | Competition name |

## Mathematical Features

| Feature | Description |
|---|---|
| domain | Main mathematical domain |
| subtopic | More specific mathematical topic |
| concepts | Main mathematical concepts |
| prerequisites | Required prior knowledge |

## Difficulty Features

| Feature | Description |
|---|---|
| difficulty | Existing/provisional difficulty label |
| solution_depth | Estimated number of major reasoning stages |
| estimated_time_minutes | Estimated solving time |
| proof_required | Whether proof is required |
| reasoning_intensity | Reasoning complexity |
| calculation_intensity | Computational complexity |
| major_steps | Number of major solution stages |

## Future Student Features

| Feature | Description |
|---|---|
| student_id | Anonymous student identifier |
| attempts | Number of attempts |
| solved | Whether problem was solved |
| time_minutes | Time spent |
| hints | Number of hints |
| error_type | Type of observed error |

## Important Note

Existing difficulty labels are not treated as ground truth.

Future experiments will investigate empirical difficulty using student performance data.