import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

feature_cols = [
    "profanity_score",
    "sentiment_score",
    "capital_ratio",
    "message_length",
    "repetition_score"
]

df = pd.read_csv("data/final_featured_dataset.csv")

scaler = StandardScaler()
scaler.fit(df[feature_cols])

joblib.dump(scaler, "models/feature_scaler.pkl")

print("Scaler saved successfully.")
