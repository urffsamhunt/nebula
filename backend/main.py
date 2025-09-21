# main.py
from fastapi import FastAPI
from api.v1.routers import analysis as analysis_v1
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Resume Analyzer API",
    description="An API to analyze resumes against job descriptions using AI.",
    version="1.0.0"
)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://0.0.0.0:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(analysis_v1.router, prefix="/api/v1", tags=["Analysis"])

@app.get("/", tags=["Root"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Welcome to the Resume Analyzer API!"}