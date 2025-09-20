# api/v1/routers/analysis.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from api.v1.schemas.analysis import AnalysisResponse
from services import analysis_service

router = APIRouter()

SUPPORTED_FILE_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume: UploadFile = File(..., description="The user's resume file (pdf, docx, or txt)."),
    job_description: str = Form(..., description="The job description text.")
):
    """
    Analyzes a resume against a job description and returns a comprehensive analysis.
    """
    # Validate file type
    file_type = resume.content_type
    if file_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Please upload a PDF, DOCX, or TXT file."
        )

    file_format = SUPPORTED_FILE_TYPES[file_type]

    try:
        result = analysis_service.analyze_resume_against_jd(
            resume_file=resume,
            file_format=file_format,
            job_description=job_description
        )
        return result
    except Exception as e:
        # Log the exception e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )