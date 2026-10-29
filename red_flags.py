
# SmartTriage AI - Red Flag Detection
# Hackathon demonstration only. Not for clinical use.

import re

# These are starter keyword rules, not complete clinical detection.
# Every code must match the hackathon red_flag_codes.csv.

RED_FLAG_PATTERNS = {
    "RF_CHEST_PAIN_CARDIAC": [
        r"\bchest pain\b",
        r"\bchest pressure\b",
        r"\bchest tightness\b",
        r"\bheart attack\b",
    ],
    "RF_STROKE_SIGNS": [
        r"\bface droop",
        r"\bslurred speech\b",
        r"\bone.side weakness\b",
        r"\bsudden paralysis\b",
        r"\bstroke\b",
    ],
    "RF_RESP_DISTRESS": [
        r"\bsevere breathlessness\b",
        r"\bstruggling to breathe\b",
        r"\bgasping\b",
        r"\brespiratory distress\b",
    ],
    "RF_ALTERED_SENSORIUM": [
        r"\bunconscious\b",
        r"\bunresponsive\b",
        r"\bnot responding\b",
        r"\baltered sensorium\b",
    ],
    "RF_SEIZURE": [
        r"\bseizure",
        r"\bconvulsion",
        r"\bfit occurring\b",
    ],
    "RF_SEVERE_BLEEDING": [
        r"\bheavy bleeding\b",
        r"\bsevere bleeding\b",
        r"\buncontrolled bleeding\b",
    ],
    "RF_PREGNANCY_BLEEDING": [
        r"\bbleeding during pregnancy\b",
        r"\bpregnant.*bleeding\b",
    ],
    "RF_ECLAMPSIA_SIGNS": [
        r"\beclampsia\b",
        r"\bpregnant.*seizure\b",
    ],
    "RF_REDUCED_FETAL_MOVEMENT": [
        r"\breduced fetal movement\b",
        r"\bbaby not moving\b",
    ],
    "RF_POISONING": [
        r"\bpoisoning\b",
        r"\bpoison ingestion\b",
        r"\boverdose\b",
    ],
    "RF_SNAKEBITE": [
        r"\bsnake.?bite\b",
        r"\bbitten by snake\b",
    ],
    "RF_SCORPION_STING": [
        r"\bscorpion sting\b",
        r"\bscorpion bite\b",
    ],
    "RF_SEVERE_DEHYDRATION": [
        r"\bsevere dehydration\b",
        r"\bnot passing urine\b",
    ],
    "RF_HIGH_FEVER_INFANT": [
        r"\binfant.*high fever\b",
        r"\bnewborn.*fever\b",
    ],
    "RF_CHILD_DANGER_SIGNS": [
        r"\bchild not drinking\b",
        r"\bchild lethargic\b",
    ],
    "RF_SEPSIS_SIGNS": [
        r"\bsepsis\b",
        r"\bseptic shock\b",
    ],
    "RF_MENINGITIS_SIGNS": [
        r"\bneck stiffness\b",
        r"\bmeningitis\b",
    ],
    "RF_DENGUE_WARNING": [
        r"\bdengue.*bleeding\b",
        r"\bdengue warning\b",
    ],
    "RF_SUICIDAL": [
        r"\bsuicidal\b",
        r"\bwants to die\b",
        r"\bself.harm\b",
    ],
    "RF_ACUTE_PSYCHOSIS_AGITATION": [
        r"\bacute psychosis\b",
        r"\bviolent agitation\b",
    ],
    "RF_TRAUMA_MAJOR": [
        r"\bmajor trauma\b",
        r"\broad traffic accident\b",
        r"\bsevere injury\b",
    ],
    "RF_ANAPHYLAXIS": [
        r"\banaphylaxis\b",
        r"\bthroat closing\b",
    ],
    "RF_DKA_SIGNS": [
        r"\bdiabetic ketoacidosis\b",
        r"\bdka\b",
    ],
    "RF_HYPOGLYCAEMIA": [
        r"\bhypoglycaemia\b",
        r"\bhypoglycemia\b",
        r"\bvery low blood sugar\b",
    ],
    "RF_HEAT_STROKE": [
        r"\bheat stroke\b",
        r"\bheatstroke\b",
    ],
    "RF_ACUTE_ABDOMEN": [
        r"\bacute abdomen\b",
        r"\bsevere abdominal pain\b",
    ],
    "RF_THUNDERCLAP_HEADACHE": [
        r"\bthunderclap headache\b",
        r"\bworst headache of life\b",
    ],
    "RF_TESTICULAR_TORSION": [
        r"\btesticular torsion\b",
        r"\bsudden testicular pain\b",
    ],
    "RF_EYE_EMERGENCY": [
        r"\bchemical eye injury\b",
        r"\bsudden vision loss\b",
    ],
    "RF_BURNS_MAJOR": [
        r"\bmajor burns\b",
        r"\bsevere burns\b",
    ],
}





# Additional multilingual and common-language patterns.
# These are conservative screening heuristics for synthetic hackathon data.

EXTRA_RED_FLAG_PATTERNS = {
    "RF_CHEST_PAIN_CARDIAC": [
        r"\bseene mein dard\b",
        r"\bchhati mein dard\b",
        r"\bchati me dard\b",
        r"\bchest discomfort\b",
    ],
    "RF_STROKE_SIGNS": [
        r"\bbolne mein dikkat\b",
        r"\bchehra tedha\b",
        r"\bek taraf.*kamzori\b",
        r"\bface.*droop",
    ],
    "RF_RESP_DISTRESS": [
        r"\bsaans.*nahi.*aa",
        r"\bsaans lene mein.*dikkat\b",
        r"\bsevere shortness of breath\b",
        r"\bunable to breathe\b",
    ],
    "RF_ALTERED_SENSORIUM": [
        r"\bbehosh\b",
        r"\bhosh nahi\b",
        r"\bnot waking up\b",
    ],
    "RF_SEIZURE": [
        r"\bdaura pad",
        r"\bfits aa",
        r"\bjerking.*unresponsive\b",
    ],
    "RF_SEVERE_BLEEDING": [
        r"\bbahut khoon\b",
        r"\bkhoon.*ruk nahi",
        r"\bprofuse bleeding\b",
    ],
    "RF_POISONING": [
        r"\bzeher\b",
        r"\bzahar\b",
        r"\bpesticide.*drink",
    ],
    "RF_SNAKEBITE": [
        r"\bsaap.*kata\b",
        r"\bsaap.*kaat",
        r"\bsaanp.*kata\b",
        r"\bsnake.*bit",
    ],
    "RF_SCORPION_STING": [
        r"\bbichhu.*kata\b",
        r"\bbichoo.*kata\b",
    ],
    "RF_MENINGITIS_SIGNS": [
        r"\bstiff neck\b",
        r"\bgardan.*akad",
    ],
    "RF_DENGUE_WARNING": [
        r"\bdengue.*vomit",
        r"\bdengue.*pet.*dard",
        r"\bfever.*persistent vomiting\b",
    ],
    "RF_SUICIDAL": [
        r"\bkhudkushi\b",
        r"\batmahatya\b",
        r"\bkill myself\b",
    ],
    "RF_ANAPHYLAXIS": [
        r"\bthroat swelling.*breath",
        r"\ballergic.*cannot breathe\b",
    ],
    "RF_ACUTE_ABDOMEN": [
        r"\bsevere stomach pain\b",
        r"\bbahut tez pet dard\b",
    ],
    "RF_EYE_EMERGENCY": [
        r"\baankh.*chemical\b",
        r"\bchemical.*aankh\b",
        r"\bsudden blindness\b",
        r"\bachanak.*dikhai nahi\b",
    ],
    "RF_BURNS_MAJOR": [
        r"\bextensive burns\b",
        r"\bsevere burn injury\b",
    ],
}

for code, patterns in EXTRA_RED_FLAG_PATTERNS.items():
    RED_FLAG_PATTERNS[code].extend(patterns)


def detect_red_flags(complaint):
    """Detect candidate red flags for immediate human review."""
    text = str(complaint or "").lower().strip()

    if text in ("", "nan", "none", "null", "xx", "unknown"):
        return []

    found = []

    for code, patterns in RED_FLAG_PATTERNS.items():
        if any(re.search(pattern, text) for pattern in patterns):
            found.append(code)

    return found
if __name__ == "__main__":
        examples = [
        "Severe chest pain",
        "Sudden face drooping and slurred speech",
        "Fever and headache",
        "Snake bite",
    ]

        for complaint in examples:
            print("Complaint:", complaint)
            print("Red flags:", detect_red_flags(complaint))
            print()