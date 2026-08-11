import pandas as pd
import numpy as np

from sklearn.model_selection import KFold, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


print("=" * 70)
print("OLYMPIAD INTELLIGENCE - MODEL COMPARISON")
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

models = {
    "Linear Regression": make_pipeline(
        StandardScaler(),
        LinearRegression()
    ),

    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    ),
}

kf = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

results = []

print("\nEvaluating models...\n")

for name, model in models.items():

    print(f"Training: {name}")

    mae_scores = -cross_val_score(
        model,
        X,
        y,
        cv=kf,
        scoring="neg_mean_absolute_error",
        n_jobs=-1
    )

    mse_scores = -cross_val_score(
        model,
        X,
        y,
        cv=kf,
        scoring="neg_mean_squared_error",
        n_jobs=-1
    )

    r2_scores = cross_val_score(
        model,
        X,
        y,
        cv=kf,
        scoring="r2",
        n_jobs=-1
    )

    rmse_scores = np.sqrt(mse_scores)

    results.append({
        "model": name,
        "mae_mean": mae_scores.mean(),
        "mae_std": mae_scores.std(),
        "rmse_mean": rmse_scores.mean(),
        "rmse_std": rmse_scores.std(),
        "r2_mean": r2_scores.mean(),
        "r2_std": r2_scores.std(),
    })

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "mae_mean"
)

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

output = "data/processed/model_comparison.csv"

results_df.to_csv(
    output,
    index=False
)

print(f"\nSaved:")
print(output)

best_model = results_df.iloc[0]

print("\n" + "=" * 70)
print("BEST MODEL")
print("=" * 70)

print(f"Model: {best_model['model']}")
print(f"MAE:   {best_model['mae_mean']:.4f}")
print(f"RMSE:  {best_model['rmse_mean']:.4f}")
print(f"R²:    {best_model['r2_mean']:.4f}")

print("\n" + "=" * 70)
print("MODEL COMPARISON COMPLETE")
print("=" * 70)