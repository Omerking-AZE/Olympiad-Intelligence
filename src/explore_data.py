import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/problems.csv")

print("Average difficulty:")
print(df["difficulty"].mean())

print("\nAverage solving time:")
print(df["estimated_time_minutes"].mean())

print("\nProblems by domain:")
print(df["domain"].value_counts())

# Domain distribution
df["domain"].value_counts().plot(kind="bar")

plt.title("Problems by Mathematical Domain")
plt.xlabel("Domain")
plt.ylabel("Number of Problems")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()