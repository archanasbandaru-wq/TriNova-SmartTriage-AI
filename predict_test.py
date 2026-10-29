
import pickle
from pathlib import Path

import pandas as pd

from red_flags import detect_red_flags
from safety_rules import safety_check

BASE = Path(__file__).resolve().parent

print("Loading trained AI models...")

with open(BASE / "triage_level_model.pkl", "rb") as f:
    triage_model = pickle.load(f)

with open(BASE / "department_model.pkl", "rb") as f:
    department_model = pickle.load(f)

patients = pd.read_csv(BASE / "intake_test.csv")
departments = set(pd.read_csv(BASE / "departments.csv").iloc[:, 0].astype(str))
valid_flags = set(pd.read_csv(BASE / "red_flag_codes.csv").iloc[:, 0].astype(str))

def clean_text(value):
    return "" if pd.isna(value) else str(value)

def clean_number(value):
    number = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(number) else float(number)

def get_safety(row):
    return safety_check(
        age_years=clean_number(row.get("age_years")),
        spo2=clean_number(row.get("spo2_pct")),
        pulse=clean_number(row.get("pulse_bpm")),
        systolic=clean_number(row.get("bp_systolic")),
        diastolic=clean_number(row.get("bp_diastolic")),
        temperature=clean_number(row.get("temp_c")),
    )

def make_features(row):
    complaint = clean_text(row.get("chief_complaint"))
    conditions = clean_text(row.get("known_conditions"))
    medications = clean_text(row.get("current_medications"))

    return {
        "age_years": row.get("age_years"),
        "age_months": row.get("age_months"),
        "sex": clean_text(row.get("sex")) or "unknown",
        "pregnant": clean_text(row.get("pregnant")) or "unknown",
        "arrival_mode": clean_text(row.get("arrival_mode")) or "unknown",
        "chief_complaint": complaint,
        "medical_text": " ".join(
            text for text in [complaint, conditions, medications] if text
        ),
        "pulse_bpm": row.get("pulse_bpm"),
        "spo2_pct": row.get("spo2_pct"),
        "bp_systolic": row.get("bp_systolic"),
        "bp_diastolic": row.get("bp_diastolic"),
        "temp_c": row.get("temp_c"),
    }

features = pd.DataFrame(
    [make_features(row) for _, row in patients.iterrows()]
)

print("Predicting triage priorities...")
predicted_levels = triage_model.predict(features)

print("Predicting departments...")
predicted_departments = department_model.predict(features)

results = []

for i, (_, row) in enumerate(patients.iterrows()):
    complaint = clean_text(row.get("chief_complaint"))
    flags = [
        flag for flag in detect_red_flags(complaint)
        if flag in valid_flags
    ]

    safety = get_safety(row)

    level = int(predicted_levels[i])
    department = str(predicted_departments[i])

    # A smaller triage number means greater urgency.
    level = min(level, int(safety["minimum_urgency_level"]))

    # Any detected red flag requires emergency escalation.
    if flags:
        level = min(level, 2)
    complaint = str(row.get("chief_complaint", "")).strip().lower()
   
    complaint = str(row.get("chief_complaint", "")).strip().lower()
    missing_complaint = complaint in ("", "nan", "none", "null", "xx", "unknown", "na", "n/a")

    if safety["needs_nurse_review"] or missing_complaint:
        level = "ABSTAIN"
        department = ""
        confidence = ""
    else:
        if level in (1, 2):
            department = "Emergency/Casualty"

        if department not in departments:
            department = "General Medicine"

        confidence = 0.80

    results.append({
        "visit_id": row["visit_id"],
        "triage_level": level,
        "department": department,
        "red_flags": ";".join(flags),
        "confidence": confidence,
    })

           

submission = pd.DataFrame(results)
print("Total patients:", len(patients))
print("Total predictions:", len(submission))
print("Total predictions:", len(submission))
print("Missing predictions:", len(patients) - len(submission))
print("Total predictions:", len(submission))
print("Missing predictions:", len(patients) - len(submission))
assert len(submission) == len(patients)
assert submission["visit_id"].is_unique
assert submission["triage_level"].astype(str).isin(
    ["1", "2", "3", "4", "5", "ABSTAIN"]
).all()

output_dir = BASE / "submission"
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "H1_predictions.csv"
submission.to_csv(output_file, index=False)

print("\nSUCCESS!")
print("Total predictions:", len(submission))
print("Saved file:", output_file)
print("\nTriage distribution:")
print(submission["triage_level"].value_counts())
