import warnings
warnings.filterwarnings("ignore")
import os
from backend.modules.doc_intelligence.text_loader import load_text
from backend.modules.doc_intelligence.classifier import classify_document
from backend.modules.doc_intelligence.extractors.salary_slip import extract_salary_slip
from backend.modules.doc_intelligence.extractors.bank_statement import extract_bank_statement
from backend.modules.red_flag_engine.run_red_flags import run_red_flags
from backend.db.database import get_connection

BASE_DIR = "data"

def main():
    print("🚀 Starting Risk Pipeline...\n")

    profile = {"salary_slips": [], "bank_statements": []}

    conn = get_connection()
    cursor = conn.cursor()

    # Clear old data
    cursor.execute("DELETE FROM documents")
    cursor.execute("DELETE FROM salary_slips")
    cursor.execute("DELETE FROM bank_statements")
    cursor.execute("DELETE FROM risk_reports")
    conn.commit()

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
            doc_type = classify_document(text, folder)

            cursor.execute(
                "INSERT INTO documents (filename, doc_type) VALUES (?, ?)",
                (file, doc_type)
            )
            doc_id = cursor.lastrowid

            if doc_type == "salary_slip":
                data = extract_salary_slip(text)
                profile["salary_slips"].append(data)
                cursor.execute(
                    "INSERT INTO salary_slips (document_id, net_salary) VALUES (?, ?)",
                    (doc_id, data.get("net_salary", 0))
                )

            elif doc_type == "bank_statement":
                data = extract_bank_statement(text)
                profile["bank_statements"].append(data)
                cursor.execute(
                    "INSERT INTO bank_statements (document_id, total_credit) VALUES (?, ?)",
                    (doc_id, data.get("total_credit", 0))
                )

    conn.commit()

    print("\n🚨 Running Red Flag Engine...\n")
    print("Salary Slips Count:", len(profile["salary_slips"]))
    print("Bank Statements Count:", len(profile["bank_statements"]))
    print("Total Salary:",
      sum([s.get("net_salary", 0) for s in profile["salary_slips"]]))
    print("Total Bank Credits:",
      sum([b.get("total_credit", 0) for b in profile["bank_statements"]]))
    risk = run_red_flags(profile)

    for flag in risk["flags"]:
        cursor.execute("""
        INSERT INTO risk_reports (
            risk_score,
            risk_level,
            flag,
            severity,
            explanation,
            source
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            risk["risk_score"],
            risk["risk_level"],
            flag["flag"],
            flag["severity"],
            flag["explanation"],
            flag["source"]
        ))

    conn.commit()
    conn.close()

    print("✅ Risk Pipeline Completed Successfully")


if __name__ == "__main__":
    main()