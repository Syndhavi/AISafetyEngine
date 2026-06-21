import pandas as pd
import numpy as np
import re
from tqdm import tqdm


# -----------------------------
# TEXT CLEANING FUNCTION
# -----------------------------
def clean_text(text):
    if pd.isna(text):
        return ""
    
    text = str(text)
    
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    
    # Remove mentions
    text = re.sub(r"@\w+", "", text)
    
    # Remove special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    
    # Lowercase
    text = text.lower()
    
    return text.strip()


print("Loading datasets...")

df1 = pd.read_csv("data/cyberbullying.csv", encoding="latin1")
df2 = pd.read_csv("data/twitter_parsed.csv", encoding="latin1")
df3 = pd.read_csv("data/classified_tweets.csv", encoding="latin1")
df4 = pd.read_csv("data/cyberbullying_tweets.csv", encoding="latin1")
df5 = pd.read_csv("data/kaggle_parsed.csv", encoding="latin1")


# -----------------------------
# DATASET 1 – Cyberbullying
# Use SubLabel instead of CBLabel
# -----------------------------
df1 = df1[["Message", "SubLabel"]]
df1.columns = ["text", "label"]

# If SubLabel > 0 → harmful
df1["label"] = df1["label"].apply(lambda x: 1 if x > 0 else 0)


# -----------------------------
# DATASET 2 – Twitter Parsed
# -----------------------------
df2 = df2[["Text", "oh_label"]]
df2.columns = ["text", "label"]

df2["label"] = df2["label"].apply(lambda x: 1 if x == 1 else 0)


# -----------------------------
# DATASET 3 – Classified Tweets
# Multi-label → binary
# -----------------------------
df3["label"] = df3[["suspicious", "cyberbullying", "hate", "suicidal"]].max(axis=1)
df3 = df3[["text", "label"]]


# -----------------------------
# DATASET 4 – Cyberbullying Tweets
# -----------------------------
df4 = df4[["tweet_text", "cyberbullying_type"]]
df4.columns = ["text", "label"]

df4["label"] = df4["label"].apply(
    lambda x: 0 if x == "not_cyberbullying" else 1
)


# -----------------------------
# DATASET 5 – Kaggle Parsed
# -----------------------------
df5 = df5[["Text", "oh_label"]]
df5.columns = ["text", "label"]

df5["label"] = df5["label"].apply(lambda x: 1 if x == 1 else 0)


# -----------------------------
# MERGE ALL DATASETS
# -----------------------------
print("Merging datasets...")

df_final = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)

print("Before cleaning:", df_final.shape)


# -----------------------------
# CLEAN TEXT
# -----------------------------
print("Cleaning text...")

tqdm.pandas()
df_final["text"] = df_final["text"].progress_apply(clean_text)

# Remove empty rows
df_final = df_final[df_final["text"].str.strip() != ""]

# Remove duplicates
df_final = df_final.drop_duplicates(subset=["text"])

# Force binary labels
df_final["label"] = df_final["label"].apply(lambda x: 1 if x > 0 else 0)

print("After cleaning:", df_final.shape)


# -----------------------------
# CLASS DISTRIBUTION
# -----------------------------
print("Class Distribution:")
print(df_final["label"].value_counts())


# -----------------------------
# SAVE FINAL DATASET
# -----------------------------
df_final.to_csv("data/final_threat_dataset.csv", index=False)

print("Final dataset saved successfully!")