import pandas as pd
from sklearn.utils import resample

# -----------------------------
# LOAD DATASETS
# -----------------------------
print("Loading main dataset...")
main_df = pd.read_csv("data/final_featured_dataset.csv")

print("Loading grooming featured dataset...")
groom_df = pd.read_csv("data/grooming_featured_dataset.csv")

print("\nOriginal Sizes:")
print("Main dataset:", main_df.shape)
print("Grooming dataset:", groom_df.shape)

print("\nClass Distribution Before Merge:")
print("Main:")
print(main_df["label"].value_counts())
print("\nGrooming:")
print(groom_df["label"].value_counts())

# -----------------------------
# UPSAMPLE GROOMING DATASET
# -----------------------------
print("\nUpsampling grooming dataset to 4000 samples...")

groom_df_upsampled = resample(
    groom_df,
    replace=True,
    n_samples=4000,   # recommended size
    random_state=42
)

print("Upsampled Grooming Size:", groom_df_upsampled.shape)
print("Upsampled Grooming Distribution:")
print(groom_df_upsampled["label"].value_counts())

# -----------------------------
# MERGE DATASETS
# -----------------------------
print("\nMerging datasets...")

final_df = pd.concat([main_df, groom_df_upsampled], ignore_index=True)

print("\nFinal Dataset Size:", final_df.shape)
print("Final Class Distribution:")
print(final_df["label"].value_counts())

# -----------------------------
# SAVE FINAL DATASET
# -----------------------------
final_df.to_csv("data/final_featured_dataset_v2.csv", index=False)

print("\nMerged dataset saved as:")
print("data/final_featured_dataset_v2.csv")