import re

def extract_bank_statement(text):
    result = {
        "total_credit": 0.0,
        "total_debit": 0.0,
        "closing_balance": 0.0
    }

    if not text:
        return result

    clean_text = text.replace(",", " ")

    numbers = re.findall(r"\d+\.\d+", clean_text)
    numbers = [float(n) for n in numbers]

    if not numbers:
        return result

    numbers_sorted = sorted(numbers)

    if len(numbers_sorted) >= 1:
        result["closing_balance"] = numbers_sorted[-1]

    if len(numbers_sorted) >= 2:
        result["total_credit"] = numbers_sorted[-2]

    return result
if __name__ == "__main__":
    from backend.modules.doc_intelligence.text_loader import load_text
    text = load_text("data/salary_slip/1.jpg")
    data = extract_bank_statement(text)
    print(data)