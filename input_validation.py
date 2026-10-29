
import math
from dataclasses import dataclass, field

# Configurable prototype limits.
# These are demonstration assumptions, not clinical standards.
LIMITS = {
    "age": (0, 120),
    "temperature_c": (30.0, 45.0),
    "spo2": (50, 100),
    "pulse": (30, 220),
    "systolic": (60, 250),
    "diastolic": (30, 150),
}

# Values inside the valid range that need verification.
VERIFY_RANGES = {
    "temperature_c": (35.0, 40.0),
    "spo2": (90, 100),
    "pulse": (50, 130),
    "systolic": (90, 180),
    "diastolic": (60, 120),
}


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def can_predict(self):
        return not self.errors and not self.warnings


def check_number(name, value, minimum, maximum):
    if value is None or isinstance(value, bool):
        return f"{name}: value is missing or invalid."

    if isinstance(value, str) and not value.strip():
        return f"{name}: value is missing."

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return f"{name}: enter a numeric value."

    if not math.isfinite(number):
        return f"{name}: NaN or infinity is not allowed."

    if number < minimum or number > maximum:
        return (
            f"{name}: enter a value between "
            f"{minimum} and {maximum}."
        )

    return None


def validate_patient(
    age,
    complaint,
    pulse,
    spo2,
    systolic,
    diastolic,
    temperature,
):
    result = ValidationResult()

    values = {
        "age": age,
        "pulse": pulse,
        "spo2": spo2,
        "systolic": systolic,
        "diastolic": diastolic,
        "temperature_c": temperature,
    }

    for name, value in values.items():
        minimum, maximum = LIMITS[name]
        error = check_number(name, value, minimum, maximum)

        if error:
            result.errors.append(error)
            continue

        number = float(value)

        if name == "age" and not number.is_integer():
            result.errors.append("age: enter a whole number.")
            continue

        if name in VERIFY_RANGES:
            low, high = VERIFY_RANGES[name]

            if number < low or number > high:
                result.warnings.append(
                    f"{name}: unusual reading. "
                    "Verify the measurement before prediction."
                )

    if not isinstance(complaint, str) or not complaint.strip():
        result.errors.append(
            "chief_complaint: enter the patient's main symptom."
        )

    # Basic consistency check.
    if (
        "systolic" not in values_with_errors(result)
        and "diastolic" not in values_with_errors(result)
    ):
        if float(systolic) <= float(diastolic):
            result.errors.append(
                "blood_pressure: systolic must be greater "
                "than diastolic. Verify both readings."
            )

    return result


def values_with_errors(result):
    return {
        message.split(":", 1)[0]
        for message in result.errors
    }
