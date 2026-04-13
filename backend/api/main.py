from fastapi import FastAPI
from backend.db.database import get_connection

app = FastAPI(title="DeepDue AI API")


@app.get("/")
def root():
    return {"message": "DeepDue AI API Running"}


@app.get("/summary")
def get_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM documents")
    documents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM salary_slips")
    salary_slips = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bank_statements")
    bank_statements = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM risk_reports")
    risk_reports = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(net_salary) FROM salary_slips")
    salary_total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(total_credit) FROM bank_statements")
    bank_total = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "documents": documents,
        "salary_slips": salary_slips,
        "bank_statements": bank_statements,
        "risk_reports": risk_reports,
        "salary_total": salary_total,
        "bank_total": bank_total
    }


@app.get("/risk")
def get_risk():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT risk_score, risk_level
        FROM risk_reports
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "risk_score": row[0],
            "risk_level": row[1]
        }

    return {
        "risk_score": 0,
        "risk_level": "LOW"
    }


@app.get("/flags")
def get_flags():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT flag, severity, explanation, source
        FROM risk_reports
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "flag": r[0],
            "severity": r[1],
            "explanation": r[2],
            "source": r[3]
        }
        for r in rows
    ]