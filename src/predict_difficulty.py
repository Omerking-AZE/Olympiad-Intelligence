import pandas as pd
import joblib


MODEL_PATH = (
    "data/processed/"
    "best_difficulty_model.joblib"
)

FEATURES = [
    "length_score",
    "equation_score",
    "reasoning_score",
    "proof_score",
    "case_score",
    "steps_score",
    "problem_type_score",
    "domain_score",
]


def predict_difficulty(feature_values):

    model = joblib.load(MODEL_PATH)

    X = pd.DataFrame(
        [feature_values],
        columns=FEATURES
    )

    prediction = model.predict(X)[0]

    return prediction


if __name__ == "__main__":

    print("=" * 70)
    print("OLYMPIAD INTELLIGENCE - DIFFICULTY PREDICTION")
    print("=" * 70)

    # Example feature vector
    example = [
        60,  # length_score
        55,  # equation_score
        70,  # reasoning_score
        65,  # proof_score
        40,  # case_score
        60,  # steps_score
        50,  # problem_type_score
        55,  # domain_score
    ]

    prediction = predict_difficulty(example)

    print(f"\nPredicted difficulty score: {prediction:.2f}")