from nltk.tokenize import sent_tokenize
import nltk

# Ensure punkt is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def chunk_text(text, max_tokens=400):
    """
    Split large text into processable chunks based on token limit.
    
    Args:
        text (str): Input text to chunk
        max_tokens (int): Maximum tokens per chunk (default: 400)
    
    Returns:
        list: List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Split into sentences
    sentences = sent_tokenize(text)
    
    chunks = []
    current_chunk = []
    current_token_count = 0
    
    for sentence in sentences:
        # Approximate token count (words)
        sentence_tokens = len(sentence.split())
        
        # If adding this sentence exceeds limit, save current chunk
        if current_token_count + sentence_tokens > max_tokens and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_token_count = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_token_count += sentence_tokens
    
    # Add remaining sentences
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def process_large_document(text, process_func, max_tokens=400):
    """
    Process large documents by chunking and applying function to each chunk.
    
    Args:
        text (str): Large text to process
        process_func (callable): Function to apply to each chunk
        max_tokens (int): Maximum tokens per chunk
    
    Returns:
        str: Combined processed text
    """
    chunks = chunk_text(text, max_tokens)
    
    if not chunks:
        return ""
    
    # Process each chunk
    processed_chunks = []
    for chunk in chunks:
        try:
            processed = process_func(chunk)
            processed_chunks.append(processed)
        except Exception as e:
            print(f"Error processing chunk: {e}")
            # Return original chunk if processing fails
            processed_chunks.append(chunk)
    
    # Combine processed chunks
    return ' '.join(processed_chunks)

def estimate_tokens(text):
    """
    Estimate token count for text.
    
    Args:
        text (str): Input text
    
    Returns:
        int: Estimated token count
    """
    # Rough estimate: 1 token ≈ 0.75 words
    word_count = len(text.split())
    return int(word_count * 1.33)

def is_large_document(text, threshold_tokens=500):
    """
    Check if document is considered large.
    
    Args:
        text (str): Input text
        threshold_tokens (int): Token threshold for "large"
    
    Returns:
        bool: True if large document
    """
    return estimate_tokens(text) > threshold_tokens