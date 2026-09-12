import json
import random
import csv
from pathlib import Path

def generate_blank_golden_set():
    """
    Randomly samples 150 conversations from the TEST set and creates a CSV
    so the user can manually label them for the Golden Set assignment requirement.
    This guarantees no overlap with the FAISS retrieval index (train set).
    """
    conversations_path = Path("data/twitter_customer_support/test_conversations.json")
    output_csv = Path("data/golden_set_to_label.csv")
    
    if not conversations_path.exists():
        print(f"Error: {conversations_path} not found. Run build_conversations.py first.")
        return
        
    with open(conversations_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if len(data) < 150:
        print("Not enough data to sample 150 items.")
        return
        
    # Sample 150 random examples
    sample = random.sample(data, 150)
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["example_id", "customer_message", "expected_intent", "expected_decision", "human_correctness_score", "human_safety_score"])
        
        for i, item in enumerate(sample):
            writer.writerow([
                f"gs_{str(i+1).zfill(3)}",
                item.get("customer_message", "").replace("\n", " "),
                "", # Leave blank for human to fill
                "", # Leave blank for human to fill
                "", # Leave blank for human to score (1-5)
                ""  # Leave blank for human to score (1-5)
            ])
            
    print(f"Successfully generated {output_csv} with 150 examples.")
    print("Please open this CSV, fill in the expected intents and decisions, and provide 1-5 scores for about 20 of them.")

if __name__ == "__main__":
    generate_blank_golden_set()
