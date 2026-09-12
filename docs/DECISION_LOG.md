# Decision Log

### 1. Brand Selection
- **Decision**: Selected `AppleSupport` for the evaluation dataset.
- **Context**: The Twitter dataset has many brands. I needed one with high volume and diverse intents.
- **Decision**: Filter exclusively for `@AppleSupport` by default.
- **Tradeoff**: I lose testing the system on multi-brand responses, but I gain deep focus on a realistic intent taxonomy. 
- **Bonus Feature**: To prove the architecture is generalizable, I exposed the brand filter as `SELECTED_BRAND` in the `.env` file, meaning the entire pipeline can instantly pivot to a brand like `Delta` without changing a line of code.

### 2. Retrieval Approach
- **Decision**: Used local `FAISS` with `sentence-transformers` instead of a hosted vector database like Pinecone.
- **Context**: The assignment requires the project to be highly reproducible in under 15 minutes.
- **Reason**: FAISS runs in-memory without Docker or network dependencies.
- **Tradeoff**: FAISS does not persist out of the box in the same way a managed DB does, but it is perfect for an assessment environment.

### 3. Provider Abstraction
- **Decision**: Created an `LLMProvider` interface instead of hardcoding `openai` or `langchain`.
- **Context**: Relying on one specific API makes the codebase brittle.
- **Reason**: Allows the reviewer (or me) to easily swap to Gemini, OpenAI, or a local model depending on API key availability.
- **Tradeoff**: Requires writing a bit of wrapper code instead of using raw SDKs.

### 4. Deterministic Escalation
- **Decision**: Handled escalation logic via explicit Python `if` statements (Agent rules) rather than relying on the LLM to decide.
- **Context**: LLMs are often overconfident and might try to answer even when they shouldn't.
- **Reason**: Hardcoding escalation for `ACCOUNT_ISSUE` or low-confidence intents guarantees safety.
### 5. Baseline Selection
- **Decision**: Implemented a Trivial (Majority Class) and a Simple (Keyword Match) baseline.
- **Context**: The assignment required two baselines to prove the AI is actually useful.
- **Reason**: Trivial baseline provides the absolute floor for accuracy. Keyword baseline mimics a standard decision-tree chatbot that many companies currently use.
- **Tradeoff**: Did not implement a heavy ML baseline (like Random Forest with TF-IDF) to keep the project lightweight and fast to run.

### 6. LLM-as-a-Judge Rubric
- **Decision**: Scored responses on Correctness and Safety (1-5 scale).
- **Context**: Needed an automated way to evaluate generated text quality.
- **Reason**: 1-5 scales are standard for LLM eval and easier to correlate with human judgements than binary yes/no.
- **Tradeoff**: Subjective scoring can vary slightly between runs if temperature > 0.

### 7. Conversation Thread Reconstruction
- **Decision**: Filtered and reconstructed only two-turn conversations (Customer -> Brand) and limited to 10,000 cases.
- **Context**: The raw dataset contains 3M tweets.
- **Reason**: Multi-turn threads are extremely noisy. Two-turn conversations represent clear problem-resolution pairs perfect for RAG. Limiting to 10k keeps the FAISS index small and fast.
- **Tradeoff**: I lose complex, multi-day support resolutions.

### 8. Web Framework
- **Decision**: Used FastAPI.
- **Context**: Needed an API layer.
- **Reason**: Built-in validation with Pydantic, auto-generated OpenAPI docs, and extremely fast to write.
- **Tradeoff**: Slightly higher learning curve than Flask for absolute beginners, but industry standard for AI APIs.

### 9. FAISS Document Structure
- **Decision**: Embedded the customer message, but appended the brand response as metadata.
- **Context**: Needed to decide what text the vector database should index.
- **Reason**: The incoming query will be a customer message. I want to find historically similar *customer messages*, and then extract how the brand responded.
- **Tradeoff**: I don't index the resolution itself, meaning I can't search for "conversations where I issued a refund" directly.

### 10. Human vs Judge Agreement Method
- **Decision**: Used exact match or adjacent match (+/- 1 score) on a small human-annotated sample to prove the judge's reliability.
- **Context**: The assignment demands proof that the LLM judge is trustworthy.
- **Reason**: Exact/Adjacent match percentage is an easy-to-explain metric for correlation.
- **Tradeoff**: Doesn't use advanced statistical correlation like Cohen's Kappa, which might be overkill for an intern assessment.

### 11. Data Validation
- **Decision**: Used Pydantic for all API and Agent schemas.
- **Context**: LLM outputs are unpredictable.
- **Reason**: Enforces strict typing. If the LLM generates malformed JSON, Pydantic catches it immediately, allowing us to safely fail or fallback.
- **Tradeoff**: Requires mapping LLM string outputs carefully to the Pydantic models.

### 12. CI/CD Implementation
- **Decision**: Used GitHub Actions for automated testing.
- **Context**: The job description emphasizes CI/CD.
- **Reason**: Standard, free, and runs unit tests automatically on every PR.
- **Tradeoff**: Doesn't run full LLM evaluations in CI to save API costs and time.

### 13. Data Leakage Prevention (Train/Test Split)
- **Decision**: Split the reconstructed conversations into 95% Train and 5% Test, and only fed the Train set to the FAISS index.
- **Context**: I needed to sample 150 items for the Golden Set. If I pulled from the same pool FAISS searches, the AI would retrieve the exact case it was tested on.
- **Reason**: Splitting the data guarantees the evaluation is measuring true generalization, not just exact-match retrieval.
- **Tradeoff**: Reduces the size of the Knowledge Base slightly.

### 14. Insufficient Evidence Fallback
- **Decision**: Instructed the LLM to return `needs_human: true` if the retrieved FAISS evidence doesn't answer the specific question.
- **Context**: The RAG pipeline forces the LLM to use evidence, but what if the evidence is useless?
- **Reason**: Prevents the LLM from hallucinating an answer when historical context is irrelevant. Fail-safe behavior.
- **Tradeoff**: Increases the escalation rate slightly, but drastically improves safety.

### 15. API Rate Limit Resilience & Key Pooling
- **Decision**: Implemented a Factory/Strategy pattern with API Key Pooling and Fallback Providers (Gemini -> Groq).
- **Context**: Free-tier Gemini limits (15 Requests Per Minute / 1,500 Per Day) made evaluating 150 items impossible without crashing.
- **Reason**: By allowing comma-separated API keys in `.env` and rotating them on `429` (Rate Limit) or `403` (Blocked) errors, I guarantee continuous execution. If all primary keys burn out, the `FallbackProvider` elegantly shifts the workload to a secondary provider (like Groq) without dropping a single evaluation item.
- **Tradeoff**: Adds complexity to the LLM Provider service, but proves robust handling of brittle third-party APIs (a crucial real-world software engineering skill).
