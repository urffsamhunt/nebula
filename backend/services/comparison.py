# services/comparison.py
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from core.config import settings
from thefuzz import process

def hard_compare(resume_keywords: list, jd_keywords: list) -> dict:
    """
    Hard compares the resume and job description using fuzzy keyword matching.
    
    Returns:
        A dictionary with a score and missing keywords.
    """
    print("Performing fuzzy hard comparison...")

    # A similarity score of 85+ is generally a good match for technical terms.
    # This value can be tuned as needed.
    SIMILARITY_THRESHOLD = 85

    # 1. Tokenize the inputs into unique sets of keywords.
    # The jd_text and resume_text are expected to be pre-processed,
    # space-separated strings of keywords from the normalization step.

    # Handle the edge case where there are no keywords to compare.
    if not jd_keywords:
        return {"score": 0, "missing_keywords": []}
    if not resume_keywords:
        return {"score": 0, "missing_keywords": list(jd_keywords)}

    found_keywords = set()
    missing_keywords = set()

    # 2. Iterate through each required keyword from the job description.
    for keyword in jd_keywords:
        # 3. Find the best fuzzy match for the keyword within the resume.
        # process.extractOne returns a tuple: (best_match, score)
        best_match = process.extractOne(keyword, resume_keywords)
        
        # 4. If a sufficiently good match is found, count it.
        if best_match and best_match[1] >= SIMILARITY_THRESHOLD:
            found_keywords.add(keyword)
        else:
            missing_keywords.add(keyword)

    # 5. Calculate the final score based on found keywords.
    score = (len(found_keywords) / len(jd_keywords)) * 100 if jd_keywords else 0
    
    print(f"Found keywords (fuzzy): {found_keywords}")
    print(f"Missing keywords (fuzzy): {missing_keywords}")
    
    return {"score": score, "missing_keywords": sorted(list(missing_keywords))}




def soft_compare_langchain(resume_text: str, jd_text: str) -> str:
    """
    Uses LangChain with a Google GenAI model for semantic analysis.
    
    Returns:
        A string containing the model's analysis.
    """
    print("Performing soft comparison with LangChain...")
    # 1. Initialize the model
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY)
    
    # 2. Create a prompt template
    template = """
    Analyze the following resume and job description. Provide a brief, one-paragraph analysis
    on how well the resume aligns with the job requirements.
    
    JOB DESCRIP TION:
    {job_description}
    
    RESUME:
    {resume}
    
    ANALYSIS:
    """
    prompt = PromptTemplate.from_template(template)
    
    # 3. Create the chain and invoke
    chain = prompt | llm
    result = chain.invoke({"job_description": jd_text, "resume": resume_text})
    
    return result.content

def get_embedding_fit_score(resume_keywords: list[str], jd_keywords: list[str]) -> int:
    """
    Calculates a "strict" fit score by ensuring each keyword in the job description
    has a semantically similar counterpart in the resume. This version iterates
    to stay within free-tier API limits and applies a penalty to non-perfect
    matches to "widen the gap" between scores.
    """
    print("Calculating strict embedding fit score (widened gap)...")
    
    if not jd_keywords or not resume_keywords:
        return 0

    try:
        # 1. Initialize the embedding model with the correct API identifier.
        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", google_api_key=settings.GOOGLE_API_KEY)
        
        # 2. Use embed_query in a loop to process keywords one by one.
        jd_embeddings = embeddings.embed_document(jd_keywords)
        resume_embeddings = embeddings.embed_document(resume_keywords)

        jd_vecs = np.array(jd_embeddings)
        resume_vecs = np.array(resume_embeddings)

        # 3. For each JD keyword, find its best match and apply a penalty.
        # This avoids creating the full similarity matrix at once.
        penalized_scores = []
        for jd_vec in jd_vecs:
            # Compare one JD vector against all resume vectors
            similarities = cosine_similarity(jd_vec.reshape(1, -1), resume_vecs)[0]
            
            # Find the best match score for the current JD keyword
            best_match_score = np.max(similarities)
            
            # --- "WIDEN THE GAP" ---
            # Apply an exponential penalty. Squaring the score (power of 2)
            # punishes scores below 1.0 more heavily.
            # e.g., a 0.9 similarity becomes 0.81, but a 0.7 similarity drops to 0.49.
            # A higher exponent (e.g., 3) would be even stricter.
            penalized_score = best_match_score ** 2
            penalized_scores.append(penalized_score)

        # 4. The final score is the average of these penalized best-match scores.
        average_penalized_similarity = np.mean(penalized_scores)
        
        # 5. Scale the score to the 0-100 range.
        # Since cosine similarity for these embeddings is in the [0, 1] range,
        # we can directly scale the result by 100.
        score = int(average_penalized_similarity * 100)
        
        print(f"Strict embedding score (widened): {score}")
        return score
        
    except Exception as e:
        print(f"Error calculating embedding fit score: {e}")
        # Return a default score of 0 if the embedding service fails
        return 0

def get_final_verdict_and_suggestions(score: int, hard_analysis: dict, soft_analysis: str) -> dict:
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
    Please provide concise, actionable suggestions for the candidate to improve their resume.
    SUGGESTIONS:
    """
    
    suggestions = llm.invoke(prompt).content
    return {"verdict": verdict_category, "suggestions": suggestions}