# SmartTriage AI
## TalentAP Mega Hackathon 2026 — H1

### Project Overview
SmartTriage AI is a prototype OPD triage assistant for
a fictional government district hospital.

It assists nursing staff by predicting:
- Triage priority (Levels 1–5 or ABSTAIN)
- Recommended hospital department
- Emergency red-flag codes

All AI recommendations require human review.
This prototype is not approved for clinical use.

### How It Works
1. A patient enters registration details and symptoms.
2. The system processes patient information.
3. Trained machine-learning models predict triage
   priority and department.
4. Safety rules check critical vital signs.
5. The dashboard displays the recommendation
   and any safety alerts.
6. Nursing staff review the result.

### Technologies
- Python
- Pandas
- NumPy
- Scikit-learn
- Streamlit

### Running the Dashboard
Install dependencies:

pip install -r requirements.txt

Start the application:

python -m streamlit run app.py

Open http://localhost:8501

### Generating Predictions
Run:

python train_model.py

Then:

python predict_test.py

The prediction file is saved to:
submission/H1_predictions.csv

### Evaluation
Training-data evaluation score: 0.7724
Emergency recall: 0.9965
Department accuracy: 0.8558
Red-flag F1: 0.1644

These results are from the supplied labeled
training dataset, not an independent clinical
validation or official leaderboard score.

### Safety Demonstration
In the dashboard:
- SpO2 of 88% produced Level 2.
- SpO2 of 82% produced Level 1.

Both cases were routed to Emergency/Casualty.
These are synthetic demonstration tests.

### Limitations
The system may miss emergency symptoms or red flags.
It must not replace qualified medical professionals.
All patient assessments require human oversight.

### AI Assistance Disclosure
AI assistance was used during development,
debugging, documentation, and testing.
