
import pickle
from pathlib import Path

import pandas as pd
import streamlit as st

from red_flags import detect_red_flags
from safety_rules import safety_check
from input_validation import validate_patient
from triage_decision import assess_case
BASE = Path(__file__).resolve().parent

# Store demonstration patients during this Streamlit session.
if "patients" not in st.session_state:
    st.session_state["patients"] = []

st.set_page_config(
    page_title="TriNova | AI OPD Triage",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 TriNova")
st.subheader("AI-Powered OPD Triage Assistant")
st.warning("Hackathon demonstration only. Not for real clinical decisions.")

@st.cache_resource
def load_models():
    with open(BASE / "triage_level_model.pkl", "rb") as f:
        triage_model = pickle.load(f)
    with open(BASE / "department_model.pkl", "rb") as f:
        department_model = pickle.load(f)
    return triage_model, department_model

try:
    triage_model, department_model = load_models()
except Exception as e:  # noqa: BLE001
    st.error(f"Unable to load AI models: {e}")
    st.stop()


# TriNova Dashboard — live session statistics
st.header("📊 TriNova Dashboard")

patients = st.session_state.get("patients", [])

total_patients = len(patients)

emergency_cases = sum(
    (p.get("priority") in ("Level 1", "Level 2") or p.get("emergency", False))
    for p in patients
)

waiting_patients = sum(
    p.get("status") == "Waiting"
    for p in patients
)

completed_assessments = sum(
    p.get("status") == "Completed"
    for p in patients
)

nurse_review_cases = sum(
    p.get("needs_nurse_review", False)
    and p.get("status") != "Completed"
    for p in patients
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Patients", total_patients)
c2.metric("Emergency Cases", emergency_cases)
c3.metric("Waiting Patients", waiting_patients)
c4.metric("Completed Reviews", completed_assessments)
c5.metric("Nurse Review", nurse_review_cases)

st.divider()

st.header("Patient Registration")

patient_id = st.text_input(
    "Patient / Visit ID",
    placeholder="Example: P001"
)

age = st.number_input("Patient Age (Years)", 0, 120, 25)

sex = st.selectbox(
    "Sex",
    ["Unknown", "Male", "Female", "Other"]
)

complaint = st.text_area(
    "Chief Complaint",
    placeholder="Example: Severe chest pain"
)

medical_conditions = st.text_area(
    "Known Medical Conditions",
    placeholder="Example: Diabetes, hypertension, asthma"
)

current_medications = st.text_area(
    "Current Medications",
    placeholder="Example: Metformin, blood pressure medication"
)



col1, col2 = st.columns(2)

with col1:
    pulse = st.number_input(
        "Pulse (BPM) — Required",
        min_value=0,
        max_value=300,
        value=None,
        step=1,
        placeholder="Enter measured pulse",
    )

    spo2 = st.number_input(
        "Oxygen Saturation (SpO₂ %) — Required",
        min_value=0,
        max_value=200,
        value=None,
        step=1,
        placeholder="Enter measured SpO₂",
    )

with col2:
    systolic = st.number_input(
        "Systolic BP (mmHg) — Required",
        min_value=0,
        max_value=350,
        value=None,
        step=1,
        placeholder="Enter measured systolic BP",
    )

    diastolic = st.number_input(
        "Diastolic BP (mmHg) — Required",
        min_value=0,
        max_value=250,
        value=None,
        step=1,
        placeholder="Enter measured diastolic BP",
    )

    temperature = st.number_input(
        "Temperature (°C) — Required",
        min_value=0.0,
        max_value=100.0,
        value=None,
        step=0.1,
        format="%.1f",
        placeholder="Enter measured temperature in °C",
    )



if st.button("Assess Patient", type="primary"):
    # Emergency screening is performed before any AI prediction.
    assessment = assess_case(
        patient_id=patient_id,
        age=age,
        complaint=complaint,
        pulse=pulse,
        spo2=spo2,
        systolic=systolic,
        diastolic=diastolic,
        temperature=temperature,
    triage_model=triage_model,
department_model=department_model,
)

    # Only valid inputs may proceed to the trained models.
    if not assessment["reasons"]:
        try:
            patient_frame = pd.DataFrame([{
                "age_years": age,
                "age_months": age * 12,
                "sex": sex.lower(),
                "pregnant": "unknown",
                "arrival_mode": "unknown",
                "chief_complaint": complaint,
                "medical_text": (
                    complaint + " " + medical_conditions
                    + " " + current_medications
                ),
                "pulse_bpm": pulse,
                "spo2_pct": spo2,
                "bp_systolic": systolic,
                "bp_diastolic": diastolic,
                "temp_c": temperature,
            }])

            assessment = assess_case(
                patient_id=patient_id,
                age=age,
                complaint=complaint,
                pulse=pulse,
                spo2=spo2,
                systolic=systolic,
                diastolic=diastolic,
                temperature=temperature,
                patient_frame=patient_frame,
                triage_model=triage_model,
                department_model=department_model,
            )

        except Exception:
            assessment["priority"] = "ABSTAIN"
            assessment["department"] = "Unassigned — nurse assessment"
            assessment["needs_nurse_review"] = True
            assessment["reasons"] = [
                "Input preparation failed; nurse assessment required."
            ]
            assessment["status"] = (
                "Immediate review"
                if assessment["emergency"]
                else "Nurse review required"
            )

    st.divider()
    st.header("AI Triage Assessment")

    priority = assessment["priority"]
    department = assessment["department"]

    a, b = st.columns(2)
    a.metric("Triage Priority", priority)
    b.metric("Recommended Department", department)

    if assessment["emergency"]:
        st.error(
            "EMERGENCY WARNING — Immediate qualified clinical "
            "assessment required. Do not wait for AI prediction "
            "or missing measurements."
        )

    if priority == "ABSTAIN":
        st.warning(
            "ABSTAIN — Cannot assess reliably. "
            "Send to nurse now. No low-priority level assigned."
        )
    elif priority in ("Level 1", "Level 2"):
        st.error("EMERGENCY PRIORITY — Immediate nurse review.")
    elif priority == "Level 3":
        st.warning("Urgent — Nurse assessment recommended.")
    else:
        st.info("AI suggestion only — Nurse confirmation required.")

    if assessment["red_flags"]:
        st.error(
            "Detected Red Flags: "
            + ", ".join(assessment["red_flags"])
        )

    if assessment["safety"]["reasons"]:
        st.warning(
            "Safety alerts: "
            + "; ".join(assessment["safety"]["reasons"])
        )

    for reason in assessment["reasons"]:
        st.warning("Verification required: " + reason)

    # A missing patient ID cannot be safely linked to a record.
    # All other ABSTAIN cases are included in nurse review.
    clean_id = str(patient_id or "").strip()

    if not clean_id:
        st.error(
            "Patient / Visit ID is required to save the case. "
            "Seek nurse review now; do not delay an emergency."
        )
    else:
        existing_ids = {
            p["patient_id"] for p in st.session_state["patients"]
        }

        if clean_id in existing_ids:
            st.warning(
                "This Patient / Visit ID already exists. "
                "No duplicate record was created."
            )
        else:
            st.session_state["patients"].append({
                "patient_id": clean_id,
                "age": age,
                "sex": sex,
                "chief_complaint": complaint,
                "medical_conditions": medical_conditions,
                "current_medications": current_medications,
                "pulse": pulse,
                "spo2": spo2,
                "systolic": systolic,
                "diastolic": diastolic,
                "temperature": temperature,
                "priority": priority,
                "department": department,
                "red_flags": (
                    ", ".join(assessment["red_flags"])
                    if assessment["red_flags"] else "None"
                ),
                "status": assessment["status"],
                "needs_nurse_review": True,
                "emergency": assessment["emergency"],
                "abstain_reasons": "; ".join(
                    assessment["reasons"]
                ),
            })
            st.success(
                f"Patient {clean_id} added to the triage queue."
            )

    st.caption(
        "Hackathon prototype only. Not clinically validated. "
        "All assessments require qualified clinician review."
    )

# Display the patient triage queue
st.divider()
st.header("📋 Triage Queue")

if "patients" in st.session_state and st.session_state["patients"]:
    queue_df = pd.DataFrame(st.session_state["patients"])

    st.dataframe(
        queue_df[
            [
                "patient_id",
                "age",
                "chief_complaint",
                "priority",
                "department",
                "red_flags",
                "status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No patients assessed yet.")

# Nurse / Doctor Review — hackathon demonstration
st.divider()
st.header("🩺 Nurse / Doctor Review")

patients = st.session_state.get("patients", [])

if not patients:
    st.info("No patients available for review.")
else:
    patient_options = {
        f"{p['patient_id']} | {p['priority']} | {p['status']}": i
        for i, p in enumerate(patients)
    }

    selected_label = st.selectbox(
        "Select Patient for Review",
        list(patient_options.keys()),
    )

    selected_patient = patients[patient_options[selected_label]]

    st.write("**Patient ID:**", selected_patient["patient_id"])
    st.write("**Chief Complaint:**", selected_patient["chief_complaint"])
    st.write("**AI Priority:**", selected_patient["priority"])
    st.write("**Recommended Department:**", selected_patient["department"])
    st.write("**Detected Red Flags:**", selected_patient["red_flags"])

    if selected_patient["priority"] in ("Level 1", "Level 2"):
        st.error(
            "Emergency priority: immediate qualified clinical review required."
        )

    reviewer_name = st.text_input("Reviewer Name (Demo Only)")

    review_status = st.selectbox(
        "Update Patient Status",
        [
            "Waiting",
            "Nurse review required",
            "Immediate review",
            "Completed",
        ],
    )

    if st.button("Save Review"):
        if not reviewer_name.strip():
            st.error("Please enter the reviewer's name.")
        else:
            selected_patient["status"] = review_status
            selected_patient["reviewed_by"] = reviewer_name.strip()

            st.success(
                f"Review saved for {selected_patient['patient_id']}."
            )
            st.rerun()

# Emergency Alerts and Nurse Review Lists
st.divider()
st.header("🚨 Emergency Alerts")

patients = st.session_state.get("patients", [])

emergency_patients = [
    p for p in patients
    if (p.get("priority") in ("Level 1", "Level 2") or p.get("emergency", False))
]

if emergency_patients:
    for patient in emergency_patients:
        st.error(
            f"Patient {patient.get('patient_id')} | "
            f"{patient.get('priority')} | "
            f"{patient.get('chief_complaint')} | "
            f"Status: {patient.get('status')}"
        )
    st.warning(
        "Emergency alerts remain visible regardless of review status. "
        "Immediate qualified clinical assessment is required."
    )
else:
    st.info("No emergency-priority patients currently in the queue.")

st.divider()
st.header("🩺 Pending Nurse Review")

review_patients = [
    p for p in patients
    if p.get("needs_nurse_review", False)
    and p.get("status") != "Completed"
]

if review_patients:
    st.dataframe(
        pd.DataFrame(review_patients)[
            [
                "patient_id",
                "chief_complaint",
                "priority",
                "department",
                "status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No pending nurse-review cases.")

