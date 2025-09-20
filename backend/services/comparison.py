# services/comparison.py
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from core.config import settings

def hard_compare(resume_text: str, jd_text: str) -> dict:
    """
    Hard compares the resume and job description for keyword matches.
    
    Returns:
        A dictionary with a score and missing keywords.
    """
    print("Performing hard comparison...")
    # Placeholder Logic: Implement your keyword matching logic here.
    # For now, we'll return a dummy response.
    jd_keywords = {"python", "fastapi", "sql", "docker", "communication"}
    resume_words = set(resume_text.split())
    
    found_keywords = jd_keywords.intersection(resume_words)
    missing_keywords = list(jd_keywords - found_keywords)
    
    score = (len(found_keywords) / len(jd_keywords)) * 100 if jd_keywords else 0
    
    return {"score": score, "missing_keywords": missing_keywords}

def soft_compare_langchain(resume_text: str, jd_text: str) -> str:
    """
    Uses LangChain with a Google GenAI model for semantic analysis.
    
    Returns:
        A string containing the model's analysis.
    """
    print("Performing soft comparison with LangChain...")
    # 1. Initialize the model
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=settings.GOOGLE_API_KEY)
    
    # 2. Create a prompt template
    template = """
    Analyze the following resume and job description. Provide a brief, one-paragraph analysis
    on how well the resume aligns with the job requirements.
    
    JOB DESCRIPTION:
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

def get_embedding_fit_score(resume_text: str, jd_text: str) -> int:
    """
    Calculates a fit score based on the cosine similarity of text embeddings.
    
    Returns:
        A score between 0 and 100.
    """
    print("Calculating embedding fit score...")
    # 1. Initialize the embedding model
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GOOGLE_API_KEY)
    
    # 2. Get embeddings for both texts
    resume_embedding = embeddings.embed_query(resume_text)
    jd_embedding = embeddings.embed_query(jd_text)
    
    # 3. Calculate cosine similarity and scale to 0-100
    # Reshape for sklearn's cosine_similarity function
    resume_vec = np.array(resume_embedding).reshape(1, -1)
    jd_vec = np.array(jd_embedding).reshape(1, -1)
    
    similarity = cosine_similarity(resume_vec, jd_vec)[0][0]
    
    # Scale from [-1, 1] to [0, 100]
    score = int((similarity + 1) / 2 * 100)
    
    return score