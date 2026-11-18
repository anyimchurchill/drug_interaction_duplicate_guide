# Drug Interaction & Duplicate Therapy Guard

A deterministic Python rule-validation module and interactive Streamlit web app that checks active medication lists for:
- Exact duplicate medications (case-insensitive, whitespace-normalized)
- Duplicate therapeutic classes (e.g., overlapping NSAIDs or SSRIs)
- Known drug-drug interactions with severity ratings (HIGH / MODERATE)
- Strict input validation and deterministic alert ordering

## Project Structure
- app.py - Interactive Streamlit web UI
- solution/reference-solution.py - Reference rule engine and data structures
- task-problem/task-problem.py - Practice starter template
- verifier/test-verifier.py - Automated test suite

## Run Locally
py -m pip install -r requirements.txt
py -m streamlit run app.py
py verifier/test-verifier.py
