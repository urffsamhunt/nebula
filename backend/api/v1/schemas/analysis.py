# api/v1/schemas/analysis.py
from pydantic import BaseModel, Field
from typing import List

class AnalysisResponse(BaseModel):
    """Defines the structure of the final JSON response."""
    relevance_score: int = Field(..., description="The overall relevance score from 0 to 100.")
    missing_keywords: List[str] = Field(..., description="A list of important skills or terms missing from the resume.")
    verdict: str = Field(..., description="The final verdict: High, Medium, or Low suitability.")
    suggestions: str = Field(..., description="Suggestions for the candidate to improve their resume for this job.")