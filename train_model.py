
import pickle
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE = Path(__file__).resolve().parent

print("Loading patient training data...")

patients = pd.read_csv(BASE / "intake_train.csv")
labels = pd.read_csv(BASE / "train_labels.csv")

data = patients.merge(
    labels[["visit_id", "triage_level", "department"]],
    on="visit_id",
    how="inner",
    validate="one_to_one"
)

print("Matched training records:", len(data))

if len(data) != len(patients):
    raise ValueError("Some patient records have no matching labels.")

numeric = [
    "age_years", "age_months", "bp_systolic",
    "bp_diastolic", "pulse_bpm", "temp_c", "spo2_pct"
]

categorical = ["sex", "pregnant", "arrival_mode"]

text_columns = [
    "chief_complaint", "known_conditions", "current_medications"
]

for col in numeric:
    data[col] = pd.to_numeric(data[col], errors="coerce")
    data.loc[~data[col].between(-1, 300), col] = float("nan")

for col in categorical + text_columns:
    data[col] = data[col].fillna("").astype(str)

data["medical_text"] = (
    data[text_columns].agg(" ".join, axis=1).str.strip()
)

features = numeric + categorical + ["medical_text"]
X = data[features]

preprocessor = ColumnTransformer([
    ("text", TfidfVectorizer(
        max_features=12000,
        ngram_range=(1, 2),
        sublinear_tf=True
    ), "medical_text"),
    ("numbers", Pipeline([
        ("fill", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ]), numeric),
    ("categories", OneHotEncoder(
        handle_unknown="ignore"
    ), categorical)
])

def train_target(target):
    print("\nTraining model for:", target)

    y = data[target].astype(str)

    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=42,
        stratify=y
    )

    model = Pipeline([
        ("features", preprocessor),
        ("classifier", LogisticRegression(
            max_iter=500,
            class_weight="balanced"
        ))
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_valid)

    print(classification_report(
        y_valid, predictions, zero_division=0
    ))

    model.fit(X, y)

    filename = BASE / f"{target}_model.pkl"

    with open(filename, "wb") as f:
        pickle.dump(model, f)

    print("Saved model:", filename.name)

train_target("triage_level")
train_target("department")

print("\nTraining complete!")
print("Next: add mandatory emergency safety rules.")
