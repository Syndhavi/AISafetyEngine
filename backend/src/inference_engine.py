import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from transformers import DistilBertModel, DistilBertTokenizerFast
from sklearn.preprocessing import StandardScaler
import joblib


SEXUAL_KEYWORDS = [
    "nude", "naked", "sex", "porn",
    "send pic", "send pics","sexy","hot",
    "private parts","private part", "explicit",
    "send photo","send photos","send picture","send pictures","send me your pic",
    "send your pic","send your photos","send me your photos","send your picture","send me your picture","send your pictures"]

# -----------------------------
# SETTINGS
# -----------------------------
MODEL_NAME = "distilbert-base-uncased"
import os

# Get current file directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go one level up (project root)
ROOT_DIR = os.path.dirname(BASE_DIR)

MODEL_PATH = os.path.join(ROOT_DIR, "models", "hybrid_model.pth")
SCALER_PATH = os.path.join(ROOT_DIR, "models", "feature_scaler.pkl")

scaler = joblib.load(SCALER_PATH)

DEVICE = torch.device("cpu")

feature_cols = [
    "profanity_score",
    "sentiment_score",
    "capital_ratio",
    "message_length",
    "repetition_score"
]

# -----------------------------
# LOAD TOKENIZER
# -----------------------------
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

# -----------------------------
# HYBRID MODEL (SAME AS TRAINING)
# -----------------------------
class HybridModel(nn.Module):
    def __init__(self):
        super(HybridModel, self).__init__()
        self.bert = DistilBertModel.from_pretrained(MODEL_NAME)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(768 + len(feature_cols), 1)

    def forward(self, input_ids, attention_mask, features):
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        combined = torch.cat((cls_embedding, features), dim=1)
        combined = self.dropout(combined)
        logits = self.classifier(combined)
        return logits


# -----------------------------
# LOAD MODEL WEIGHTS
# -----------------------------
model = HybridModel().to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()


# -----------------------------
# FEATURE EXTRACTOR (same logic)
# -----------------------------
def extract_features(text):
    words = text.split()

    profanity_score = sum(1 for w in words if w in ["kill", "hate", "die"]) / max(len(words), 1)
    sentiment_score = 0  # keep simple for now
    capital_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    message_length = len(words)
    repetition_score = len(words) - len(set(words))

    return np.array([
        profanity_score,
        sentiment_score,
        capital_ratio,
        message_length,
        repetition_score
    ])


# -----------------------------
# MAIN INFERENCE FUNCTION
# -----------------------------
def process_message(text):
    encoding = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=128,
        return_tensors="pt"
    )

    features = extract_features(text)
   

    features_df = pd.DataFrame([features], columns=feature_cols)
    features = scaler.transform(features_df)[0]

    features = torch.tensor(features, dtype=torch.float).unsqueeze(0)


    with torch.no_grad():
        outputs = model(
            encoding["input_ids"],
            encoding["attention_mask"],
            features
        )
        prob = torch.sigmoid(outputs).item()
        text_lower = text.lower()

        for keyword in SEXUAL_KEYWORDS:
          if keyword in text_lower:
             
            prob = max(prob, 0.7)
            break


    return prob