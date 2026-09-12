import pytest
from src.api.baselines import TrivialBaseline, KeywordBaseline

def test_trivial_baseline():
    baseline = TrivialBaseline(majority_class="DEVICE_ISSUE")
    assert baseline.predict("My password is lost") == "DEVICE_ISSUE"
    assert baseline.predict("My battery is dying") == "DEVICE_ISSUE"

def test_keyword_baseline():
    baseline = KeywordBaseline()
    
    # Should predict DEVICE_ISSUE
    assert baseline.predict("My phone screen is broken") == "DEVICE_ISSUE"
    
    # Should predict ACCOUNT_ISSUE
    assert baseline.predict("I forgot my password for icloud") == "ACCOUNT_ISSUE"
    
    # Should fall back to OTHER
    assert baseline.predict("Hello, are you there?") == "OTHER"
