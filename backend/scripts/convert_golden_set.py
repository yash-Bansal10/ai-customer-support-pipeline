import csv
import json
from pathlib import Path

def convert_csv_to_json():
    csv_path = Path("data/golden_set_labeled.csv")
    json_path = Path("data/golden_set.json")
    
    if not csv_path.exists():
        print(f"Error: Cannot find {csv_path}. Please generate and label it first.")
        return
        
    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only keep the ones you actually labeled, skip empty ones
            if row.get("expected_intent") and row.get("expected_decision"):
                item = {
                    "example_id": row["example_id"],
                    "customer_message": row["customer_message"],
                    "expected_intent": row["expected_intent"].strip(),
                    "expected_decision": row["expected_decision"].strip()
                }
                
                # Add human scores if provided
                if row.get("human_correctness_score"):
                    item["human_correctness_score"] = int(row["human_correctness_score"].strip())
                if row.get("human_safety_score"):
                    item["human_safety_score"] = int(row["human_safety_score"].strip())
                    
                data.append(item)
                
    if not data:
        print("Warning: No labeled rows found in CSV. Did you fill out the expected_intent column?")
        return
        
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully converted {len(data)} labeled items to {json_path}")
    print("You can now run 'python scripts/evaluate.py'")

if __name__ == "__main__":
    convert_csv_to_json()
