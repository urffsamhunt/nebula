from pathlib import Path
import sqlite3
from typing import Optional, List
import json

# Database file will be created at the backend/ level next to this package
DB_PATH = Path(__file__).parent.parent / "jobs.db"

# Ensure parent dir exists (it should) and create/connect to the sqlite database
_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.row_factory = sqlite3.Row

def _init_db() -> None:
    """Create the job_descriptions and evaluations tables if they don't exist."""
    with _conn:
        _conn.execute(
            """
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                job_role TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Evaluations table stores the result of each resume analysis
        _conn.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                job_description TEXT,
                result_json TEXT,
                relevance_score REAL,
                verdict TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

_init_db()


def save_job_description(company_name: str, job_role: str, description: str) -> int:
    """Insert a job description and return the inserted row id."""
    with _conn:
        cur = _conn.execute(
            "INSERT INTO job_descriptions (company_name, job_role, description) VALUES (?, ?, ?)",
            (company_name, job_role, description),
        )
        return cur.lastrowid


def get_job_description(job_id: int) -> Optional[sqlite3.Row]:
    """Fetch a saved job description by id."""
    cur = _conn.execute("SELECT * FROM job_descriptions WHERE id = ?", (job_id,))
    return cur.fetchone()


def get_all_job_description() -> list[sqlite3.Row]:
    """Fetch all saved job descriptions."""
    cur = _conn.execute("SELECT * FROM job_descriptions ORDER BY created_at DESC")
    return cur.fetchall()


def update_job_description(job_id: int, company_name: str, job_role: str, description: str) -> bool:
    """Update an existing job description. Returns True if a row was updated."""
    with _conn:
        cur = _conn.execute(
            "UPDATE job_descriptions SET company_name = ?, job_role = ?, description = ? WHERE id = ?",
            (company_name, job_role, description, job_id),
        )
        return cur.rowcount > 0


def list_job_descriptions() -> List[sqlite3.Row]:
    """Return all saved job descriptions."""
    cur = _conn.execute("SELECT * FROM job_descriptions ORDER BY created_at DESC")
    return cur.fetchall()


# New evaluation-related functions
def save_evaluation(filename: Optional[str], job_description: str, result_json: str, relevance_score: Optional[float], verdict: Optional[str]) -> int:
    """Persist an analysis result and return the inserted row id."""
    with _conn:
        cur = _conn.execute(
            "INSERT INTO evaluations (filename, job_description, result_json, relevance_score, verdict) VALUES (?, ?, ?, ?, ?)",
            (filename, job_description, result_json, relevance_score, verdict),
        )
        return cur.lastrowid


def get_evaluation(eval_id: int) -> Optional[sqlite3.Row]:
    """Fetch a saved evaluation by id."""
    cur = _conn.execute("SELECT * FROM evaluations WHERE id = ?", (eval_id,))
    return cur.fetchone()


def get_all_evaluations() -> list[sqlite3.Row]:
    """Fetch all saved evaluations ordered by newest first."""
    cur = _conn.execute("SELECT * FROM evaluations ORDER BY created_at DESC")
    return cur.fetchall()