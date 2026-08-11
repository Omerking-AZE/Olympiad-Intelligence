import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("=" * 70)
print("OLYMPIAD INTELLIGENCE - DIFFICULTY ML MODEL")
print("=" * 70)

# Load dataset
DATA_PATH = "data/processed/mathnet_difficulty.csv"

df = pd.read_csv(DATA_PATH)

print(f"\nLoaded {len(df)} problems.")
print(f"Total columns: {len(df.columns)}")

# Features used by the model
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

# Check required columns
missing = [column for column in features + [target] if column not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

# Prepare X and y
X = df[features].copy()
y = df[target].copy()

# Handle missing values
X = X.fillna(0)
y = y.fillna(y.median())

print("\nFeatures:")
for feature in features:
    print(f"  - {feature}")

print(f"\nTarget: {target}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nDataset split:")
print(f"  Training samples: {len(X_train)}")
print(f"  Testing samples:  {len(X_test)}")

# Model
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

print("\nTraining Random Forest...")
model.fit(X_train, y_train)

joblib.dump(
    model,
    "data/processed/difficulty_model.joblib"
)

print("Saved:")
print("data/processed/difficulty_model.joblib")

# Predictions
predictions = model.predict(X_test)

# Evaluation
mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(y_test, predictions) ** 0.5
r2 = r2_score(y_test, predictions)

print("\n" + "=" * 70)
print("MODEL RESULTS")
print("=" * 70)

print(f"MAE:  {mae:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"R²:   {r2:.3f}")

# Feature importance
importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

print("\nFeature Importance:")
print(importance.to_string(index=False))

# Save predictions
results = X_test.copy()
results["actual_difficulty"] = y_test.values
results["predicted_difficulty"] = predictions
results["absolute_error"] = (
    results["actual_difficulty"] -
    results["predicted_difficulty"]
).abs()

results.to_csv(
    "data/processed/difficulty_predictions.csv",
    index=False
)

print("\nSaved:")
print("data/processed/difficulty_predictions.csv")

print("\n" + "=" * 70)
print("DAY 5 - STEP 1 COMPLETE")
print("=" * 70)