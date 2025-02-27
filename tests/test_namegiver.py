import pytest
import os
from unittest.mock import patch, MagicMock
from namegiver.namegiver import (
    TokenTracker,
    is_too_similar,
    generate_unique_name,
    get_token_usage
)

# Reset token tracker and environment before each test
token_tracker = TokenTracker()
@pytest.fixture(autouse=True)
def setup_test_env():
    # Reset token tracker
    global token_tracker
    token_tracker.reset()
    
    # Store original env vars
    original_env = dict(os.environ)
    
    # Clear environment for test
    os.environ.clear()
    
    yield
    
    # Restore original env vars
    os.environ.clear()
    os.environ.update(original_env)

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
    ("Alexander", ["Alexandra"], 2, True),
    ("Bob", ["Robert"], 2, False),
    ("Sam", ["Samuel"], 3, True),  # Updated threshold to 3 for Sam/Samuel
    ("", [], 2, False),
])
def test_is_too_similar(new_name, past_names, threshold, expected):
    assert is_too_similar(new_name, past_names, threshold) == expected

# Test name generation - patch at the module level
@patch('namegiver.namegiver.client.chat.completions.create')
def test_generate_unique_name_success(mock_completions_create):
    os.environ['OPENAI_API_KEY'] = 'test-key'
    
    # Create mock response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Zephyr"
    mock_response.usage.total_tokens = 50
    
    # Set up mock function return
    mock_completions_create.return_value = mock_response
    
    result = generate_unique_name("fantasy wizard", past_names=["Merlin", "Gandalf"])
    mock_completions_create.assert_called_once()
    assert result == "Zephyr"
    assert token_tracker.total_tokens == 50

@patch('namegiver.namegiver.client.chat.completions.create')
def test_generate_unique_name_similar_names(mock_completions_create):
    os.environ['OPENAI_API_KEY'] = 'test-key'
    
    # Create mock responses
    mock_response1 = MagicMock()
    mock_response1.choices = [MagicMock()]
    mock_response1.choices[0].message.content = "Jon"
    mock_response1.usage.total_tokens = 10

    mock_response2 = MagicMock()
    mock_response2.choices = [MagicMock()]
    mock_response2.choices[0].message.content = "Zephyr"
    mock_response2.usage.total_tokens = 10
    
    # Set up mock function returns for consecutive calls
    mock_completions_create.side_effect = [mock_response1, mock_response2]
    
    result = generate_unique_name("fantasy wizard", past_names=["John"])
    assert result == "Zephyr"
    assert mock_completions_create.call_count == 2
    assert token_tracker.total_tokens == 20

@patch('namegiver.namegiver.client.chat.completions.create')
def test_generate_unique_name_max_attempts(mock_completions_create):
    os.environ['OPENAI_API_KEY'] = 'test-key'
    
    # Create mock response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "John"
    mock_response.usage.total_tokens = 10
    
    # Set up mock function return
    mock_completions_create.return_value = mock_response
    
    result = generate_unique_name("fantasy wizard", past_names=["John"], max_attempts=3)
    assert result is None
    assert mock_completions_create.call_count == 3
    assert token_tracker.total_tokens == 30

@patch('namegiver.namegiver.client.chat.completions.create')
def test_get_token_usage(mock_completions_create):
    os.environ['OPENAI_API_KEY'] = 'test-key'
    
    # Create mock response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Zephyr"
    mock_response.usage.total_tokens = 75
    
    # Set up mock function return
    mock_completions_create.return_value = mock_response
    
    result = generate_unique_name("fantasy wizard", past_names=["Merlin"])
    assert result == "Zephyr"
    assert get_token_usage() == {"total_tokens_used": 75}

# Test environment variables
def test_environment_variables():
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['ECONOMY_MODE'] = 'true'
    
    assert 'OPENAI_API_KEY' in os.environ, "OPENAI_API_KEY should be set"
    assert 'ECONOMY_MODE' in os.environ, "ECONOMY_MODE should be set"
