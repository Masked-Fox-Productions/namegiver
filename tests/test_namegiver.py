import pytest
import os
from unittest.mock import patch, MagicMock
from src.namegiver import (
    TokenTracker,
    is_too_similar,
    generate_unique_name,
    get_token_usage,
    token_tracker
)

# Test TokenTracker class
def test_token_tracker_initialization():
    tracker = TokenTracker()
    assert tracker.total_tokens == 0

def test_token_tracker_add_usage():
    tracker = TokenTracker()
    tracker.add_usage(50)
    assert tracker.total_tokens == 50
    tracker.add_usage(25)
    assert tracker.total_tokens == 75

def test_token_tracker_report():
    tracker = TokenTracker()
    tracker.add_usage(100)
    assert tracker.report() == {"total_tokens_used": 100}

# Test name similarity checking
@pytest.mark.parametrize("new_name,past_names,threshold,expected", [
    ("John", ["Jon"], 2, True),
    ("Alexander", ["Alexandra"], 2, False),
    ("Bob", ["Robert"], 2, False),
    ("Sam", ["Samuel", "Samantha"], 2, True),
    ("", [], 2, False),
])
def test_is_too_similar(new_name, past_names, threshold, expected):
    assert is_too_similar(new_name, past_names, threshold) == expected

# Test name generation
@patch('openai.ChatCompletion.create')
def test_generate_unique_name_success(mock_create):
    # Mock successful API response
    mock_response = {
        "choices": [{
            "message": {"content": "Zephyr"}
        }],
        "usage": {"total_tokens": 50}
    }
    mock_create.return_value = mock_response
    
    result = generate_unique_name("fantasy wizard", past_names=["Merlin", "Gandalf"])
    assert result == "Zephyr"
    assert token_tracker.total_tokens == 50

@patch('openai.ChatCompletion.create')
def test_generate_unique_name_similar_names(mock_create):
    # Mock responses that generate similar names first, then a unique one
    responses = [
        {
            "choices": [{"message": {"content": "Jon"}}],
            "usage": {"total_tokens": 10}
        },
        {
            "choices": [{"message": {"content": "Zephyr"}}],
            "usage": {"total_tokens": 10}
        }
    ]
    mock_create.side_effect = responses
    
    result = generate_unique_name("fantasy wizard", past_names=["John"])
    assert result == "Zephyr"

@patch('openai.ChatCompletion.create')
def test_generate_unique_name_api_error(mock_create):
    # Mock API error
    mock_create.side_effect = Exception("API Error")
    
    result = generate_unique_name("fantasy wizard")
    assert "Error generating name" in result

def test_generate_unique_name_no_api_key():
    # Temporarily remove API key
    with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
        with pytest.raises(ValueError) as exc_info:
            generate_unique_name("fantasy wizard")
        assert "Missing OpenAI API key" in str(exc_info.value)

# Test max attempts limit
@patch('openai.ChatCompletion.create')
def test_generate_unique_name_max_attempts(mock_create):
    # Mock responses that always generate similar names
    mock_response = {
        "choices": [{
            "message": {"content": "John"}
        }],
        "usage": {"total_tokens": 10}
    }
    mock_create.return_value = mock_response
    
    result = generate_unique_name("fantasy wizard", past_names=["John"], max_attempts=3)
    assert result is None

# Test token usage reporting
def test_get_token_usage():
    global token_tracker
    token_tracker = TokenTracker()  # Reset global tracker
    token_tracker.add_usage(75)
    assert get_token_usage() == {"total_tokens_used": 75}

# Test environment variables
def test_environment_variables():
    assert 'OPENAI_API_KEY' in os.environ, "OPENAI_API_KEY should be set"
    assert 'ECONOMY_MODE' in os.environ, "ECONOMY_MODE should be set"
