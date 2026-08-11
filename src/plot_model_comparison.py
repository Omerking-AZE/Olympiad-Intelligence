import pandas as pd
import matplotlib.pyplot as plt


print("=" * 70)
print("OLYMPIAD INTELLIGENCE - MODEL COMPARISON PLOT")
print("=" * 70)

df = pd.read_csv(
    "data/processed/model_comparison.csv"
)

print("\nModel results:")
print(df.to_string(index=False))

# MAE comparison
plt.figure(figsize=(9, 6))

plt.bar(
    df["model"],
    df["mae_mean"],
    yerr=df["mae_std"],
    capsize=5
)

plt.ylabel("Mean Absolute Error")
plt.xlabel("Model")
plt.title("Model Comparison - MAE")

plt.tight_layout()

output = "data/processed/model_comparison_mae.png"

plt.savefig(
    output,
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print(f"\nSaved: {output}")

# R2 comparison
plt.figure(figsize=(9, 6))

plt.bar(
    df["model"],
    df["r2_mean"],
    yerr=df["r2_std"],
    capsize=5
)

plt.ylabel("R²")
plt.xlabel("Model")
plt.title("Model Comparison - R²")

plt.tight_layout()

output = "data/processed/model_comparison_r2.png"

plt.savefig(
    output,
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {output}")

print("\nPlot generation complete.")