import ssl
import certifi
ssl._create_default_https_context = ssl._create_unverified_context
import easyocr
import os

# Initialize OCR reader once
reader = easyocr.Reader(['en'], gpu=False)

def load_text(file_path):
    try:
        if not os.path.exists(file_path):
            print("File not found:", file_path)
            return ""

        results = reader.readtext(file_path, detail=0)
        return " ".join(results)

    except Exception as e:
        print(f"OCR Error for {file_path}: {e}")
        return ""
if __name__ == "__main__":
    text= load_text("data/salary_slip/1.jpg")
    print(text)