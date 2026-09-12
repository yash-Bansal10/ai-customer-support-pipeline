# Product Requirements Document (PRD)

## Product Overview
Customer support teams at large brands face overwhelming volumes of queries on social media. A majority of these queries are repetitive. However, current automated systems (chatbots) often hallucinate policies, leading to customer dissatisfaction and brand risk. This product is an AI-based customer support pipeline that automatically handles customer queries *only* when it can ground its responses in historical evidence, and safely escalates risky or novel queries to a human agent.

## Problem Statement
Simply generating an answer using an LLM is insufficient because LLMs hallucinate policies, invent refunds, or give bad technical advice. I need a system that can be trusted. It must be capable of saying "I don't have enough evidence to answer this safely."

## Goals
- Classify customer intent from incoming messages.
- Retrieve relevant historical support cases from a vector database.
- Generate responses grounded exclusively in retrieved evidence.
- Autonomously decide whether the case can be auto-handled.
- Escalate uncertain or high-risk cases to a human.
- Measure system performance thoroughly (LLM-as-a-judge, Baselines).

## Non-Goals
- Production-scale Hiver replacement.
- Real Twitter integration (I only use a static dataset).
- Autonomous account actions or payment processing.

## User Stories
- **As a Customer**, I want instant, accurate support for my query without waiting for a human agent.
- **As a Support Agent**, I want the AI to handle repetitive queries so I can focus on complex, high-risk cases.
- **As a Support Manager**, I want the AI to escalate cases when it is unsure, rather than lying to customers.

## Functional Requirements
- **FR-001**: The system must expose an API endpoint (`POST /support`) that accepts a customer message.
- **FR-002**: The system must classify the message into predefined intents.
- **FR-003**: The system must retrieve up to K related historical conversations.
- **FR-004**: The system must return an explicit decision (`AUTO` or `ESCALATE`) along with a reason.
- **FR-005**: The system must generate a reply if the decision is `AUTO`.

## Non-Functional Requirements
- **Maintainability**: Clear separation of concerns (API vs Agent vs Retriever).
- **Testability**: Must include unit tests and an evaluation pipeline.
- **Reproducibility**: The pipeline and evaluation must be reproducible locally within 15 minutes.
