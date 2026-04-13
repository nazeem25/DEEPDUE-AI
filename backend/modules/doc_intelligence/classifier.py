def classify_document(text, source_hint=None):
    """
    Simple rule-based document classifier
    """

    text = text.lower() if text else ""

    # Folder hint priority
    if source_hint:
        if "salary" in source_hint:
            return "salary_slip"
        if "bank" in source_hint:
            return "bank_statement"

    # Keyword based detection
    if "net salary" in text or "gross salary" in text:
        return "salary_slip"

    if "account number" in text or "closing balance" in text:
        return "bank_statement"

    return "unknown"
if __name__ == "__main__":
    from backend.modules.doc_intelligence.text_loader import load_text
    text = load_text("data/salary_slip/1.jpg")
    label = classify_document(text)
    print("Document Type:", label)