import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
config = AutoConfig.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

def softmax(scores):
    exp_scores = np.exp(scores - np.max(scores))
    return exp_scores / exp_scores.sum(axis=0)

def preprocess_text(text):
    new_text = []
    for t in text.split():
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def classify_sentiment(text):

    text = preprocess_text(text)
    
    inputs = tokenizer(text, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model(**inputs)
    scores = outputs.logits[0].numpy()
    scores = softmax(scores)
    
    predicted_label = np.argmax(scores)
    
    if predicted_label == 0:
        return "Negativo"
    elif predicted_label == 1:
        return "Neutro"
    else:
        return "Positivo"
