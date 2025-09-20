# main.py
from fastapi import FastAPI
from api.v1.routers import analysis as analysis_v1

app = FastAPI(
    title="Resume Analyzer API",
    description="An API to analyze resumes against job descriptions using AI.",
    version="1.0.0"
)

# Include the API router
app.include_router(analysis_v1.router, prefix="/api/v1", tags=["Analysis"])

@app.get("/", tags=["Root"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Welcome to the Resume Analyzer API!"}