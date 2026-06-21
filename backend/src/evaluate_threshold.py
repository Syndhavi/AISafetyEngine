import torch
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from transformers import DistilBertModel, DistilBertTokenizerFast
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler

# SETTINGS
MODEL_NAME = "distilbert-base-uncased"
MODEL_PATH = "models/hybrid_model.pth"
DEVICE = torch.device("cpu")
MAX_LENGTH = 128
BATCH_SIZE = 8

feature_cols = [
    "profanity_score",
    "sentiment_score",
    "capital_ratio",
    "message_length",
    "repetition_score"
]

# Load dataset
df = pd.read_csv("data/final_featured_dataset.csv")

scaler = StandardScaler()
df[feature_cols] = scaler.fit_transform(df[feature_cols])

_, val_df = train_test_split(
    df, test_size=0.1, stratify=df["label"], random_state=42
)

tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

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
        
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "features": torch.tensor(self.features[idx], dtype=torch.float),
            "label": torch.tensor(self.labels[idx], dtype=torch.float)
        }

val_dataset = HybridDataset(val_df)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

# Load model
class HybridModel(torch.nn.Module):
    def __init__(self):
        super(HybridModel, self).__init__()
        self.bert = DistilBertModel.from_pretrained(MODEL_NAME)
        self.dropout = torch.nn.Dropout(0.3)
        self.classifier = torch.nn.Linear(768 + len(feature_cols), 1)

    def forward(self, input_ids, attention_mask, features):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        combined = torch.cat((cls_embedding, features), dim=1)
        combined = self.dropout(combined)
        return self.classifier(combined)

model = HybridModel().to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()

preds = []
true_labels = []

with torch.no_grad():
    for batch in val_loader:
        outputs = model(
            batch["input_ids"].to(DEVICE),
            batch["attention_mask"].to(DEVICE),
            batch["features"].to(DEVICE)
        )
        probs = torch.sigmoid(outputs)
        preds.extend(probs.cpu().numpy())
        true_labels.extend(batch["label"].numpy())

preds = np.array(preds)

# Try different thresholds
for threshold in [0.5, 0.4, 0.35, 0.3]:
    binary_preds = (preds > threshold).astype(int)
    
    accuracy = accuracy_score(true_labels, binary_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        true_labels, binary_preds, average="binary"
    )

    print(f"\nThreshold: {threshold}")
    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1:", f1)
