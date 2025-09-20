# services/normalization.py
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Ensure NLTK data is downloaded. You only need to run this once.
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

def normalize_text(text: str) -> str:
    """
    Normalizes a given text string using NLTK.
    - Tokenizes, removes stop words, and lemmatizes.
    
    Args:
        text: The input string to normalize.
        
    Returns:
        A normalized string.
    """
    # 1. Tokenize
    tokens = word_tokenize(text)
    
    # 2. Lowercase and remove punctuation/non-alphabetic characters
    words = [word.lower() for word in tokens if word.isalpha()]
    
    # 3. Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    
    # 4. Lemmatize
    lemmatizer = WordNetLemmatizer()
    lemmas = [lemmatizer.lemmatize(word) for word in filtered_words]
    
    return " ".join(lemmas)