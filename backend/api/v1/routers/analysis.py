# api/v1/routers/analysis.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Path
from sse_starlette.sse import EventSourceResponse
import json
import asyncio
from typing import List, Optional
from api.v1.schemas.analysis import AnalysisResponse
from graph.workflow import graph_app
from core import db

router = APIRouter()

SUPPORTED_FILE_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}
# In api/v1/routers/analysis.py

# ... (imports and other code) ...


async def run_single_analysis(resume: UploadFile, job_description: str) -> dict:
    """
    Runs the full LangGraph analysis for a single resume file and returns the final result.
    """
    try:
        # 1. Validate file type
        file_type = resume.content_type
        if file_type not in SUPPORTED_FILE_TYPES:
            raise ValueError(f"Unsupported file type for {resume.filename}")

        # 2. Prepare initial state for the graph
        file_content = await resume.read()
        initial_state = {
            "resume_file_content": file_content,
            "file_format": SUPPORTED_FILE_TYPES[file_type],
            "job_description": job_description,
            "progress": [],
            "filename": getattr(resume, "filename", None),
        }

        # 3. Invoke the graph and wait for the final result (no streaming)
        final_state = await graph_app.ainvoke(initial_state)

        # 4. Format the successful result
        final_result = AnalysisResponse(
            relevance_score=final_state["final_score"],
            missing_keywords=final_state["hard_analysis"]["missing_keywords"],
            verdict=final_state["final_verdict"],
            suggestions=final_state["final_suggestions"]
        )

        # Persist the evaluation result to the database in a thread to avoid blocking the event loop
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                db.save_evaluation,
                getattr(resume, "filename", None),
                job_description,
                json.dumps(final_result.model_dump()),
                float(final_result.relevance_score),
                final_result.verdict,
            )
        except Exception:
            # Swallow DB errors so they don't affect the analysis result returned to the client
            pass

        return {
            "filename": resume.filename,
            "status": "success",
            "result": final_result.model_dump()
        }
    except Exception as e:
        # 5. Format the error result
        error_payload = {
            "filename": getattr(resume, "filename", None),
            "status": "error",
            "detail": str(e)
        }
        # Try to persist the error record as well (non-blocking)
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                db.save_evaluation,
                getattr(resume, "filename", None),
                job_description,
                json.dumps(error_payload),
                None,
                None,
            )
        except Exception:
            pass

        return error_payload
    


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
                # Persist the final result to the DB (use executor to avoid blocking)
                try:
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(
                        None,
                        db.save_evaluation,
                        initial_state.get("filename"),
                        initial_state.get("job_description"),
                        json.dumps(final_result.model_dump()),
                        float(final_result.relevance_score),
                        final_result.verdict,
                    )
                except Exception:
                    pass

                # Yield the final, complete result
                yield json.dumps({"event": "final_result", "data": final_result.model_dump()})
                return # Stop the generator

            # Yield a progress update for the completed node
            progress_update = {
                "event": "progress",
                "data": { "step": node_name, "progress": node_output.get("progress", []) }
            }
            yield json.dumps(progress_update)


@router.post("/analyze-batch")
async def analyze_resume_batch(
    resumes: List[UploadFile] = File(..., description="A batch of resume files (pdf, docx, or txt)."),
    job_description: str = Form(..., description="The single job description to compare against.")
):
    """
    Analyzes a batch of resumes against a single job description concurrently.
    Returns a list of results once all analyses are complete.
    """
    # 1. Validate file types before scheduling work
    for r in resumes:
        if r.content_type not in SUPPORTED_FILE_TYPES:
            return {"batch_results": [{"filename": getattr(r, "filename", None), "status": "error", "detail": "Unsupported file type"}]}

    # 2. Limit concurrency to avoid OOM / overloading; configurable via env var
    max_concurrency = 4
    semaphore = asyncio.Semaphore(max_concurrency)

    async def guarded_run(resume_file: UploadFile):
        async with semaphore:
            return await run_single_analysis(resume_file, job_description)

    # 3. Create and run guarded tasks; gather results and handle exceptions per-file
    tasks = [asyncio.create_task(guarded_run(r)) for r in resumes]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Normalize exceptions into result dicts
    normalized = []
    for idx, res in enumerate(results):
        if isinstance(res, Exception):
            normalized.append({
                "filename": getattr(resumes[idx], "filename", None),
                "status": "error",
                "detail": str(res)
            })
        else:
            normalized.append(res)

    return {"batch_results": normalized}



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
        "progress": [],
        "filename": getattr(resume, "filename", None),
    }

    # 3. Return the streaming response
    return EventSourceResponse(analysis_event_generator(initial_state))



@router.post("/save-job-description", status_code=status.HTTP_200_OK)
async def save_job_description(
    company_name: str = Form(..., description="The company name"),
    job_role: str = Form(..., description="The job role/title"),
    description: str = Form(..., description="The job description text to be saved.")
):
    """
    Saves the provided job description for future analysis into sqlite.
    """
    try:
        row_id = db.save_job_description(company_name=company_name, job_role=job_role, description=description)
        saved = db.get_job_description(row_id)
        saved_dict = dict(saved) if saved is not None else None
        return {"message": "Job description saved successfully.", "id": row_id, "saved": saved_dict}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving the job description: {str(e)}"
        )
    


@router.get("/get-job-description/{job_id}", status_code=status.HTTP_200_OK)
async def get_job_description(job_id: int):
    """
    Fetches a saved job description by its ID.
    """
    try:
        saved = db.get_job_description(job_id)
        if saved is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job description with ID {job_id} not found."
            )
        saved_dict = dict(saved)
        return {"job_description": saved_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the job description: {str(e)}"
        )   
    

@router.get("/all-job-descriptions", status_code=status.HTTP_200_OK)
async def all_job_descriptions():
    """
    Fetches all saved job descriptions.
    """
    try:
        all_descriptions = db.get_all_job_description()
        return {"job_descriptions": all_descriptions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching job descriptions: {str(e)}"
        )


@router.get("/job-descriptions")
async def list_job_descriptions():
    """Return all saved job descriptions."""
    try:
        rows = db.get_all_job_description()
        results = [dict(r) for r in rows]
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/job-descriptions/{job_id}")
async def update_job_description(
    job_id: int = Path(..., description="The ID of the job description to update"),
    company_name: str = Form(...),
    job_role: str = Form(...),
    description: str = Form(...),
):
    """Update an existing job description."""
    try:
        updated = db.update_job_description(job_id=job_id, company_name=company_name, job_role=job_role, description=description)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
        saved = db.get_job_description(job_id)
        return {"message": "Updated", "saved": dict(saved) if saved else None}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# New endpoints to fetch saved evaluations
@router.get("/evaluations")
async def list_evaluations():
    """Return all saved evaluations."""
    try:
        rows = db.get_all_evaluations()
        results = []
        for r in rows:
            rd = dict(r)
            # Try to parse result_json into a JSON object for easier consumption
            try:
                rd["result"] = json.loads(rd.pop("result_json")) if rd.get("result_json") else None
            except Exception:
                rd["result"] = rd.pop("result_json")
            results.append(rd)
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/evaluations/{eval_id}")
async def get_evaluation(eval_id: int):
    """Fetch a specific saved evaluation by id."""
    try:
        row = db.get_evaluation(eval_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
        rd = dict(row)
        try:
            rd["result"] = json.loads(rd.pop("result_json")) if rd.get("result_json") else None
        except Exception:
            rd["result"] = rd.pop("result_json")
        return {"data": rd}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
