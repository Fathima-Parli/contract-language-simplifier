"""
Text Cleaning and Normalization Module
Milestone 2 - Task 1: Text cleaning & normalization (NLTK)
Author: Monika
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data on first run
def download_nltk_data():
    """Download necessary NLTK data packages"""
    resources = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            try:
                nltk.data.find(f'corpora/{resource}')
            except LookupError:
                try:
                    nltk.download(resource, quiet=True)
                except:
                    pass

# Download data on module import
download_nltk_data()


class TextCleaner:
    """
    Text cleaning and normalization for legal documents
    Handles whitespace, unicode, special characters, and legal formatting
    """
    
    def __init__(self, remove_stopwords=False, lemmatize=False):
        """
        Initialize TextCleaner
        
        Args:
            remove_stopwords (bool): Whether to remove stopwords
            lemmatize (bool): Whether to lemmatize words
        """
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def clean_text(self, text):
        """
        Clean and normalize text through multiple steps
        
        Args:
            text (str): Raw input text from legal document
            
        Returns:
            str: Cleaned and normalized text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Step 1: Remove extra whitespace
        text = self._remove_extra_whitespace(text)
        
        # Step 2: Normalize unicode characters
        text = self._normalize_unicode(text)
        
        # Step 3: Remove special characters (preserve sentence structure)
        text = self._remove_special_chars(text)
        
        # Step 4: Normalize numbers
        text = self._normalize_numbers(text)
        
        # Step 5: Fix common legal document issues
        text = self._fix_legal_formatting(text)
        
        return text
    
    def _remove_extra_whitespace(self, text):
        """Remove extra spaces, tabs, and newlines"""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
    
    def _normalize_unicode(self, text):
        """Normalize unicode characters (smart quotes, dashes, etc.)"""
        # Replace smart quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        # Replace em dash and en dash
        text = text.replace('—', '-').replace('–', '-')
        # Replace ellipsis
        text = text.replace('…', '...')
        # Remove problematic unicode (keep ASCII)
        text = text.encode('ascii', 'ignore').decode('ascii')
        return text
    
    def _remove_special_chars(self, text):
        """Remove special characters while preserving sentence structure"""
        # Keep: letters, numbers, spaces, periods, commas, semicolons, colons, hyphens, apostrophes
        text = re.sub(r'[^a-zA-Z0-9\s.,;:\-\']', '', text)
        return text
    
    def _normalize_numbers(self, text):
        """Normalize number representations"""
        # Remove commas from numbers (e.g., 1,000 -> 1000)
        text = re.sub(r'(\d),(\d)', r'\1\2', text)
        return text
    
    def _fix_legal_formatting(self, text):
        """Fix common legal document formatting issues"""
        # Fix section numbering (e.g., "Section1.2" -> "Section 1.2")
        text = re.sub(r'Section(\d)', r'Section \1', text, flags=re.IGNORECASE)
        
        # Fix "e.g." and "i.e." 
        text = re.sub(r'e\.g\.', 'for example', text, flags=re.IGNORECASE)
        text = re.sub(r'i\.e\.', 'that is', text, flags=re.IGNORECASE)
        
        # Fix common abbreviations
        text = text.replace('etc.', 'et cetera')
        text = re.sub(r'\bvs\.\b', 'versus', text, flags=re.IGNORECASE)
        
        # Fix multiple periods
        text = re.sub(r'\.{2,}', '.', text)
        
        return text
    
    def advanced_clean(self, text):
        """
        Advanced cleaning with tokenization, stopword removal, and lemmatization
        
        Args:
            text (str): Input text
            
        Returns:
            str: Advanced cleaned text
        """
        # First do basic cleaning
        text = self.clean_text(text)
        
        # Tokenize into words
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords if enabled
        if self.remove_stopwords:
            tokens = [t for t in tokens if t not in self.stop_words and len(t) > 2]
        
        # Lemmatize if enabled
        if self.lemmatize:
            tokens = [self.lemmatizer.lemmatize(t) for t in tokens]
        
        # Rejoin tokens
        cleaned_text = ' '.join(tokens)
        
        return cleaned_text
    
    def clean_batch(self, texts):
        """
        Clean multiple texts at once
        
        Args:
            texts (list): List of text strings
            
        Returns:
            list: List of cleaned texts
        """
        return [self.clean_text(text) for text in texts]
    
    def get_statistics(self, original_text, cleaned_text):
        """
        Get cleaning statistics
        
        Args:
            original_text (str): Original text
            cleaned_text (str): Cleaned text
            
        Returns:
            dict: Statistics about the cleaning process
        """
        return {
            "original_length": len(original_text),
            "cleaned_length": len(cleaned_text),
            "characters_removed": len(original_text) - len(cleaned_text),
            "reduction_percentage": round(
                (1 - len(cleaned_text) / len(original_text)) * 100, 2
            ) if len(original_text) > 0 else 0,
            "original_word_count": len(original_text.split()),
            "cleaned_word_count": len(cleaned_text.split()),
            "words_removed": len(original_text.split()) - len(cleaned_text.split())
        }


# Utility functions for easy use
def clean_text(text, remove_stopwords=False, lemmatize=False):
    """
    Quick function to clean text
    
    Args:
        text (str): Input text
        remove_stopwords (bool): Remove stopwords
        lemmatize (bool): Lemmatize words
        
    Returns:
        str: Cleaned text
    """
    cleaner = TextCleaner(remove_stopwords, lemmatize)
    return cleaner.clean_text(text)


def advanced_clean(text, remove_stopwords=True, lemmatize=True):
    """
    Quick function for advanced cleaning
    
    Args:
        text (str): Input text
        remove_stopwords (bool): Remove stopwords  
        lemmatize (bool): Lemmatize words
        
    Returns:
        str: Cleaned text
    """
    cleaner = TextCleaner(remove_stopwords, lemmatize)
    return cleaner.advanced_clean(text)