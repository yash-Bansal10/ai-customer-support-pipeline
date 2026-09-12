import pytest
from unittest.mock import MagicMock, patch
from src.services.agent import SupportAgent
from src.models.api_models import SupportRequest

@pytest.fixture
def mock_agent():
    # Mocking out the external LLM and Retriever services to test pure business logic
    with patch('src.services.agent.get_llm_provider') as mock_llm_factory, \
         patch('src.services.agent.get_retriever') as mock_retriever_factory:
        
        mock_llm = MagicMock()
        mock_retriever = MagicMock()
        
        mock_llm_factory.return_value = mock_llm
        mock_retriever_factory.return_value = mock_retriever
        
        agent = SupportAgent()
        agent.llm = mock_llm
        agent.retriever = mock_retriever
        return agent

def test_low_confidence_escalation(mock_agent):
    """Test that a prediction below the confidence threshold is safely escalated."""
    # Arrange
    req = SupportRequest(message="My phone is broken")
    # Simulate the LLM returning a low confidence intent
    mock_agent.llm.generate_json.return_value = {"intent": "DEVICE_ISSUE", "confidence": 0.4}
    
    # Act
    response = mock_agent.process_request(req)
    
    # Assert
    assert response.decision == "ESCALATE"
    assert response.intent == "DEVICE_ISSUE"
    assert "confidence was too low" in response.reason

def test_account_issue_escalation(mock_agent):
    """Test that high-risk intents like ACCOUNT_ISSUE are escalated regardless of confidence."""
    # Arrange
    req = SupportRequest(message="I forgot my password")
    # High confidence, but it is a restricted intent
    mock_agent.llm.generate_json.return_value = {"intent": "ACCOUNT_ISSUE", "confidence": 0.95}
    
    # Act
    response = mock_agent.process_request(req)
    
    # Assert
    assert response.decision == "ESCALATE"
    assert response.intent == "ACCOUNT_ISSUE"
    assert "ACCOUNT_ISSUE to require human verification" in response.reason

def test_successful_auto_handle(mock_agent):
    """Test that safe intents with high confidence are auto-handled."""
    # Arrange
    req = SupportRequest(message="How do I restart my phone?")
    
    # Mock Intent Classification (High confidence, safe intent)
    def generate_json_side_effect(prompt):
        if "Classify" in prompt:
            return {"intent": "HOW_TO_QUERY", "confidence": 0.9}
        elif "You are an AI customer support agent" in prompt:
            return {"needs_human": False, "reply": "Hold the power button."}
        return {}
        
    mock_agent.llm.generate_json.side_effect = generate_json_side_effect
    
    # Act
    response = mock_agent.process_request(req)
    
    # Assert
    assert response.decision == "AUTO"
    assert response.reply == "Hold the power button."
