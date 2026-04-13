import re

def extract_salary_slip(text):
    """
    Extract net salary from salary slip text
    """

    if not text:
        return {"net_salary": 0}

    text = text.lower()

    # Try to find "net salary"
    match = re.search(r"net\s*salary[:\s]*([\d,]+\.?\d*)", text)

    if match:
        salary = match.group(1).replace(",", "")
        return {"net_salary": float(salary)}

    # Fallback
    return {"net_salary": 0}

if __name__ == "__main__":
    from backend.modules.doc_intelligence.text_loader import load_text
    text = load_text("data/salary_slip/1.jpg")
    data = extract_salary_slip(text)
    print(data)