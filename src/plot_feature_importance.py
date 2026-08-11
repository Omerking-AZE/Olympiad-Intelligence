import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor


print("=" * 70)
print("OLYMPIAD INTELLIGENCE - FEATURE IMPORTANCE")
print("=" * 70)

df = pd.read_csv(
    "data/processed/mathnet_difficulty.csv"
)

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

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=True
)

print("\nFeature importance:")
print(
    importance.sort_values(
        "importance",
        ascending=False
    ).to_string(index=False)
)

plt.figure(figsize=(10, 6))

plt.barh(
    importance["feature"],
    importance["importance"]
)

plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Difficulty Model Feature Importance")

plt.tight_layout()

output = "data/processed/feature_importance.png"

plt.savefig(
    output,
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print(f"\nSaved: {output}")