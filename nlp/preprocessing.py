import spacy
import re

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
    Tokenize text using SpaCy.
    """
    if not text:
        return []

    doc = nlp(text)
    return [token.text for token in doc]


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
