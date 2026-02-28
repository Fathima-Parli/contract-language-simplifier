from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

_model_name = "google/flan-t5-base"
print(f"Loading FLAN-T5 model ({_model_name}) directly from weights...")

try:
    tokenizer = AutoTokenizer.from_pretrained(_model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(_model_name)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    tokenizer = None
    model = None

def simplify_text(text: str, level: int = 70) -> str:
    """Simplifies the given text using FLAN-T5. 
    Level (1-100) controls how brief the output is.
    Higher level = Simpler/Shorter length. Lower level = Closer to original length.
    """
    if not model or not tokenizer:
        return "Model not loaded properly."
    if not text.strip():
        return ""
    
    # Scale between 40 (shortest) and 350 (longest limit)
    mapped_max_tokens = int(max(40, 350 - (level * 2)))

    if level > 80:
        prompt = f"Rewrite this text using extremely simple words so a child can understand: {text}"
    elif level > 40:
        prompt = f"Simplify the following text so it is easy to read for the general public: {text}"
    else:
        prompt = f"Slightly rephrase the following text to improve clarity, keeping all details: {text}"

    inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
    outputs = model.generate(
        **inputs, 
        max_new_tokens=mapped_max_tokens, 
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

import nltk
from nltk.tokenize import sent_tokenize

def _extractive_summary(text: str, num_sentences: int = 3) -> str:
    """Fallback extractive summarizer picking the most important sentences."""
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text
    
    # Simple heuristic: first sentence, middle sentence, last sentence
    idx = [0, len(sentences)//2, len(sentences)-1]
    return " ".join([sentences[i] for i in sorted(list(set(idx)))])

def summarize_text(text: str) -> str:
    """Summarizes the given text using FLAN-T5 with an extractive fallback."""
    if not text.strip():
        return ""
        
    sentences = sent_tokenize(text)
    # If the text is very short already, just return it or simplify it slightly
    if len(sentences) <= 2:
        return text

    if not model or not tokenizer:
        return _extractive_summary(text)
    
    # Use FLAN-T5 for abstractive summarization
    prompt = f"Write a detailed summary of the following text: {text}"
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
    
    # If the model produced something too short, fall back to extractive
    if len(summary.split()) < 10 and len(text.split()) > 30:
        return _extractive_summary(text)
        
    return summary
