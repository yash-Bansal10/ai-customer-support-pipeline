import pandas as pd
import json
from pathlib import Path
from typing import List, Dict
import random
import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path("data/twitter_customer_support/")
RAW_DATA_PATH = DATA_DIR / "twitter_customer_support.csv"
TRAIN_DATA_PATH = DATA_DIR / "train_conversations.json"
TEST_DATA_PATH = DATA_DIR / "test_conversations.json"

SELECTED_BRAND = os.getenv("SELECTED_BRAND", "AppleSupport")

def build_conversations(df: pd.DataFrame, brand: str) -> List[Dict]:
    """
    Reconstructs conversations for a specific brand from the raw dataset.
    
    A conversation is built by tracing 'in_response_to_tweet_id' and 'response_tweet_id'.
    We look for interactions where a customer asks a question (inbound) and the brand responds.
    """
    print(f"Filtering dataset for brand: {brand}")
    
    # Get all tweets from the brand
    brand_tweets = df[df['author_id'] == brand]
    
    # We want to find threads that start with a user, are replied to by the brand, etc.
    # To simplify and ensure high quality for the assessment, we will find "resolved" cases.
    # A simple proxy for a useful conversation:
    # 1. Customer tweet (inbound)
    # 2. Brand reply
    
    # Create dictionaries for fast lookup
    tweets_dict = df.set_index('tweet_id').to_dict(orient='index')
    
    conversations = []
    processed_ids = set()
    
    print(f"Total {brand} tweets to process: {len(brand_tweets)}")
    
    count = 0
    # Iterate through brand tweets that reply to an inbound tweet
    for tweet_id, row in brand_tweets.iterrows():
        if pd.notna(row['in_response_to_tweet_id']):
            parent_id = row['in_response_to_tweet_id']
            # If the parent hasn't been processed and is in our dataset
            if parent_id not in processed_ids and parent_id in tweets_dict:
                parent_tweet = tweets_dict[parent_id]
                
                # Check if parent is an inbound customer tweet
                if parent_tweet['inbound']:
                    # We found a basic conversation pair (Customer -> Brand)
                    conversation = {
                        "conversation_id": str(parent_id),
                        "brand": brand,
                        "customer_message": parent_tweet['text'],
                        "brand_response": row['text'],
                        "created_at": str(parent_tweet['created_at'])
                    }
                    conversations.append(conversation)
                    processed_ids.add(parent_id)
                    processed_ids.add(tweet_id)
                    
                    count += 1
                    if count >= 10000: # Limit to 10k for manageability in this assessment
                        break
                        
    print(f"Reconstructed {len(conversations)} conversations.")
    return conversations

def run_pipeline():
    print("Loading raw data...")
    if not RAW_DATA_PATH.exists():
        print(f"Error: Raw data not found at {RAW_DATA_PATH}. Please run prepare_data.py first.")
        return
        
    df = pd.read_csv(RAW_DATA_PATH)
    
    conversations = build_conversations(df, SELECTED_BRAND)
    print(f"Reconstructed {len(conversations)} two-turn conversations.")
    
    # We shuffle and split the data (95% Train, 5% Test) to prevent evaluation leakage
    random.shuffle(conversations)
    split_idx = int(len(conversations) * 0.95)
    train_convs = conversations[:split_idx]
    test_convs = conversations[split_idx:]
    
    with open(TRAIN_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(train_convs, f, indent=2)
        
    with open(TEST_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(test_convs, f, indent=2)
        
    print(f"Saved {len(train_convs)} to {TRAIN_DATA_PATH}")
    print(f"Saved {len(test_convs)} to {TEST_DATA_PATH}")
    print("Pipeline complete.")

if __name__ == "__main__":
    run_pipeline()
