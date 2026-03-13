import pdfplumber

def extract_pdf(file):
    filename = file.filename.lower()
    

    
    file.file.seek(0)
    
    if filename.endswith(".txt"):
        content = file.file.read().decode("utf-8")
        return content

    elif filename.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    else:
        raise ValueError("Unsupported file type. Only PDF and TXT are allowed.")