# Failure Analysis

This document identifies real expected failure modes based on the evaluation pipeline.

### 1. The "Ambiguous Vague Complaint"
- **Category**: Intent Classification Failure
- **Real Example**: "This is ridiculous, I've been waiting for hours."
- **Expected Behavior**: Classify as `OTHER` and `ESCALATE`.
- **Actual Behavior**: Sometimes the LLM tries to guess what they are waiting for and might classify as `DEVICE_ISSUE`.
- **Why it failed**: Lack of context. The model attempts to be helpful and pattern matches "waiting" to device repairs.
- **Improvement**: Add a stricter system prompt for the classification LLM to output `OTHER` whenever specific product nouns are missing.

### 2. The "Hardware disguised as Software"
- **Category**: Boundary Case Misclassification
- **Real Example**: "My phone gets super hot after I installed iOS 15."
- **Expected Behavior**: `DEVICE_ISSUE`
- **Actual Behavior**: Sometimes classified as `HOW_TO_QUERY` if it contains words like "settings".
- **Improvement**: Expand the Golden Set with more examples of software-induced hardware symptoms.

### 3. The "Overconfident Hallucination"
- **Category**: Generation Grounding Failure
- **Real Example**: Customer asks about a refund for a 3-year-old app.
- **Expected Behavior**: Retrieve refund policy, realize time limit exceeded, and escalate or reject.
- **Actual Behavior**: The LLM might generate "We can refund that for you right away!" because historical cases for 1-day-old app refunds were retrieved.
- **Why it failed**: The LLM failed to distinguish the temporal constraint (3 years vs 1 day).
- **Improvement**: Enforce strict account verification before ANY billing issues are auto-handled (currently implemented in the Agent Risk Layer by hard-escalating all Account/Billing issues).

### 4. Poor Retrieval due to Short Queries
- **Category**: Retrieval Failure
- **Real Example**: "Broken."
- **Expected Behavior**: Escalate due to ambiguity.
- **Actual Behavior**: FAISS retrieves random historical cases that contain the word "broken".
- **Improvement**: Implement a minimum query length check before running retrieval.

### 5. LLM Judge Bias
- **Category**: Evaluation Failure
- **Real Example**: A generated response is perfectly accurate but very blunt.
- **Expected Behavior**: High correctness, low brand consistency.
- **Actual Behavior**: The LLM Judge gives it 5/5 for everything because the facts match.
- **Improvement**: Provide the LLM Judge with a specific rubric and negative examples of "bad tone" to calibrate it.
