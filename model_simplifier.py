from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class TextSimplifier:
    """
    Text simplification using FLAN-T5 model
    Transforms complex legal text into simpler language
    """
    
    def __init__(self, model_name="google/flan-t5-base"):
        """
        Initialize the FLAN-T5 model
        
        Args:
            model_name (str): Hugging Face model identifier
        """
        print(f"Loading model: {model_name}...")
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        # Use GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"Model loaded successfully on {self.device}!")
    
    def simplify_text(self, complex_text, max_length=512, temperature=0.7):
        """
        Simplify complex legal text
        
        Args:
            complex_text (str): Input complex text
            max_length (int): Maximum length of output
            temperature (float): Sampling temperature (higher = more creative)
            
        Returns:
            str: Simplified text
        """
        # Create prompt for simplification
        prompt = f"Simplify this legal text for a general audience: {complex_text}"
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        ).to(self.device)
        
        # Generate simplified text
        outputs = self.model.generate(
            inputs.input_ids,
            max_length=max_length,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            num_return_sequences=1
        )
        
        # Decode output
        simplified = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return simplified
    
    def simplify_batch(self, texts, max_length=512):
        """
        Simplify multiple texts at once
        
        Args:
            texts (list): List of complex texts
            max_length (int): Maximum length per output
            
        Returns:
            list: List of simplified texts
        """
        simplified_texts = []
        for text in texts:
            simplified = self.simplify_text(text, max_length)
            simplified_texts.append(simplified)
        return simplified_texts
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        }


# Utility function for easy use
def simplify(text, model_name="google/flan-t5-base"):
    """
    Quick function to simplify text
    
    Args:
        text (str): Complex text
        model_name (str): Model to use
        
    Returns:
        str: Simplified text
    """
    simplifier = TextSimplifier(model_name)
    return simplifier.simplify_text(text)