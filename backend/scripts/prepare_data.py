import os
import zipfile
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from kaggle.api.kaggle_api_extended import KaggleApi

DATA_DIR = Path("data")
RAW_DATA_PATH = DATA_DIR / "twitter_customer_support" / "twitter_customer_support.csv"
DATASET_NAME = "thoughtvector/customer-support-on-twitter"

def authenticate_kaggle() -> KaggleApi:
    """Authenticates with the Kaggle API."""
    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as e:
        print("Error authenticating with Kaggle.")
        print("Please ensure KAGGLE_USERNAME and KAGGLE_KEY are set in your environment.")
        print("Example: set KAGGLE_USERNAME=... and set KAGGLE_KEY=...")
        raise e
    return api

def download_dataset():
    """Downloads and unzips the Twitter Customer Support dataset."""
    if RAW_DATA_PATH.exists():
        print(f"Dataset already exists at {RAW_DATA_PATH}")
        return

    print(f"Downloading dataset: {DATASET_NAME}...")
    api = authenticate_kaggle()
    api.dataset_download_files(DATASET_NAME, path=DATA_DIR, unzip=True)
    print("Download complete.")

def analyze_brands():
    """Analyzes the dataset to find the best brand for evaluation."""
    print("Loading data for analysis (this might take a minute)...")
    df = pd.read_csv(RAW_DATA_PATH)
    
    print(f"Total tweets: {len(df)}")
    
    # Identify brands (author_id is a string, often starts with a letter for brands)
    # The dataset has an 'inbound' boolean flag. Inbound=False means the brand replied.
    brands_df = df[df['inbound'] == False]
    top_brands = brands_df['author_id'].value_counts().head(10)
    
    print("\nTop 10 Responding Brands:")
    print(top_brands)
    
    print("\nDecision: We will select a brand that has enough volume but also diverse intents.")
    print("Usually, 'AppleSupport', 'AmazonHelp', or 'SpotifyCares' are good candidates.")
    # In a real run, you'd plot these and make a structured decision.

if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    download_dataset()
    if RAW_DATA_PATH.exists():
        analyze_brands()
