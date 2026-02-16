import spacy

nlp = spacy.load("en_core_web_sm")

def segment_sentences(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

