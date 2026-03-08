import spacy
import re
import nltk
from nltk.tokenize import word_tokenize

# Ensure required NLTK data is available (do not download during runtime)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    raise LookupError(
        "NLTK resource 'punkt' not found. Please install it during build with: nltk.download('punkt')"
    )

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    raise LookupError(
        "NLTK resource 'stopwords' not found. Please install it during build with: nltk.download('stopwords')"
    )

# Load SpaCy model (must be installed in requirements.txt)
try:
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
except OSError:
    raise OSError(
        "SpaCy model 'en_core_web_sm' is not installed. "
        "Install it by adding it to requirements.txt."
    )


def clean_text(text):
    """
    Clean text by removing extra whitespace.
    """
    if not text:
        return ""

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
    Returns cleaned text, sentences, and tokens.
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
