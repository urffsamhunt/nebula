# services/analysis_service.py
from fastapi import UploadFile
from api.v1.schemas.analysis import AnalysisResponse
from services import extraction, normalization, comparison
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings


def get_final_verdict_and_suggestions(score: int, hard_analysis: dict, soft_analysis: str) -> dict:
    """
    Uses Gemini to generate a final verdict and suggestions based on all analysis.
    """
    print("Generating final verdict and suggestions...")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY)
    
    if score >= 75:
        verdict_category = "High"
    elif score >= 50:
        verdict_category = "Medium"
    else:
        verdict_category = "Low"

    prompt = f"""
    Given the following analysis of a resume against a job description:
    - Overall Relevance Score: {score}/100
    - Missing Keywords: {', '.join(hard_analysis['missing_keywords'])}
    - Semantic Analysis: "{soft_analysis}"
    - Verdict Category: {verdict_category} suitability

    Please provide concise, actionable suggestions for the candidate to improve their resume for this specific job.
    Focus on what they should add or highlight. Frame the suggestions positively.
    
    SUGGESTIONS:
    """
    
    suggestions = llm.invoke(prompt).content
    
    return {"verdict": verdict_category, "suggestions": suggestions}


def analyze_resume_against_jd(resume_file: UploadFile, file_format: str, job_description: str) -> AnalysisResponse:
    """
    Orchestrates the entire resume analysis process.
    """
    # 1. Extract text from the resume file
    resume_text = extraction.extract_text_from_file(resume_file, file_format)
    
    # 2. Normalize both the resume and job description text
    normalized_resume = normalization.normalize_text(resume_text)
    normalized_jd = normalization.normalize_text(job_description)
    
    # 3. Perform hard comparison for keyword matching
    hard_analysis = comparison.hard_compare(normalized_resume, normalized_jd)
    
    # 4. Perform soft comparison using LangChain for semantic understanding
    soft_analysis = comparison.soft_compare_langchain(resume_text, job_description)
    
    # 5. Get embedding-based fit score
    embedding_score = comparison.get_embedding_fit_score(resume_text, job_description)
    
    # 6. Calculate a final weighted score (example weights)
    final_score = int(0.6 * embedding_score + 0.4 * hard_analysis['score'])

    # 7. Generate final verdict and suggestions using the LLM
    final_result = get_final_verdict_and_suggestions(final_score, hard_analysis, soft_analysis)
    
    # 8. Assemble the final response
    return AnalysisResponse(
        relevance_score=final_score,
        missing_keywords=hard_analysis['missing_keywords'],
        verdict=final_result['verdict'],
        suggestions=final_result['suggestions']
    )