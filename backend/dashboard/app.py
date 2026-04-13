import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from sklearn.ensemble import IsolationForest
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table
import os

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="DeepDue AI Premium", layout="wide")

# ------------------ LUXURY DARK THEME ------------------
st.markdown("""
<style>
body { background-color: #0f1117; color: white; }
.block-container { padding-top: 2rem; }
.metric-container {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🔍 DeepDue AI — Enterprise Risk Dashboard")
st.caption("AI Powered Financial Risk & Fraud Intelligence System")
st.divider()

# ------------------ FETCH API DATA ------------------
summary = requests.get(f"{API}/summary").json()
risk = requests.get(f"{API}/risk").json()
flags = requests.get(f"{API}/flags").json()

salary_total = summary.get("salary_total", 0)
bank_total = summary.get("bank_credit_total", 0)
risk_score = risk.get("risk_score", 0)
risk_level = risk.get("risk_level", "LOW")

# ------------------ KPI SECTION ------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 Documents", summary["documents"])
col2.metric("💼 Salary Slips", summary["salary_slips"])
col3.metric("🏦 Bank Statements", summary["bank_statements"])
col4.metric("🚨 Risk Reports", summary["risk_reports"])

st.divider()

# ------------------ RISK GAUGE ------------------
gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=risk_score,
    title={"text": "Overall Risk Score"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "#ff4b4b"},
        "steps": [
            {"range": [0, 30], "color": "#2ecc71"},
            {"range": [30, 70], "color": "#f39c12"},
            {"range": [70, 100], "color": "#e74c3c"},
        ],
    },
))
st.plotly_chart(gauge, width="stretch")

if risk_level == "LOW":
    st.success("🟢 LOW RISK")
elif risk_level == "MEDIUM":
    st.warning("🟠 MEDIUM RISK")
else:
    st.error("🔴 HIGH RISK")

st.divider()

# ------------------ SALARY VS BANK ------------------
st.subheader("💰 Salary vs Bank Credits")

income_df = pd.DataFrame({
    "Category": ["Declared Salary", "Bank Credits"],
    "Amount": [salary_total, bank_total]
})

bar_fig = px.bar(income_df, x="Category", y="Amount", text_auto=True)
st.plotly_chart(bar_fig, width="stretch")

# ------------------ ISOLATION FOREST ------------------
st.subheader("🧠 ML Anomaly Detection (Isolation Forest)")

data = np.array([[salary_total], [bank_total]])

if salary_total > 0 and bank_total > 0:
    model = IsolationForest(contamination=0.3)
    model.fit(data)
    anomaly = model.predict(data)

    anomaly_df = pd.DataFrame({
        "Value": [salary_total, bank_total],
        "Type": ["Salary", "Bank Credit"],
        "Anomaly": anomaly
    })

    anomaly_fig = px.scatter(
        anomaly_df,
        x="Type",
        y="Value",
        color="Anomaly",
        size="Value"
    )
    st.plotly_chart(anomaly_fig, width="stretch")
else:
    st.info("Not enough data for anomaly detection.")

st.divider()

# ------------------ BENFORD'S LAW ------------------
st.subheader("📊 Benford’s Law Fraud Detection")

def leading_digit(n):
    return int(str(int(abs(n)))[0]) if n > 0 else 0

digits = [leading_digit(salary_total), leading_digit(bank_total)]
digit_counts = pd.Series(digits).value_counts().sort_index()

benford_expected = {d: np.log10(1 + 1/d) for d in range(1, 10)}

benford_df = pd.DataFrame({
    "Digit": list(benford_expected.keys()),
    "Expected": list(benford_expected.values()),
    "Observed": [digit_counts.get(d, 0)/len(digits) if len(digits)>0 else 0 for d in benford_expected.keys()]
})

benford_fig = go.Figure()
benford_fig.add_trace(go.Bar(x=benford_df["Digit"], y=benford_df["Expected"], name="Expected"))
benford_fig.add_trace(go.Bar(x=benford_df["Digit"], y=benford_df["Observed"], name="Observed"))

st.plotly_chart(benford_fig, width="stretch")

st.divider()

# ------------------ FLAGS ------------------
st.subheader("🚩 Risk Flags")

flags_response = requests.get(f"{API}/flags").json()

if isinstance(flags_response, list) and len(flags_response) > 0:
    for flag in flags_response:

        severity = flag.get("severity", "LOW")

        if severity == "HIGH":
            st.error(
                f"⚠ {flag.get('flag')} \n\n"
                f"{flag.get('explanation')}  \n\n"
                f"Source: {flag.get('source')}"
            )

        elif severity == "MEDIUM":
            st.warning(
                f"⚠ {flag.get('flag')} \n\n"
                f"{flag.get('explanation')}  \n\n"
                f"Source: {flag.get('source')}"
            )

        else:
            st.info(
                f"ℹ {flag.get('flag')} \n\n"
                f"{flag.get('explanation')}  \n\n"
                f"Source: {flag.get('source')}"
            )

else:
    st.success("No Risk Flags Detected")

# ------------------ PDF DOWNLOAD ------------------
st.subheader("📄 Download AI Risk Report")

if st.button("Generate Risk Report PDF"):
    file_path = "risk_report.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("DeepDue AI Risk Report", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Risk Score: {risk_score}", styles["Normal"]))
    elements.append(Paragraph(f"Risk Level: {risk_level}", styles["Normal"]))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Flags:", styles["Heading2"]))

    for flag in flags:
        elements.append(Paragraph(flag["flag"], styles["Normal"]))

    doc.build(elements)

    with open(file_path, "rb") as f:
        st.download_button("Download Report", f, file_name="risk_report.pdf")

st.caption("DeepDue AI • Enterprise Financial Intelligence")