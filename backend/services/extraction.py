# services/extraction.py
import pdfplumber
import docx2txt
from fastapi import UploadFile
import io

def extract_text_from_file(file: UploadFile, file_format: str) -> str:
    """
    Extracts text from an uploaded file based on its format.
    
    Args:
        file: The uploaded file object from FastAPI.
        file_format: The format of the file ('pdf', 'txt', 'docx').

    Returns:
        The extracted text as a string.
    """
    text = ""
    file_bytes = file.file.read()

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