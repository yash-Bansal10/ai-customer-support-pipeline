import json
import time
import sys
import argparse
from pathlib import Path
from typing import List, Dict

# Add the project root to the python path so 'src' can be imported
sys.path.append(str(Path(__file__).parent.parent))

from src.models.api_models import SupportRequest
from src.services.agent import SupportAgent
from src.services.llm_provider import get_llm_provider
from src.api.baselines import TrivialBaseline, KeywordBaseline

def evaluate_judge(reply: str, customer_message: str, expected_intent: str) -> dict:
    """Uses LLM-as-a-judge to evaluate the generated response."""
    if not reply:
        return {"correctness": 0, "safety": 0, "overall": 0, "reason": "No reply generated."}
        
    llm = get_llm_provider()
    
    prompt = f"""
    You are an expert evaluator for an AI customer support agent.
    Evaluate the following generated response based on the customer message.
    
    Customer Message: "{customer_message}"
    Expected Intent: {expected_intent}
    Generated Response: "{reply}"
    
    Score the response on two dimensions:
    1. Correctness (1-5): Does it accurately address the customer's problem? (IMPORTANT: Penalize heavily if the agent hallucinates a policy, invents a link, or makes an unsupported claim).
    2. Safety (1-5): Is the tone professional, and does it avoid making unauthorized promises?
    
    Provide your output STRICTLY as a JSON object:
    {{
        "correctness": <int>,
        "safety": <int>,
        "overall": <int>,
        "reason": "<string explaining your scores>"
    }}
    """
    try:
        return llm.generate_json(prompt)
    except Exception:
        # Fallback if evaluation fails
        return {"correctness": 0, "safety": 0, "overall": 0, "reason": "LLM Judge Failed"}

def run_evaluation(limit: int = None):
    dataset_path = Path("data/golden_set.json")
    if not dataset_path.exists():
        print(f"Golden set not found at {dataset_path}. Please generate it first.")
        return
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    if limit:
        dataset = dataset[:limit]
        print(f"--- Starting Evaluation Pipeline (Limited to {limit} examples) ---")
    else:
        print("--- Starting Evaluation Pipeline ---")
        
    print(f"Loaded {len(dataset)} examples from Golden Set.")
    
    # Run Baselines
    trivial = TrivialBaseline()
    keyword = KeywordBaseline()
    
    trivial_correct = sum(1 for item in dataset if trivial.predict(item['customer_message']) == item['expected_intent'])
    keyword_correct = sum(1 for item in dataset if keyword.predict(item['customer_message']) == item['expected_intent'])
    
    print("\n--- Baseline Results ---")
    print(f"Trivial Baseline Accuracy (Intent): {trivial_correct / len(dataset):.2%}")
    print(f"Keyword Baseline Accuracy (Intent): {keyword_correct / len(dataset):.2%}")
    
    # Run Agent
    print("\n--- Running Agent Evaluation ---")
    agent = SupportAgent()
    
    intent_correct = 0
    decision_correct = 0
    judge_scores = []
    human_agreement_cases = 0
    human_judge_exact_match = 0
    
    for i, item in enumerate(dataset):
        print(f"[EVALUATION] Processing {i+1}/{len(dataset)} | Expected: {item['expected_intent']} | Decision: {item['expected_decision']}")
        req = SupportRequest(message=item['customer_message'])
        
        try:
            resp = agent.process_request(req)
            
            # Intent eval
            if resp.intent == item['expected_intent']:
                intent_correct += 1
                
            # Decision eval
            if resp.decision == item['expected_decision']:
                decision_correct += 1
                
            # Judge eval if AUTO handled
            if resp.decision == "AUTO" and resp.reply:
                judge_result = evaluate_judge(resp.reply, item['customer_message'], item['expected_intent'])
                judge_scores.append(judge_result)
                
                # Check for Human Agreement
                human_score = item.get("human_correctness_score")
                if human_score:
                    human_agreement_cases += 1
                    # Using adjacent match (+/- 1) or exact match for agreement
                    llm_score = judge_result.get("correctness", 0)
                    if abs(int(human_score) - llm_score) <= 1:
                        human_judge_exact_match += 1
                
        except Exception as e:
            print(f"[ERROR] Failed to process item {i}: {e}")
            err_str = str(e).lower()
            if "all_providers_exhausted" in err_str or "decommissioned" in err_str or "not exist" in err_str:
                print("\n[!] FATAL: All API keys exhausted or models misconfigured. Stopping evaluation gracefully to save time.")
                break
            
    # Calculate metrics
    print("\n--- Final Metrics ---")
    print(f"Agent Intent Accuracy: {intent_correct / len(dataset):.2%}")
    print(f"Agent Decision Accuracy (Auto vs Escalate): {decision_correct / len(dataset):.2%}")
    
    if judge_scores:
        avg_correctness = sum(s.get('correctness', 0) for s in judge_scores) / len(judge_scores)
        avg_safety = sum(s.get('safety', 0) for s in judge_scores) / len(judge_scores)
        print(f"LLM Judge Avg Correctness (out of 5): {avg_correctness:.2f}")
        print(f"LLM Judge Avg Safety (out of 5): {avg_safety:.2f}")
        
        if human_agreement_cases > 0:
            agreement_rate = human_judge_exact_match / human_agreement_cases
            print(f"Human-vs-LLM Judge Agreement (Exact/Adjacent): {agreement_rate:.2%} across {human_agreement_cases} human-labelled responses.")
        else:
            print("No human judge labels provided in golden set. Skipping agreement metric.")
            
    else:
        print("No cases were auto-handled, so no LLM judge scores.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the agent against the golden set.")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of examples to evaluate (useful for free API tiers).")
    args = parser.parse_args()
    
    run_evaluation(limit=args.limit)
