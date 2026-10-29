
# SmartTriage AI — Hackathon emergency safety rules
# Synthetic-data demonstration only. Not for clinical use.

import math


def number(value):
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None


def safety_check(
    age_years,
    age_months=None,
    spo2=None,
    pulse=None,
    systolic=None,
    diastolic=None,
    temperature=None,
    pregnant=False,
):
    """Return minimum urgency level, reasons, and review status."""

    reasons = []
    review = False
    level = 5

    age = number(age_years)
    months = number(age_months)

    if months is None and age is not None:
        months = age * 12

    if age is None or age < 0 or age > 120:
        review = True
        reasons.append("Age missing or implausible")

    def escalate(target, message):
        nonlocal level
        level = min(level, target)
        reasons.append(message)

    def check_vital(value, name, low, high):
        nonlocal review
        n = number(value)
        if n is None or n == 0:
            return None
        if not low <= n <= high:
            review = True
            reasons.append(f"{name}: implausible value, nurse review")
            return None
        return n

    oxygen = check_vital(spo2, "SpO2", 50, 100)
    heart = check_vital(pulse, "Pulse", 25, 250)
    sbp = check_vital(systolic, "Systolic BP", 20, 260)
    dbp = check_vital(diastolic, "Diastolic BP", 20, 180)

    temp = number(temperature)
    if temp is not None and temp != 0:
        if 86 <= temp <= 113:
            temp = (temp - 32) * 5 / 9
            reasons.append("Temperature converted from Fahrenheit")
        elif not 30 <= temp <= 45:
            temp = None
            review = True
            reasons.append("Temperature implausible, nurse review")
    else:
        temp = None

    if oxygen is not None:
        if oxygen < 85:
            escalate(1, "SpO2 below 85%")
        elif oxygen < 92:
            escalate(2, "SpO2 below 92%")
        elif oxygen < 94:
            escalate(3, "SpO2 92–93%")

    if temp is not None:
        if temp <= 35:
            escalate(2, "Temperature 35°C or lower")
        if months is not None and months < 3:
            if temp >= 38 or temp < 36:
                escalate(2, "Dangerous temperature in infant under 3 months")
        elif temp >= 39.1:
            escalate(3, "High temperature")

    if heart is not None and age is not None:
        if age < 8 and heart < 60:
            escalate(1, "Child heart rate below 60")
        elif age < 0.25 and heart > 180:
            escalate(2, "Infant heart rate above 180")
        elif age < 3 and heart > 160:
            escalate(2, "Young child heart rate above 160")
        elif age < 8 and heart > 140:
            escalate(2, "Child heart rate above 140")
        elif age < 16 and (heart > 120 or heart <= 40):
            escalate(2, "School-age heart rate danger")
        elif age >= 16:
            if heart >= 131 or heart <= 40:
                escalate(2, "Adult heart rate danger")
            elif heart >= 111:
                escalate(3, "Adult heart rate 111–130")

    if sbp is not None and age is not None:
        if age >= 10:
            if sbp < 80:
                escalate(1, "Systolic BP below 80")
            elif sbp <= 90:
                escalate(2, "Systolic BP 90 or lower")

            if age >= 16 and sbp >= 220:
                escalate(2, "Systolic BP 220 or higher")
        else:
            if age < 1 / 12:
                limit = 60
            elif age < 1:
                limit = 70
            else:
                limit = 70 + 2 * age

            if sbp < limit:
                escalate(1, "Paediatric hypotension")

    is_pregnant = str(pregnant).strip().lower() in (
        "true", "yes", "1", "y"
    )

    if is_pregnant:
        if (sbp is not None and sbp >= 160) or (
            dbp is not None and dbp >= 110
        ):
            escalate(2, "Severe blood pressure in pregnancy")
        elif (sbp is not None and sbp >= 140) or (
            dbp is not None and dbp >= 90
        ):
            escalate(3, "Raised blood pressure in pregnancy")

    if months is not None and months < 3:
        level = min(level, 4)

    return {
        "minimum_urgency_level": level,
        "reasons": reasons,
        "needs_nurse_review": review,
    }


if __name__ == "__main__":
    result = safety_check(
        age_years=45,
        spo2=89,
        pulse=90,
        systolic=120,
        diastolic=80,
        temperature=37,
    )
    print(result)
