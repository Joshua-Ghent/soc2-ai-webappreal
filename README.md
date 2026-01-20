# SOC 2 Security Readiness Checker

A Streamlit web app that helps small teams quickly assess SOC 2 Security readiness using a structured questionnaire, weighted scoring, and a gap report with an evidence checklist.

## Features
- SOC 2 Security-aligned questionnaire (plain English)
- Weighted readiness score + risk level
- Prioritized remediation plan
- Evidence checklist

## Tech Stack
- Python
- Streamlit

## Run Locally
```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
## Disclaimer
This tool provides informational guidance only and does not constitute legal, audit, or compliance advice.
