import logging
import os
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# -------------------------------
# Hugging Face environment setup
# -------------------------------
os.environ["HF_HOME"] = "/data"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

# -------------------------------
# Logging setup
# -------------------------------
logging.basicConfig(level=logging.DEBUG)

# -------------------------------
# Simple sentence tokenizer
# -------------------------------
def sent_tokenize(text):
    return re.split(r'(?<=[.!?]) +', text)

# -------------------------------
# Model setup
# -------------------------------
_MODEL_DIR = "google/flan-t5-small"

logging.info(f"Loading FLAN-T5 model from Hugging Face hub ({_MODEL_DIR})...")

try:
    print("Downloading and loading FLAN-T5 model...")

    tokenizer = AutoTokenizer.from_pretrained(
        _MODEL_DIR,
        local_files_only=False
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(
        _MODEL_DIR,
        local_files_only=False
    )

    model.to("cpu")

    print("Model loaded successfully.")
    logging.info("Model loaded successfully.")

except Exception as e:
    logging.exception("Error loading model")
    tokenizer = None
    model = None

# -------------------------------
# Simplification functions
# -------------------------------
def simplify_text(text: str, level: int = 70, simplification_mode: str = "intermediate") -> str:
    if not model or not tokenizer:
        return "Model not loaded properly."
    if not text.strip():
        return ""

    try:
        from nlp.chunking import is_large_document, process_large_document
    except Exception as e:
        logging.exception("Error importing chunking utilities")
        return text

    if is_large_document(text, threshold_tokens=500):
        def simplify_chunk(chunk):
            return _simplify_single_chunk(chunk, level, simplification_mode)
        simplified = process_large_document(text, simplify_chunk, max_tokens=400)
        return simplified
    else:
        return _simplify_single_chunk(text, level, simplification_mode)


def _simplify_single_chunk(text: str, level: int = 70, simplification_mode: str = "intermediate") -> str:
    mapped_max_tokens = int(max(40, 350 - (level * 2)))

    if simplification_mode == "basic":
        prompt = f"Slightly rephrase this text for easier reading, keeping most original words: {text}"
        max_tokens_override = int(mapped_max_tokens * 1.2)
    elif simplification_mode == "advanced":
        prompt = f"Rewrite this in the simplest possible words, as if explaining to a 10-year-old: {text}"
        max_tokens_override = int(mapped_max_tokens * 0.8)
    else:
        prompt = f"Rewrite this text using simple words for general audience: {text}"
        max_tokens_override = mapped_max_tokens

    try:
        inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)

        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens_override,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )

        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    except Exception as e:
        logging.exception("Error during simplification generation")
        return text


# -------------------------------
# Summarization functions
# -------------------------------
def _extractive_summary(text: str, num_sentences: int = 3) -> str:
    sentences = sent_tokenize(text)

    if len(sentences) <= num_sentences:
        return text

    idx = [0, len(sentences)//2, len(sentences)-1]

    return " ".join([sentences[i] for i in sorted(list(set(idx)))])


def summarize_text(text: str) -> str:
    if not text.strip():
        return ""

    if not model or not tokenizer:
        return _extractive_summary(text)

    try:
        from nlp.chunking import is_large_document, chunk_text
    except Exception as e:
        logging.exception("Error importing chunking utilities")
        return _extractive_summary(text)

    if is_large_document(text, threshold_tokens=600):

        chunks = chunk_text(text, max_tokens=500)
        chunk_summaries = []

        for chunk in chunks:
            summary = _summarize_single_chunk(chunk)

            if summary:
                chunk_summaries.append(summary)

        combined = ' '.join(chunk_summaries)

        if len(combined.split()) > 200:
            return _summarize_single_chunk(combined)

        return combined

    else:
        return _summarize_single_chunk(text)


def _summarize_single_chunk(text: str) -> str:
    prompt = f"Write a detailed summary of the following text: {text}"

    try:
        inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)

        outputs = model.generate(
            **inputs,
            max_new_tokens=400,
            min_new_tokens=20,
            length_penalty=2.0,
            num_beams=4,
            do_sample=False
        )

        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

        if len(summary.split()) < 10 and len(text.split()) > 30:
            return _extractive_summary(text)

        return summary

    except Exception as e:
        logging.exception("Error during summarization generation")
        return _extractive_summary(text)