# api/v1/routers/analysis.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from langgraph.graph import END
from sse_starlette.sse import EventSourceResponse
import json

from api.v1.schemas.analysis import AnalysisResponse
from graph.workflow import graph_app

router = APIRouter()

SUPPORTED_FILE_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}

async def analysis_event_generator(initial_state: dict):
    """
    This generator streams the progress of the LangGraph execution.
    """
    async for event in graph_app.astream(initial_state):
        # The 'event' dictionary has keys corresponding to the node that just finished
        for node_name, node_output in event.items():
            if node_name == "aggregate_results":
                # This is the final state of the graph
                final_state = node_output
                final_result = AnalysisResponse(
                    relevance_score=final_state["final_score"],
                    missing_keywords=final_state["hard_analysis"]["missing_keywords"],
                    verdict=final_state["final_verdict"],
                    suggestions=final_state["final_suggestions"]
                )
                # Yield the final, complete result
                yield json.dumps({"event": "final_result", "data": final_result.model_dump()})
                return # Stop the generator

            # Yield a progress update for the completed node
            progress_update = {
                "event": "progress",
                "data": { "step": node_name, "progress": node_output.get("progress", []) }
            }
            yield json.dumps(progress_update)

@router.post("/analyze-stream")
async def analyze_resume_stream(
    resume: UploadFile = File(..., description="The user's resume file (pdf, docx, or txt)."),
    job_description: str = Form(..., description="The job description text.")
):
    """
    Analyzes a resume against a job description and streams the progress.
    
    The client will receive a stream of Server-Sent Events (SSE).
    - **Progress events**: `{"event": "progress", "data": {"step": "...", "progress": [...]}}`
    - **Final result event**: `{"event": "final_result", "data": { ...AnalysisResponse... }}`
    """
    # 1. Validate file type
    file_type = resume.content_type
    if file_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Please upload a PDF, DOCX, or TXT file."
        )
    
    # 2. Prepare initial state for the graph
    file_content = await resume.read()
    initial_state = {
        "resume_file_content": file_content,
        "file_format": SUPPORTED_FILE_TYPES[file_type],
        "job_description": job_description,
        "progress": []
    }

    # 3. Return the streaming response
    return EventSourceResponse(analysis_event_generator(initial_state))