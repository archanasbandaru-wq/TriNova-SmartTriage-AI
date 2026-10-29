# H1 — OPD Triage Assistant for an Overloaded Government Hospital

**Chandrapuri District Hospital** (a fictional government district hospital) sees about 800 walk-ins a day in its outpatient department (OPD). Two doctors work at the first-contact desk. Patients are seen first-come-first-served (in order of arrival). So a person with chest pain waits behind 40 people with a mild fever. Today an overworked nurse makes the triage decision in about 30 seconds. (Triage means deciding how urgently each patient needs a doctor.)

**Your task:** for each patient you get a short intake form and a free-text complaint. From these, your system must **safely**:

1. assign a **triage priority (1–5)**, where 1 is the most urgent and 5 the least urgent;
2. recommend the **right department**;
3. list the **red-flag symptoms** you detected (warning signs of a possible emergency).

Under-triaging a true emergency (giving it too low a priority) costs **20 times** more than over-triaging a mild case. Your system is also allowed to say **"cannot assess, send to nurse now"** (`ABSTAIN`).

> **In short**
>
> - **You get:** 21,455 training visits with labels (the correct answers), 8,872 test visits without labels, and a triage primer, `data/triage_primer.md`.
> - **You build:** a clinician-assisting system that gives every test visit a triage level (1–5) or `ABSTAIN`, a department, and red-flag codes.
> - **You submit:** one file, `submission/H1_predictions.csv`, inside your team zip `teamID_H1.zip`. You also include all your code and a `README.md` (see **What to submit**).
> - **You are scored by** `evaluate.py`. Missing a true emergency costs 20 times more than over-triaging a mild case. The primary score ranges from −0.6 to 1.0 (higher is better).
> - **Special rule:** your demo **must show your hard-coded escalation rules** for critical vitals (primer, Section 8) and your emergency recall.

## Synthetic data notice

Every record in this package is synthetic. A program generated it for the TalentAP Mega Hackathon 2026. No real patient is described. Names, the hospital and the brand names of medicines are fictional.

> **Ethics note:** All healthcare data is synthetic. No team may use real patient data. Every healthcare solution must be positioned as clinician-assisting, not clinician-replacing, and must include a safety/escalation path. Teams that present an autonomous diagnostic system without a human-in-the-loop will lose points on the Responsibility criterion.

The triage rubric in `data/triage_primer.md` is **simplified for the hackathon and is not for clinical use**.

## What's in the box

| File | Rows | Description |
|---|---|---|
| `data/intake_train.csv` | 21,455 | Intake forms, 2026-08-03 to 2026-08-29 (labelled) |
| `data/train_labels.csv` | 21,455 | Labels for the training visits: level, department, emergency flag, red flags, assessable |
| `data/intake_test.csv` | 8,872 | Intake forms, 2026-08-30 to 2026-09-09 (labels hidden; you predict these) |
| `data/arrival_log.csv` | 30,327 | Arrival log for every visit, with token number and a first-come-first-served simulation (for the stretch goal) |
| `data/triage_primer.md` | n/a | **Read this first.** The 5-level scale, danger-zone vital signs, red-flag codes, departments, and how the labels were made |
| `data/red_flag_codes.csv` | 30 | The allowed red-flag codes with definitions |
| `data/departments.csv` | 13 | The allowed departments with typical complaints |
| `sample_submission.csv` | 8,872 | A valid (deliberately naive) submission for the test data. Use it only to see the format. |
| `evaluate.py` | n/a | The official scorer (organisers use the same file with the hidden test labels) |
| `baseline/baseline.py` | n/a | A simple rules baseline: vital-sign thresholds plus keywords, no machine learning |

## Data dictionary

### `intake_train.csv` / `intake_test.csv`

| Column | Type | Description | Example | Can be missing? |
|---|---|---|---|---|
| visit_id | string | Random visit ID (carries no information) | OPD-K3Z9Q2LM | no |
| arrival_ts | timestamp | Registration time, IST (Indian Standard Time), `YYYY-MM-DDTHH:MM:SS` | 2026-08-04T09:41:07 | no |
| age_years | int | Age in completed years (0 for infants) | 34 | no |
| age_months | int | Age in completed months, filled only for children under 2 years | 2 | yes (blank when age ≥ 2) |
| sex | string | `M`, `F` or `Other` | F | no |
| pregnant | string | `Y`, `N` or `unknown`, recorded only for females aged 15–49 | Y | yes (blank for everyone else) |
| arrival_mode | string | `walk-in`, `brought by family` or `ambulance-referred` | walk-in | no |
| bp_systolic | int | Recorded systolic BP (the upper blood-pressure number), in mmHg | 130 | yes |
| bp_diastolic | int | Recorded diastolic BP (the lower blood-pressure number), in mmHg | 80 | yes |
| pulse_bpm | int | Recorded pulse (beats /min) | 96 | yes |
| temp_c | float | Recorded temperature (meant to be °C) | 38.4 | yes |
| spo2_pct | int | Recorded oxygen saturation (%) | 97 | yes |
| chief_complaint | text | Free-text complaint as told by the patient or relative, or as typed by the clerk | "mujhe 3 din se bukhar hai, badan dard" | yes (sometimes blank or meaningless) |
| known_conditions | text | Known illnesses, free text, usually `;`-separated | "sugar; BP" | yes |
| current_medications | text | Current medicines, free text (generic names and fictional brands) | "metformin 500 BD; Amlochand 5" | yes |

### `train_labels.csv` (the hidden `test_truth.csv` has the same columns)

| Column | Type | Description | Example |
|---|---|---|---|
| visit_id | string | Joins to the intake file | OPD-K3Z9Q2LM |
| triage_level | int | 1 (resuscitation, most urgent) … 5 (non-urgent, least urgent), per the primer | 4 |
| department | string | One of the 13 departments in `data/departments.csv` | General Medicine |
| true_emergency | 0/1 | 1 if triage_level is 1 or 2 | 0 |
| red_flags | text | `;`-separated red-flag codes truly present (empty if none) | RF_SNAKEBITE |
| assessable | 0/1 | 0 if the case genuinely cannot be assessed from the form (primer, Section 7) | 1 |

### `arrival_log.csv`

| Column | Type | Description |
|---|---|---|
| visit_id | string | Joins to the intake files |
| opd_date | date | OPD day |
| token_no | int | Queue token, in order of arrival that day |
| arrival_ts | timestamp | Registration time (same as the intake file) |
| consult_minutes | float | Synthetic doctor time for this patient at the first-contact desk (independent of the patient's condition) |
| fcfs_consult_start_ts | timestamp | When the patient was seen under today's first-come-first-served (FCFS) system (2 doctors, 08:00 start) |

## Know your data

- **Read the primer.** The labels were produced by applying the primer's rules to each patient's **true** clinical state. The form shows that state only partly, and imperfectly.
- **Complaints are written the way people talk.** You will see English, Hinglish (Hindi and English mixed) and transliterated Hindi (Hindi written in English letters). You will also see some Devanagari (Hindi script), and a little Bengali, Telugu, Tamil and Marathi in Latin script (English letters).
- **Expect messy text:** spelling mistakes, SMS shortcuts, missing punctuation, ALL CAPS, the occasional emoji, clerk shorthand ("c/o fever x3d") and truncated text.
- **Children's complaints are in the parent's voice.** Very sick adults' complaints are often told by a relative.
- **Patients under-report and over-report.** "Thoda sa" may hide something serious. "bahut tez dard, emergency!" may be minor. Atypical presentations exist (for example a heart attack described as "gas").
- **Vital signs may be missing or mis-entered.** You will see blanks and BP recorded as 0. Some values look like they were entered in the wrong unit or the wrong box. Some digits are obviously wrong. BP is often not measured in young children. Clean the vitals carefully: your escalation rules depend on them.
- **A few complaints are blank or meaningless.** If there is also almost no usable vital sign, the case cannot be assessed.
- **Mixed words for the same thing.** Known conditions and medicine lists use mixed vocabulary ("sugar", "DM", "diabetes"; "BP", "HTN").
- **OPD hours.** The OPD runs 08:00–14:00 Monday–Saturday (busiest on Mondays). There is a reduced 08:00–11:00 session on Sundays and on Independence Day.

## Train / test split

The split is by time:

- **Training data:** visits from 2026-08-03 to 2026-08-29 (21,455 visits, labelled).
- **Test data:** visits from 2026-08-30 to 2026-09-09 (8,872 visits). Their labels are hidden and used for the leaderboard.

Each row is a separate visit. No patient identity links visits. The test period is later in the monsoon, so expect slightly more fever-type illness.

## What to submit

You submit **one file**, `H1_predictions.csv`. Put it at this exact path inside your team zip:

```
teamID_H1.zip                  a zip of your project (a fresh git clone)
├── README.md                  how to set up and run your code
├── submission/
│   └── H1_predictions.csv
└── FULL_CODE/                 This folder should contain all of your code:
                               your demo app + the code that created the
                               submission/ files
```

**Your code is required too.** Every team submits one zip of its whole project, as the *Participant Coding Guidelines* explain (zip a fresh `git clone` of your project). The zip holds **all** your code, not only the code that makes your submission files: also the code of the solution you demo (for example a web or mobile app, dashboard, API, command-line tool or notebook). It also holds your own `README.md` that explains how to set up and run everything. It is fine if everything sits inside one project folder in the zip.

- Write your **own** `README.md`. The *Participant Coding Guidelines* (rule 12) list what it must cover. If you built inside this pack's folder, replace this pack's README with yours (rename this one to `PACK_README.md` if you want to keep it).
- Put **all** your code inside a folder named exactly `FULL_CODE/`, at the top of your project: your demo app + the code that created the `submission/` files. At the top of your project, keep only `README.md`, `submission/`, `FULL_CODE/` and your `.gitignore` (plus a `LICENSE` file if you have one).
- Put `submission/` at the top of your project, next to your `README.md`.
- Commit the files in `submission/` to git. Make sure your `.gitignore` does not exclude them (for example with `*.csv` or `*.jsonl`).
- Before you commit, list `data/`, `models/`, `.env`, `.venv/` and `node_modules/` in your `.gitignore`. This keeps the pack's data files and downloaded models out of your zip. Your README should say where to put the data and how to get any models.

Replace `teamID` with your own team ID.

The file must have **all 5 columns** below, with these exact names. Some cells may be left empty, as the table says.

| Column | Allowed values | Can the cell be empty? |
|---|---|---|
| visit_id | every visit_id from `data/intake_test.csv` (extra IDs are ignored) | no |
| triage_level | `1`, `2`, `3`, `4`, `5` or `ABSTAIN` ("cannot assess, send to nurse now"). 1 is the most urgent. | no |
| department | one of the 13 department names exactly as in `data/departments.csv` (case-insensitive: capital and small letters do not matter) | only when triage_level is `ABSTAIN` |
| red_flags | `;`-separated codes from `data/red_flag_codes.csv` | yes (means no red flags) |
| confidence | a number between 0 and 1 (not scored; use it in your demo) | yes |

Example row:

```
visit_id,triage_level,department,red_flags,confidence
OPD-K3Z9Q2LM,2,Emergency/Casualty,RF_CHEST_PAIN_CARDIAC,0.83
```

**Checklist before you zip:**

1. The file is named exactly `H1_predictions.csv`. It is inside the `submission/` folder at the top of your project, in `teamID_H1.zip`.
2. It has all 5 columns: `visit_id`, `triage_level`, `department`, `red_flags`, `confidence`.
3. It has one row for every `visit_id` in `data/intake_test.csv`. Each `visit_id` appears only once. A duplicate or empty `visit_id` makes `evaluate.py` stop with a SUBMISSION FORMAT ERROR.
4. Do not leave out any test visit. A missing visit is scored as level 5 (worst case), and `evaluate.py` prints a WARNING about it.
5. Every value follows the table above. If one does not, `evaluate.py` stops with a SUBMISSION FORMAT ERROR message that says what to fix.

## How you're scored

`evaluate.py` compares your file with the true labels and prints a report. It also saves the report as a `.json` file.

### Emergency recall

**Emergency recall (sensitivity)** is reported first. It is the share of true emergencies (level 1 or 2) that you predicted as level 1 or 2 **or** sent to the nurse with ABSTAIN. A value of 1.0 means you caught every true emergency.

### Cost per visit

Every visit gets a cost. **Lower cost is better.** In the table, t is the truth level and p is your prediction.

Remember that level 1 is the most urgent. So **p > t** means you gave a *less* urgent level than the truth (under-triage). **p < t** means you gave a *more* urgent level than the truth (over-triage).

| Situation | Cost |
|---|---|
| True emergency and p = 1 or 2 | 0 |
| True emergency and p = 3, 4 or 5 (missed emergency) | **20** |
| Not an emergency, p > t (under-triage) | 2 × (p − t) |
| p < t (over-triage) | 1 × (t − p), at most 4 |
| p = t | 0 |
| ABSTAIN on an unassessable case or a true emergency | 0 |
| ABSTAIN on any other case (nurse time) | 1.5 |
| No prediction for a test visit | scored as level 5 (worst case), and `evaluate.py` prints a warning |

How `evaluate.py` reads this table:

- If you predict ABSTAIN, only the two ABSTAIN rows apply.
- Otherwise, for a true emergency, only the first two rows apply.
- Otherwise (not ABSTAIN, not a true emergency), the p > t, p < t and p = t rows apply.

### The primary score

```
normalised_safety_score = clip(1 − your_total_cost / reference_total_cost, −1, 1)
   where reference = "predict level 4 for every visit, never abstain"
primary_score = 0.6 × normalised_safety_score
              + 0.2 × emergency_recall
              + 0.1 × department_accuracy   (on visits you did not abstain on and that are assessable)
              + 0.1 × red_flag_micro_F1     (micro-averaged over all codes and visits)
```

What each part means:

- **normalised_safety_score** compares your total cost with a simple reference system. That system predicts level 4 for every visit and never abstains. A score of 1 means zero cost. A score of 0 means the same cost as the reference. `clip(…, −1, 1)` keeps the value between −1 and 1, so −1 means double the reference cost or worse.
- **emergency_recall** is explained above. Close to 1 is good.
- **department_accuracy** is the share of visits where your department matches the true one. It counts only visits you did not abstain on and that are assessable.
- **red_flag_micro_F1** checks your red-flag codes. F1 balances precision (what share of your codes are correct) and recall (what share of the true codes you found). Micro-averaged means all codes from all visits are counted together. Close to 1 is good.
- **primary_score** adds these four parts with the weights shown. The safety part carries the most weight (0.6).

The primary score ranges from −0.6 to 1.0 (higher is better). All constants are at the top of `evaluate.py`.

A model tuned only for plain accuracy will score badly. The reason is that the 20× penalty for a missed emergency dominates. Finding that out is part of the exercise.

### How judges use the score

The leaderboard score is **20 % of the judging rubric**:

| Judging criterion | Share |
|---|---|
| Problem framing & assumptions | 20 % |
| Technical soundness | 25 % |
| Score on hidden split (your `evaluate.py` score on the test data) | 20 % |
| Real-world usability | 15 % |
| Responsibility | 15 % |
| Demo & communication | 5 % |

**Your demo must show:**

1. your **hard-coded escalation rules** for critical vitals (primer, Section 8);
2. your emergency recall.

## Hour Zero quick start

Run these commands **one at a time** from this folder (the folder that contains this `README.md`). You need Python 3.9+ with `numpy` and `pandas`.

On Mac/Linux, type `python3` instead of `python`.

**Step 1.** Run the baseline on the training data. It writes `baseline_train_predictions.csv`.

```bash
python baseline/baseline.py --input data/intake_train.csv --out baseline_train_predictions.csv
```

**Step 2.** Score the baseline on the labelled training data. The report prints on screen and is saved as `score_train.json`. Read the printout, starting with emergency recall. Then find the PRIMARY SCORE line. The baseline scores about 0.46 on the training labels.

```bash
python evaluate.py --submission baseline_train_predictions.csv --truth data/train_labels.csv --out score_train.json
```

**Step 3.** Make the **test submission**. This command writes `submission/H1_predictions.csv`, a valid submission for the test data. The organisers score it with the hidden test labels: the baseline scores about 0.47 on the test data.

```bash
python baseline/baseline.py --input data/intake_test.csv --out submission/H1_predictions.csv
```

## Assumptions you may make

- No labs, imaging or ECG are available at triage. You have only the intake form.
- Vital signs may be missing or mis-entered (teams must handle a BP of 0 or a temperature of 96 °C).
- Patients may under-report or over-report symptoms.
- The nurse has ≤ 60 seconds per patient, so the interface must be near-instant.

**Stretch goal (optional):** estimate the expected wait-time reduction for true emergencies versus first-come-first-served, using `data/arrival_log.csv`.

## Licence

Synthetic data generated for the TalentAP Mega Hackathon 2026. CC BY 4.0. Contains no real personal data.
