from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
from nltk.tokenize import sent_tokenize

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

def simplify_text(text: str, level: int = 70, simplification_mode: str = "intermediate") -> str:
    """Simplifies the given text using FLAN-T5 with chunking for large documents.
    
Args:
    text (str): Input text to simplify
    level (int): Simplification intensity (1-100)
    simplification_mode (str): Simplification level - 'basic', 'intermediate', or 'advanced'
        - basic: Minimal changes, preserve legal terminology
        - intermediate: Balanced simplification (default)
        - advanced: Maximum simplification, very simple language
    
Returns:
    str: Simplified text
"""
    if not model or not tokenizer:
        return "Model not loaded properly."
    if not text.strip():
        return ""
    
    # Import chunking module
    from nlp.chunking import is_large_document, process_large_document
    
    # Check if document is large (> 500 tokens)
    if is_large_document(text, threshold_tokens=500):
        print(f"Large document detected. Processing in chunks...")
        
        # Process large document in chunks
        def simplify_chunk(chunk):
             return _simplify_single_chunk(chunk, level, simplification_mode)
        
        # Use chunking with max 400 tokens per chunk
        simplified = process_large_document(text, simplify_chunk, max_tokens=400)
        return simplified
    else:
        # Process normally for small documents
        return _simplify_single_chunk(text, level, simplification_mode)

def _simplify_single_chunk(text: str, level: int = 70, simplification_mode: str = "intermediate") -> str:
    # Scale between 40 (shortest) and 350 (longest limit)
    mapped_max_tokens = int(max(40, 350 - (level * 2)))

    # Multi-level simplification prompts
    if simplification_mode == "basic":
        # Basic: Minimal changes, preserve most original wording
        if level > 80:
            prompt = f"Slightly rephrase this text for easier reading, keeping most original words: {text}"
        elif level > 40:
            prompt = f"Make this text a bit clearer while keeping the legal language mostly intact: {text}"
        else:
            prompt = f"Improve clarity of this text with minimal changes: {text}"
        max_tokens_override = int(mapped_max_tokens * 1.2)  # Allow longer output for basic
        
    elif simplification_mode == "advanced":
        # Advanced: Maximum simplification, very simple language
        if level > 80:
            prompt = f"Rewrite this in the simplest possible words, as if explaining to a 10-year-old child: {text}"
        elif level > 40:
            prompt = f"Translate this legal text into extremely simple everyday language that anyone can understand: {text}"
        else:
            prompt = f"Simplify this text dramatically using only common, everyday words: {text}"
        max_tokens_override = int(mapped_max_tokens * 0.8)  # Shorter output for advanced
        
    else:  # intermediate (default)
        # Intermediate: Balanced simplification
        if level > 80:
            prompt = f"Rewrite this text using simple words so a general audience can understand: {text}"
        elif level > 40:
            prompt = f"Simplify the following text so it is easy to read for the general public: {text}"
        else:
            prompt = f"Rephrase the following text to improve clarity while keeping important details: {text}"
        max_tokens_override = mapped_max_tokens

    inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
    outputs = model.generate(
        **inputs, 
        max_new_tokens=max_tokens_override, 
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def _extractive_summary(text: str, num_sentences: int = 3) -> str:
    """Fallback extractive summarizer picking the most important sentences."""
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text
    
    # Simple heuristic: first sentence, middle sentence, last sentence
    idx = [0, len(sentences)//2, len(sentences)-1]
    return " ".join([sentences[i] for i in sorted(list(set(idx)))])

def summarize_text(text: str) -> str:
    """Summarizes the given text using FLAN-T5 with chunking for large documents."""
    if not text.strip():
        return ""
        
    sentences = sent_tokenize(text)
    # If the text is very short already, just return it or simplify it slightly
    if len(sentences) <= 2:
        return text

    if not model or not tokenizer:
        return _extractive_summary(text)
    
    # Import chunking
    from nlp.chunking import is_large_document, chunk_text
    
    # For large documents, summarize in chunks then combine
    if is_large_document(text, threshold_tokens=600):
        print(f"Large document detected for summarization. Processing in chunks...")
        chunks = chunk_text(text, max_tokens=500)
        
        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            summary = _summarize_single_chunk(chunk)
            if summary:
                chunk_summaries.append(summary)
        
        # Combine chunk summaries
        combined = ' '.join(chunk_summaries)
        
        # If combined is still long, summarize again
        if len(combined.split()) > 200:
            return _summarize_single_chunk(combined)
        return combined
    else:
        return _summarize_single_chunk(text)

def _summarize_single_chunk(text: str) -> str:
    """Internal function to summarize a single chunk."""
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