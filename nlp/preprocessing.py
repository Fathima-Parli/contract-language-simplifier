import spacy
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')

# Load SpaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    """
    Clean text by removing extra whitespace and special characters.
    """
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def segment_sentences(text):
    """
    Segment text into sentences using SpaCy.
    """
    if not text:
        return []
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def tokenize_text(text):
    """
    Tokenize text using NLTK.
    """
    if not text:
        return []
    return word_tokenize(text)

def preprocess_pipeline(text):
    """
    Run full preprocessing pipeline.
    Returns a dictionary with cleaned text, sentences, and tokens.
    """
    cleaned = clean_text(text)
    sentences = segment_sentences(cleaned)
    tokens = tokenize_text(cleaned)
    
    return {
        "cleaned_text": cleaned,
        "sentences": sentences,
        "tokens": tokens,
        "sentence_count": len(sentences),
        "word_count": len(tokens)
    }
