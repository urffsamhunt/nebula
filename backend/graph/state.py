# graph/state.py
from typing import TypedDict, List, Dict, Any
from fastapi import UploadFile

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        resume_file_content: The raw content of the resume file.
        file_format: The format of the file ('pdf', 'txt', 'docx').
        job_description: The job description text.
        resume_text: Extracted text from the resume.
        normalized_resume: Normalized resume text.
        normalized_jd: Normalized job description text.
        hard_analysis: Results from keyword comparison.
        soft_analysis: Results from semantic LLM analysis.
        embedding_score: Score from embedding similarity.
        final_score: The final aggregated score.
        final_verdict: The final verdict (High, Medium, Low).
        final_suggestions: Final improvement suggestions.
        progress: A list to track completed steps.
    """
    resume_file_content: bytes
    file_format: str
    job_description: str
    
    # Fields to be populated by the graph nodes
    resume_text: str
    normalized_resume: str
    normalized_jd: str
    hard_analysis: Dict[str, Any]
    soft_analysis: str
    embedding_score: int
    final_score: int
    final_verdict: str
    final_suggestions: str
    progress: List[str]