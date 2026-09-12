import json
import random
from pathlib import Path
from typing import List, Dict, Tuple

class BaselineClassifier:
    """Interface for baseline classifiers."""
    def predict(self, text: str) -> str:
        raise NotImplementedError

class TrivialBaseline(BaselineClassifier):
    """
    A trivial baseline that always predicts the majority class.
    For AppleSupport, 'DEVICE_ISSUE' is often the majority.
    """
    def __init__(self, majority_class: str = "DEVICE_ISSUE"):
        self.majority_class = majority_class
        
    def predict(self, text: str) -> str:
        return self.majority_class

class KeywordBaseline(BaselineClassifier):
    """
    A simple baseline that uses keyword matching to predict intent.
    If no keywords match, it falls back to a default class.
    """
    def __init__(self):
        self.keywords = {
            "DEVICE_ISSUE": ["screen", "battery", "freeze", "crash", "broken", "update", "ios"],
            "ACCOUNT_ISSUE": ["password", "id", "icloud", "locked", "code", "verification"],
            "BILLING_ISSUE": ["charge", "refund", "subscription", "pay", "money", "bought"],
            "HOW_TO_QUERY": ["how to", "where is", "turn on", "turn off", "settings"]
        }
        self.default_class = "OTHER"
        
    def predict(self, text: str) -> str:
        text_lower = text.lower()
        
        # Simple scoring
        scores = {intent: 0 for intent in self.keywords}
        for intent, words in self.keywords.items():
            for word in words:
                if word in text_lower:
                    scores[intent] += 1
                    
        # Find max score
        max_intent = max(scores, key=scores.get)
        
        if scores[max_intent] > 0:
            return max_intent
        return self.default_class

def evaluate_baseline(baseline: BaselineClassifier, golden_set_path: Path) -> float:
    """Evaluates a baseline against the golden set."""
    with open(golden_set_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    correct = 0
    total = len(data)
    
    for item in data:
        pred = baseline.predict(item['customer_message'])
        if pred == item['expected_intent']:
            correct += 1
            
    accuracy = correct / total if total > 0 else 0
    return accuracy

if __name__ == "__main__":
    gs_path = Path("data/golden_set.json")
    
    trivial = TrivialBaseline()
    trivial_acc = evaluate_baseline(trivial, gs_path)
    print(f"Trivial Baseline (Majority Class) Accuracy: {trivial_acc:.2%}")
    
    keyword = KeywordBaseline()
    keyword_acc = evaluate_baseline(keyword, gs_path)
    print(f"Keyword Baseline Accuracy: {keyword_acc:.2%}")
