import textstat

def calculate_readability(text):
    """
    Calculate readability scores using textstat.
    Returns Flesch-Kincaid Grade and Gunning Fog Index.
    """
    if not text or not text.strip():
        return {
            "flesch_kincaid_grade": 0,
            "gunning_fog": 0,
            "complexity_level": "N/A"
        }
        
    fk_grade = textstat.flesch_kincaid_grade(text)
    gunning_fog = textstat.gunning_fog(text)
    
    # Simple complexity mapping based on FK Grade
    if fk_grade < 8:
        complexity = "Easy"
    elif fk_grade < 12:
        complexity = "Medium"
    elif fk_grade < 16:
        complexity = "Difficult"
    else:
        complexity = "Very Difficult (Legal/Academic)"
        
    return {
        "flesch_kincaid_grade": fk_grade,
        "gunning_fog": gunning_fog,
        "complexity_level": complexity
    }

def analyze_word_complexity(text):
    """
    Analyze word complexity based on syllable count and length.
    Returns a list of dictionaries with word and complexity level.
    """
    import re
    
    if not text:
        return []
        
    # Split by space to preserve basic structure, but we need to handle punctuation
    # A simple approach: tokenize but keep track of non-tokens?
    # For now, let's just return a list of tokens with their complexity.
    # The frontend can reconstruct or we can just return the marked up segments.
    # actually, to highlight in place, we need to map back to original text or just return a list of (word, type) tuples including whitespace/punctuation.
    
    # Better approach for "heatmap": 
    # Tokenize preserving whitespace and punctuation
    tokens = re.findall(r'\S+|\s+', text)
    
    result = []
    
    for token in tokens:
        # Check if it's a word (contains letters)
        if re.search(r'[a-zA-Z]', token):
            # Clean for analysis (remove punctuation)
            clean_token = re.sub(r'[^\w\s]', '', token)
            syllables = textstat.syllable_count(clean_token)
            length = len(clean_token)
            
            if syllables >= 3:
                complexity = "complex"
            elif length > 7:
                 complexity = "medium"
            else:
                complexity = "simple"
                
            result.append({"text": token, "complexity": complexity})
        else:
            # Punctuation or whitespace
            result.append({"text": token, "complexity": "none"})
            
    return result
