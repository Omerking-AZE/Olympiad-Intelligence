import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("data/processed/features.csv")

features = [
    "solution_depth",
    "estimated_time_minutes",
    "proof_required",
    "reasoning_intensity",
    "calculation_intensity",
    "major_steps",
]

X = df[features]
y = df["difficulty"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)

print("=" * 50)
print("BASELINE DIFFICULTY MODEL")
print("=" * 50)

print(f"MAE: {mae:.3f}")