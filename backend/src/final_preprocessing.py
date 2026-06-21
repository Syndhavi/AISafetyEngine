import pandas as pd
import numpy as np
import re
from tqdm import tqdm
from sklearn.utils import shuffle

# ==============================
# Text Cleaning Function
# ==============================
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ==============================
# Load Original Processed Dataset
# ==============================
print("Loading main dataset...")
main_df = pd.read_csv("data/final_threat_dataset.csv")  # <-- your current merged dataset

print("Main dataset shape:", main_df.shape)

# ==============================
# Load Toxicity Dataset
# ==============================
print("Loading toxicity dataset...")
tox_df = pd.read_csv("data/toxicity_parsed.csv")

# Rename columns properly
tox_df = tox_df.rename(columns={"Text": "text", "oh_label": "label"})

tox_df = tox_df[["text", "label"]]

print("Toxicity dataset shape:", tox_df.shape)

# ==============================
# Separate Classes From Main Dataset
# ==============================
harmful_main = main_df[main_df["label"] == 1]
safe_main = main_df[main_df["label"] == 0]

print("Main Harmful:", len(harmful_main))
print("Main Safe:", len(safe_main))

# ==============================
# Separate Classes From Toxic Dataset
# ==============================
safe_tox = tox_df[tox_df["label"] == 0]
harmful_tox = tox_df[tox_df["label"] == 1]

print("Toxic Safe:", len(safe_tox))
print("Toxic Harmful:", len(harmful_tox))

# ==============================
# Target Size Settings
# ==============================
TARGET_TOTAL = 80000
TARGET_PER_CLASS = TARGET_TOTAL // 2  # 40000 each

# ==============================
# Prepare Harmful Class
# ==============================
harmful_combined = pd.concat([harmful_main, harmful_tox], ignore_index=True)

if len(harmful_combined) > TARGET_PER_CLASS:
    harmful_combined = harmful_combined.sample(TARGET_PER_CLASS, random_state=42)

# ==============================
# Prepare Safe Class
# ==============================
safe_combined = pd.concat([safe_main, safe_tox], ignore_index=True)

if len(safe_combined) > TARGET_PER_CLASS:
    safe_combined = safe_combined.sample(TARGET_PER_CLASS, random_state=42)

# ==============================
# Merge Balanced Dataset
# ==============================
final_df = pd.concat([harmful_combined, safe_combined], ignore_index=True)

print("Before cleaning:", final_df.shape)

# ==============================
# Clean Text
# ==============================
print("Cleaning text...")
tqdm.pandas()
final_df["text"] = final_df["text"].progress_apply(clean_text)

# Remove empty rows
final_df = final_df[final_df["text"].str.strip() != ""]

print("After cleaning:", final_df.shape)

# ==============================
# Shuffle Dataset
# ==============================
final_df = shuffle(final_df, random_state=42)

# ==============================
# Show Class Distribution
# ==============================
print("Class Distribution:")
print(final_df["label"].value_counts())

# ==============================
# Save Final Dataset
# ==============================
final_df.to_csv("data/final_balanced_dataset.csv", index=False)

print("Final balanced dataset saved successfully!")