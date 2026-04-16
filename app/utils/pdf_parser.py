import pdfplumber


def extract_text_from_pdf(file_path: str) -> str:
    full_text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if text:
                full_text += text + "\n"

    return full_text.strip()