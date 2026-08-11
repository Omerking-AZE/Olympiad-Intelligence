import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


print("=" * 70)
print("OLYMPIAD INTELLIGENCE - BEST MODEL TRAINING")
print("=" * 70)

DATA_PATH = "data/processed/mathnet_difficulty.csv"
COMPARISON_PATH = "data/processed/model_comparison.csv"

df = pd.read_csv(DATA_PATH)
comparison = pd.read_csv(COMPARISON_PATH)

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

X = df[features].fillna(0)
y = df["difficulty_score"].fillna(
    df["difficulty_score"].median()
)

# Select best model using lowest MAE
best_name = comparison.sort_values(
    "mae_mean"
).iloc[0]["model"]

print(f"\nSelected model: {best_name}")

if best_name == "Linear Regression":

    model = make_pipeline(
        StandardScaler(),
        LinearRegression()
    )

elif best_name == "Random Forest":

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    )

elif best_name == "Gradient Boosting":

    model = GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )

else:
    raise ValueError(
        f"Unknown model: {best_name}"
    )

print("\nTraining best model on full dataset...")

model.fit(X, y)

output = "data/processed/best_difficulty_model.joblib"

joblib.dump(
    model,
    output
)

print(f"\nSaved:")
print(output)

print("\n" + "=" * 70)
print("BEST MODEL TRAINING COMPLETE")
print("=" * 70)