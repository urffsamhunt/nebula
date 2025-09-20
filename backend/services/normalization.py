# services/normalization.py
# (This file remains the same as the original answer)
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def normalize_text(text: str) -> str:
    tokens = word_tokenize(text)
    words = [word.lower() for word in tokens if word.isalpha()]
    print(f"Tokens after isalpha filter: {words}")
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    return filtered_words