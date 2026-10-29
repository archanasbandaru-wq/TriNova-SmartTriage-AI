
"""Prototype-only triage orchestration. Not for clinical use."""

from red_flags import detect_red_flags
from safety_rules import safety_check
from input_validation import validate_patient


def assess_case(
    *,
    patient_id,
    age,
    complaint,
    pulse,
    spo2,
    systolic,
    diastolic,
    temperature,
    patient_frame=None,
    triage_model=None,
    department_model=None,
):
    """Never suppress emergency indicators when prediction is unavailable."""

    flags = detect_red_flags(complaint)

    safety = safety_check(
        age_years=age,
        spo2=spo2,
        pulse=pulse,
        systolic=systolic,
        diastolic=diastolic,
        temperature=temperature,
    )

    validation = validate_patient(
        age,
        complaint,
        pulse,
        spo2,
        systolic,
        diastolic,
        temperature,
    )

    emergency = bool(flags) or safety["minimum_urgency_level"] <= 2

    reasons = list(validation.errors) + list(validation.warnings)

    if not str(patient_id or "").strip():
        reasons.insert(0, "Patient / Visit ID is required.")

    result = dict(
        priority="ABSTAIN",
        department="Unassigned — nurse assessment",
        red_flags=flags,
        safety=safety,
        emergency=emergency,
        reasons=reasons,
        needs_nurse_review=True,
        status=(
            "Immediate review"
            if emergency
            else "Nurse review required"
        ),
    )

    if reasons:
        return result

    try:
        if (
            patient_frame is None
            or triage_model is None
            or department_model is None
        ):
            raise ValueError("Prediction inputs or models unavailable")

        predicted = int(triage_model.predict(patient_frame)[0])

        if predicted not in (1, 2, 3, 4, 5):
            raise ValueError("Model returned an invalid triage level")

        department = str(department_model.predict(patient_frame)[0])

        if not department.strip():
            raise ValueError("Model returned an empty department")

        final_level = min(
            predicted,
            int(safety["minimum_urgency_level"]),
        )

        if flags:
            final_level = min(final_level, 2)

        if final_level <= 2:
            department = "Emergency/Casualty"

        result.update(
            priority=f"Level {final_level}",
            department=department,
            needs_nurse_review=True,
            status=(
                "Immediate review"
                if final_level <= 2
                else "Nurse review required"
            ),
        )

    except Exception:
        result["reasons"] = [
            "AI prediction or preprocessing failed; "
            "qualified staff review required."
        ]

    return result
