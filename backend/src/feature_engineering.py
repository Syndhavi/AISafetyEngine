import pandas as pd
import numpy as np
import re
from tqdm import tqdm
from textblob import TextBlob

# -----------------------------
# LOAD DATASET
# -----------------------------
print("Loading dataset...")
df = pd.read_csv("data/final_balanced_dataset.csv")

print("Dataset shape:", df.shape)

# -----------------------------
# PROFANITY LIST
# -----------------------------
profanity_words = [
    "fuck", "shit", "bitch", "asshole", "bastard",
    "dumb", "idiot", "faggot", "nigger", "slut",
    "fucking", "cunt", "rape", "idiots", "stupid",
    "dick", "suck", "sucks", "shut", "bullies",
    "bully", "hate", "ass", "sex", "racist",
    "fucker", "negro", "motherfucker", "asswipe", "sexist", "sexism"
]

def profanity_score(text):
    words = text.split()
    if len(words) == 0:
        return 0
    count = sum(word in profanity_words for word in words)
    return count / len(words)

# -----------------------------
# SENTIMENT
# -----------------------------
def sentiment_score(text):
    return TextBlob(text).sentiment.polarity

# -----------------------------
# CAPITAL RATIO
# -----------------------------
def capital_ratio(text):
    if len(text) == 0:
        return 0
    capitals = sum(1 for c in text if c.isupper())
    letters = sum(1 for c in text if c.isalpha())
    if letters == 0:
        return 0
    return capitals / letters

# -----------------------------
# MESSAGE LENGTH
# -----------------------------
def message_length(text):
    return len(text.split())

# -----------------------------
# REPETITION SCORE
# -----------------------------
def repetition_score(text):
    repeated = len(re.findall(r"(.)\1{2,}", text))
    if len(text) == 0:
        return 0
    return repeated / len(text)

# -----------------------------
# APPLY FEATURES
# -----------------------------
tqdm.pandas()

print("Extracting features...")

df["profanity_score"] = df["text"].progress_apply(profanity_score)
df["sentiment_score"] = df["text"].progress_apply(sentiment_score)
df["capital_ratio"] = df["text"].progress_apply(capital_ratio)
df["message_length"] = df["text"].progress_apply(message_length)
df["repetition_score"] = df["text"].progress_apply(repetition_score)

# -----------------------------
# SAVE
# -----------------------------
df.to_csv("data/final_featured_dataset.csv", index=False)

print("Feature extraction completed.")
print(df.head())