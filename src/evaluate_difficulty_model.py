import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


print("=" * 70)
print("OLYMPIAD INTELLIGENCE - MODEL VALIDATION")
print("=" * 70)

DATA_PATH = "data/processed/mathnet_difficulty.csv"

df = pd.read_csv(DATA_PATH)

features = [
    "length_score",
    "equation_score",
    "reasoning_score",
    "proof_score",
    "case_score",
    "steps_score",
    "problem_type_score",
    "domain_score",
]

target = "difficulty_score"

X = df[features].fillna(0)
y = df[target].fillna(df[target].median())

print(f"\nLoaded {len(df)} problems.")

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

kf = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

print("\nRunning 5-fold cross-validation...")

mae_scores = -cross_val_score(
    model,
    X,
    y,
    cv=kf,
    scoring="neg_mean_absolute_error",
    n_jobs=-1
)

rmse_scores = np.sqrt(
    -cross_val_score(
        model,
        X,
        y,
        cv=kf,
        scoring="neg_mean_squared_error",
        n_jobs=-1
    )
)

r2_scores = cross_val_score(
    model,
    X,
    y,
    cv=kf,
    scoring="r2",
    n_jobs=-1
)

print("\nCross-validation results:")

for i in range(5):
    print(
        f"Fold {i + 1}: "
        f"MAE={mae_scores[i]:.3f}, "
        f"RMSE={rmse_scores[i]:.3f}, "
        f"R²={r2_scores[i]:.3f}"
    )

print("\n" + "=" * 70)
print("AVERAGE RESULTS")
print("=" * 70)

print(f"MAE:  {mae_scores.mean():.3f} ± {mae_scores.std():.3f}")
print(f"RMSE: {rmse_scores.mean():.3f} ± {rmse_scores.std():.3f}")
print(f"R²:   {r2_scores.mean():.3f} ± {r2_scores.std():.3f}")

print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)