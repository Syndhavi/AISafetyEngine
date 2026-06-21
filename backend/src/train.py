import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertModel, DistilBertTokenizerFast
from tqdm import tqdm

# -----------------------------
# SETTINGS
# -----------------------------
MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 128
BATCH_SIZE = 8
EPOCHS = 1
LEARNING_RATE = 2e-5
DEVICE = torch.device("cpu")  # Force CPU

# -----------------------------
# LOAD DATA
# -----------------------------
print("Loading dataset...")
df = pd.read_csv("data/final_featured_dataset.csv")

feature_cols = [
    "profanity_score",
    "sentiment_score",
    "capital_ratio",
    "message_length",
    "repetition_score"
]

# Normalize numerical features
scaler = StandardScaler()
df[feature_cols] = scaler.fit_transform(df[feature_cols])

train_df, val_df = train_test_split(
    df, test_size=0.1, stratify=df["label"], random_state=42
)

print("Train size:", len(train_df))
print("Validation size:", len(val_df))

# -----------------------------
# TOKENIZER
# -----------------------------
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

# -----------------------------
# DATASET CLASS
# -----------------------------
class HybridDataset(Dataset):
    def __init__(self, dataframe):
        self.texts = dataframe["text"].tolist()
        self.labels = dataframe["label"].tolist()
        self.features = dataframe[feature_cols].values
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        encoding = tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
            return_tensors="pt"
        )
        
        item = {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "features": torch.tensor(self.features[idx], dtype=torch.float),
            "label": torch.tensor(self.labels[idx], dtype=torch.float)
        }
        return item

train_dataset = HybridDataset(train_df)
val_dataset = HybridDataset(val_df)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

# -----------------------------
# HYBRID MODEL
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

model = HybridModel().to(DEVICE)

criterion = nn.BCEWithLogitsLoss()
optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE)

# -----------------------------
# TRAINING LOOP
# -----------------------------
print("Starting training...")

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    
    for batch in tqdm(train_loader):
        optimizer.zero_grad()
        
        input_ids = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        features = batch["features"].to(DEVICE)
        labels = batch["label"].unsqueeze(1).to(DEVICE)
        
        outputs = model(input_ids, attention_mask, features)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    print(f"Epoch {epoch+1} Loss: {total_loss/len(train_loader)}")

# -----------------------------
# VALIDATION
# -----------------------------
model.eval()
preds = []
true_labels = []

with torch.no_grad():
    for batch in val_loader:
        input_ids = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        features = batch["features"].to(DEVICE)
        labels = batch["label"].to(DEVICE)
        
        outputs = model(input_ids, attention_mask, features)
        probs = torch.sigmoid(outputs)
        preds.extend(probs.cpu().numpy())
        true_labels.extend(labels.cpu().numpy())

preds = np.array(preds)
THRESHOLD = 0.35
binary_preds = (preds > THRESHOLD).astype(int)

accuracy = accuracy_score(true_labels, binary_preds)
precision, recall, f1, _ = precision_recall_fscore_support(
    true_labels, binary_preds, average="binary"
)

print("\nValidation Results")
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)

# -----------------------------
# SAVE MODEL
# -----------------------------
torch.save(model.state_dict(), "models/hybrid_model.pth")
print("Model saved successfully.")