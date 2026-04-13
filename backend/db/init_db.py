from backend.db.database import get_connection


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        doc_type TEXT
    )
    """)

    # Salary slips
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS salary_slips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        net_salary REAL
    )
    """)

    # Bank statements
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bank_statements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        total_credit REAL
    )
    """)

    # Risk reports (DROP & RECREATE CLEAN)
    cursor.execute("DROP TABLE IF EXISTS risk_reports")

    cursor.execute("""
    CREATE TABLE risk_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        risk_score INTEGER,
        risk_level TEXT,
        flag TEXT,
        severity TEXT,
        explanation TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")