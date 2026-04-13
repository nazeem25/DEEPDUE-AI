import os
import sys

from backend.modules.doc_intelligence.text_loader import load_text
from backend.modules.doc_intelligence.classifier import classify_document
from backend.modules.doc_intelligence.extractors.bank_statement import extract_bank_statement
from backend.modules.doc_intelligence.extractors.salary_slip import extract_salary_slip
from backend.modules.red_flag_engine.run_red_flags import run_red_flags

from backend.db.insert_data import (
    insert_document,
    insert_salary_slip,
    insert_bank_statement,
    insert_risk_report
)

BASE_DIR = "data"

print("🚀 Starting Risk Analysis...\n")
sys.stdout.flush()

profile = {
    "salary_slips": [],
    "bank_statements": []
}

# -----------------------------
# PROCESS DOCUMENTS
# -----------------------------
for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)

    if not os.path.isdir(folder_path):
        continue

    for file in os.listdir(folder_path):
        if not file.lower().endswith((".jpg", ".png", ".jpeg")):
            continue

        print(f"📄 Processing: {folder}/{file}")
        path = os.path.join(folder_path, file)

        text = load_text(path)
        doc_type = classify_document(text, source_hint=folder)

        print(f"   → classified as: {doc_type}")

        doc_id = insert_document(file, doc_type)

        if doc_type == "salary_slip":
            data = extract_salary_slip(text)
            insert_salary_slip(doc_id, data)
            profile["salary_slips"].append(data)

        elif doc_type == "bank_statement":
            data = extract_bank_statement(text)
            insert_bank_statement(doc_id, data)
            profile["bank_statements"].append(data)

print("\n✅ Extraction Completed")
print(f"💼 Salary slips: {len(profile['salary_slips'])}")
print(f"🏦 Bank statements: {len(profile['bank_statements'])}")

# -----------------------------
# RUN RED FLAG ENGINE
# -----------------------------
print("\n🚨 Running Red Flag Engine...\n")

risk_report = run_red_flags(profile)

print("📊 FINAL RISK SCORE:", risk_report["risk_score"])
print("🚦 Risk Level:", risk_report["risk_level"])

for flag in risk_report["flags"]:
    print(f"🚩 {flag['flag']} ({flag['severity']})")
    print("   →", flag["explanation"])
    print("   → Source:", flag["source"])

# -----------------------------
# SAVE RISK REPORT
# -----------------------------
insert_risk_report(
    risk_report["risk_score"],
    risk_report["risk_level"],
    risk_report["flags"]
)

print("\n✅ Risk Report Saved to Database")
print("🎯 Risk Analysis Completed Successfully")