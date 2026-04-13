import numpy as np
import math
from collections import Counter
from sklearn.ensemble import IsolationForest


def safe_number(value):
    try:
        return float(value)
    except:
        return 0.0


def first_digit(n):
    n = abs(int(n))
    while n >= 10:
        n //= 10
    return n


def run_red_flags(profile):
    flags = []
    risk_score = 0

    salary_data = profile.get("salary_slips", [])
    bank_data = profile.get("bank_statements", [])

    total_salary = sum(safe_number(s.get("net_salary")) for s in salary_data)
    total_bank = sum(safe_number(b.get("total_credit")) for b in bank_data)

    print("DEBUG TOTAL SALARY:", total_salary)
    print("DEBUG TOTAL BANK:", total_bank)

    # --------------------------------------------------
    # 1️⃣ INCOME MISMATCH CHECK
    # --------------------------------------------------
    if total_salary > 0 and total_bank > 0:
        mismatch_ratio = abs(total_salary - total_bank) / max(total_salary, total_bank)

        print("DEBUG MISMATCH RATIO:", mismatch_ratio)

        if mismatch_ratio > 0.30:
            flags.append({
                "flag": "Income Mismatch",
                "severity": "HIGH",
                "explanation": "Bank credits significantly differ from declared salary.",
                "source": "Rule Engine"
            })
            risk_score += 30

    # --------------------------------------------------
    # 2️⃣ ISOLATION FOREST
    # --------------------------------------------------
    salary_values = [safe_number(s.get("net_salary")) for s in salary_data]

    if len(salary_values) > 5:
        model = IsolationForest(contamination=0.15, random_state=42)
        preds = model.fit_predict(np.array(salary_values).reshape(-1, 1))

        if -1 in preds:
            flags.append({
                "flag": "Anomalous Salary Pattern",
                "severity": "HIGH",
                "explanation": "Isolation Forest detected abnormal salary values.",
                "source": "ML - Isolation Forest"
            })
            risk_score += 25

    # --------------------------------------------------
    # 3️⃣ BENFORD'S LAW
    # --------------------------------------------------
    first_digits = []

    for b in bank_data:
        value = safe_number(b.get("total_credit"))
        if value > 0:
            first_digits.append(first_digit(value))

    if len(first_digits) > 10:
        digit_count = Counter(first_digits)
        total = len(first_digits)

        expected = {d: math.log10(1 + 1/d) for d in range(1, 10)}

        deviation = 0
        for d in range(1, 10):
            observed = digit_count.get(d, 0) / total
            deviation += abs(observed - expected[d])

        print("DEBUG BENFORD DEVIATION:", deviation)

        if deviation > 0.5:
            flags.append({
                "flag": "Benford Law Deviation",
                "severity": "MEDIUM",
                "explanation": "Digit distribution deviates from Benford's Law.",
                "source": "Statistical Model"
            })
            risk_score += 20

    # --------------------------------------------------
    # FINAL RISK LEVEL
    # --------------------------------------------------
    if risk_score >= 60:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": min(risk_score, 100),
        "risk_level": risk_level,
        "flags": flags
    }

