from datasets import load_dataset


print("=" * 60)
print("MATHNET DATASET STRUCTURE")
print("=" * 60)

dataset = load_dataset(
    "ShadenA/MathNet",
    split="train",
)

print(f"\nTotal problems: {len(dataset)}")

print("\nColumns:")
for column in dataset.column_names:
    print(f"  - {column}")

print("\n" + "=" * 60)
print("DATASET STATISTICS")
print("=" * 60)

# Countries
countries = dataset.unique("country")

print(f"\nCountries: {len(countries)}")
print("First 20 countries:")

for country in countries[:20]:
    print(f"  - {country}")

# Competitions
competitions = dataset.unique("competition")

print(f"\nCompetitions: {len(competitions)}")
print("First 20 competitions:")

for competition in competitions[:20]:
    print(f"  - {competition}")

# Languages
languages = dataset.unique("language")

print(f"\nLanguages: {len(languages)}")
print(languages)

# Problem types
problem_types = dataset.unique("problem_type")

print(f"\nProblem types: {len(problem_types)}")

for problem_type in problem_types:
    print(f"  - {problem_type}")

# Topics
print("\n" + "=" * 60)
print("TOPIC ANALYSIS")
print("=" * 60)

unique_topics = set()

for row in dataset:
    topics = row["topics_flat"]

    if topics:
        for topic in topics:
            unique_topics.add(topic)

print(f"\nUnique topic paths: {len(unique_topics)}")

print("\nFirst 30 topic paths:")

for topic in sorted(unique_topics)[:30]:
    print(f"  - {topic}")

# First problem
print("\n" + "=" * 60)
print("FIRST PROBLEM")
print("=" * 60)

problem = dataset[0]

print(f"\nID: {problem['id']}")
print(f"Country: {problem['country']}")
print(f"Competition: {problem['competition']}")
print(f"Language: {problem['language']}")
print(f"Problem type: {problem['problem_type']}")

print("\nTopics:")

for topic in problem["topics_flat"]:
    print(f"  - {topic}")

print("\nProblem text:")
print(problem["problem_markdown"][:1500])

print("\nFinal answer:")
print(problem["final_answer"])