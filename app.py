import streamlit as st
from soc2_controls import SOC2_CONTROLS

st.set_page_config(page_title="SOC 2 Readiness Checker", page_icon="🛡️", layout="wide")
st.title("🛡️ SOC 2 Readiness Checker (Security) — No-AI MVP")
st.caption("Informational guidance only. Not legal or audit advice.")

OPTIONS = ["Yes", "Partially", "No", "Not sure"]

def score(ans: str) -> float:
    return {"Yes": 1.0, "Partially": 0.5, "No": 0.0, "Not sure": 0.25}[ans]

def risk_label(readiness: float) -> str:
    if readiness >= 0.80:
        return "Low"
    if readiness >= 0.55:
        return "Medium"
    return "High"

# --- Collect org info ---
with st.expander("Optional: Scope Info", expanded=False):
    org = st.text_input("Company / org name (optional)", placeholder="Example: Joshua Labs")
    stack = st.selectbox("Primary environment (optional)", ["Mixed/Not sure", "Microsoft 365", "Google Workspace", "AWS-heavy", "On-prem / Hybrid"])
    notes = st.text_area("Notes (optional)", height=90, placeholder="Example: 10 employees, remote-first, M365 + Intune, no SIEM yet.")

# --- Questionnaire UI grouped by category ---
st.subheader("1) Questionnaire")
answers = {}

categories = sorted(set(c["category"] for c in SOC2_CONTROLS))
tabs = st.tabs(categories)

for cat, tab in zip(categories, tabs):
    with tab:
        for c in [x for x in SOC2_CONTROLS if x["category"] == cat]:
            answers[c["id"]] = st.selectbox(
                f"{c['question']}  \n**Mapped:** {', '.join(c['cc'])}",
                OPTIONS,
                key=c["id"]
            )

# --- Scoring ---
st.divider()
st.subheader("2) Results")

total_weight = sum(c["weight"] for c in SOC2_CONTROLS)
weighted_points = 0.0

gaps = []
strengths = []

for c in SOC2_CONTROLS:
    ans = answers.get(c["id"], "Not sure")
    s = score(ans)
    weighted_points += s * c["weight"]

    row = {
        "id": c["id"],
        "category": c["category"],
        "question": c["question"],
        "answer": ans,
        "score": s,
        "weight": c["weight"],
        "cc": c["cc"],
        "fix": c["fix"],
        "owner": c["owner"],
        "evidence": c["evidence"],
    }

    if s >= 0.75:
        strengths.append(row)
    else:
        gaps.append(row)

readiness = (weighted_points / total_weight) if total_weight else 0.0
st.metric("Overall readiness score", f"{round(readiness * 100)}%")
st.metric("Estimated risk", risk_label(readiness))

gaps_sorted = sorted(gaps, key=lambda r: (r["score"], -r["weight"]))
strengths_sorted = sorted(strengths, key=lambda r: (-r["score"], -r["weight"]))

colA, colB = st.columns(2)
with colA:
    st.write("### Top gaps")
    for g in gaps_sorted[:6]:
        st.write(f"- **{g['cc'][0]}** — {g['question']} (**{g['answer']}**)")

with colB:
    st.write("### Top strengths")
    for s in strengths_sorted[:6]:
        st.write(f"- **{s['cc'][0]}** — {s['question']} (**{s['answer']}**)")

# --- Report generation (no AI) ---
st.divider()
st.subheader("3) Generated Report (Downloadable)")

report_lines = []
report_lines.append("# Executive Summary")
if org:
    report_lines.append(f"- Organization: **{org}**")
if stack and stack != "Mixed/Not sure":
    report_lines.append(f"- Environment: **{stack}**")
report_lines.append(f"- Overall readiness score: **{round(readiness * 100)}%**")
report_lines.append(f"- Estimated risk: **{risk_label(readiness)}**")
report_lines.append("- This report is based solely on questionnaire responses and provides SOC 2 Security-aligned guidance.")
report_lines.append("- It does **not** certify compliance or audit readiness.")

report_lines.append("\n# Strengths Observed")
if strengths_sorted:
    for s in strengths_sorted:
        report_lines.append(f"- ({', '.join(s['cc'])}) {s['question']} — **{s['answer']}**")
else:
    report_lines.append("- No strengths identified based on current responses.")

report_lines.append("\n# Key Gaps and Risks")
if gaps_sorted:
    for g in gaps_sorted:
        report_lines.append(f"- ({', '.join(g['cc'])}) {g['question']} — **{g['answer']}**")
else:
    report_lines.append("- No major gaps identified based on current responses.")

report_lines.append("\n# Prioritized Remediation Plan")
if gaps_sorted:
    for i, g in enumerate(gaps_sorted[:7], start=1):
        report_lines.append(
            f"{i}. **{g['fix']}**  \n"
            f"   - Owner: {g['owner']}  \n"
            f"   - Control(s): {', '.join(g['cc'])}  \n"
            f"   - How to verify: Collect evidence and confirm control operates as designed."
        )
else:
    report_lines.append("1. Maintain current controls and ensure evidence is consistently collected and retained.")

report_lines.append("\n# Evidence Checklist (What to Collect)")
# Deduplicate evidence lines but keep them grouped roughly by control mapping
evidence_items = []
for g in gaps_sorted:
    for ev in g["evidence"]:
        evidence_items.append(f"- ({', '.join(g['cc'])}) {ev}")
if evidence_items:
    report_lines.extend(sorted(set(evidence_items)))
else:
    report_lines.append("- Collect baseline evidence for access controls, logging, incident response, and change management.")

report_lines.append("\n# Assumptions & Limitations")
report_lines.append("- Answers are assumed accurate and current.")
report_lines.append("- This tool provides informational guidance only and is not legal or audit advice.")
report_lines.append("- A formal SOC 2 readiness assessment typically includes interviews, evidence validation, and scoping review.")

if notes:
    report_lines.append("\n# Additional Notes")
    report_lines.append(notes)

report_md = "\n".join(report_lines)

st.markdown(report_md)

st.download_button(
    "Download report (Markdown)",
    data=report_md.encode("utf-8"),
    file_name="soc2_readiness_report.md",
    mime="text/markdown",
)
