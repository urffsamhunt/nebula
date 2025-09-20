# graph/nodes.py
from graph.state import GraphState
from services import extraction, normalization, comparison

def extract_text(state: GraphState) -> dict:
    """Extracts text from the resume."""
    print("---NODE: EXTRACTING TEXT---")
    file_content = state["resume_file_content"]
    file_format = state["file_format"]
    
    extracted_text = extraction.extract_text_from_file_content(file_content, file_format)
    
    return {
        "resume_text": extracted_text,
        "progress": ["Text Extracted"]
    }

def normalize_texts(state: GraphState) -> dict:
    """Normalizes the resume and job description text."""
    print("---NODE: NORMALIZING TEXTS---")
    resume_text = state["resume_text"]
    jd_text = state["job_description"]
    
    norm_resume = normalization.normalize_text(resume_text)
    norm_jd = normalization.normalize_text(jd_text)
    
    progress = state["progress"] + ["Texts Normalized"]
    return {
        "normalized_resume": norm_resume,
        "normalized_jd": norm_jd,
        "progress": progress
    }

def run_comparisons(state: GraphState) -> dict:
    """Runs all three comparison methods."""
    print("---NODE: RUNNING COMPARISONS---")
    # Hard comparison uses normalized text
    hard_analysis = comparison.hard_compare(
        state["normalized_resume"], state["normalized_jd"]
    )
    
    # Soft and embedding comparisons use original text for better context
    soft_analysis = comparison.soft_compare_langchain(
        state["resume_text"], state["job_description"]
    )
    embedding_score = comparison.get_embedding_fit_score(
        state["resume_text"], state["job_description"]
    )

    progress = state["progress"] + ["Comparisons Complete"]
    return {
        "hard_analysis": hard_analysis,
        "soft_analysis": soft_analysis,
        "embedding_score": embedding_score,
        "progress": progress
    }

def aggregate_results(state: GraphState) -> dict:
    """Aggregates scores and generates the final verdict and suggestions."""
    print("---NODE: AGGREGATING RESULTS---")
    embedding_score = state["embedding_score"]
    hard_score = state["hard_analysis"]["score"]

    # Simple weighted average for final score
    final_score = int(0.6 * embedding_score + 0.4 * hard_score)
    
    final_result = comparison.get_final_verdict_and_suggestions(
        score=final_score,
        hard_analysis=state["hard_analysis"],
        soft_analysis=state["soft_analysis"]
    )
    print(final_result)
    progress = state["progress"] + ["Aggregation Complete"]
    return {
        "final_score": final_score,
        "final_verdict": final_result["verdict"],
        "final_suggestions": final_result["suggestions"],
        "progress": progress,
        "hard_analysis": state["hard_analysis"],
    }