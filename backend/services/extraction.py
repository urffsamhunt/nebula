# services/extraction.py
import pdfplumber
import docx2txt
import io

def extract_text_from_file_content(file_bytes: bytes, file_format: str) -> str:
    """Extracts text from file content bytes based on its format."""
    text = ""
    if file_format == 'pdf':
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif file_format == 'docx':
        text = docx2txt.process(io.BytesIO(file_bytes))
    elif file_format == 'txt':
        text = file_bytes.decode('utf-8')
    else:
        raise ValueError("Unsupported file format")
    return text