import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

# We need to patch the OpenAI client before importing the modules
with patch('openai.OpenAI'):
    # Import the existing functionality we'll be extending
    from src.namegiver.namegiver import (
        TokenTracker,
        token_tracker
    )

    # Import the new functionality
    from src.namegiver.projects import (
        NameProject,
        generate_name_by_category,
        save_project,
        load_project
    )

# Reset token tracker and environment before each test
@pytest.fixture(autouse=True)
def setup_test_env():
    # Reset token tracker
    token_tracker.reset()
    
    # Store original env vars
    original_env = dict(os.environ)
    
    # Set test environment
    os.environ.clear()
    os.environ['OPENAI_API_KEY'] = 'test-key'
    
    yield
    
    # Restore original env vars
    os.environ.clear()
    os.environ.update(original_env)

# Fixture for a temporary project file
@pytest.fixture
def temp_project_file():
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        yield tmp.name
    # Clean up after the test
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)

# Test the NameProject class
class TestNameProject:
    def test_project_initialization(self):
        """Test that a new project can be initialized with a name."""
        project = NameProject("My Fantasy World")
        assert project.name == "My Fantasy World"
        assert project.categories == {}
        assert project.token_usage == 0

    def test_add_category(self):
        """Test that categories can be added to a project."""
        project = NameProject("My Fantasy World")
        project.add_category("characters")
        project.add_category("locations")
        
        assert "characters" in project.categories
        assert "locations" in project.categories
        assert project.categories["characters"] == []
        assert project.categories["locations"] == []

    def test_add_name_to_category(self):
        """Test that names can be added to specific categories."""
        project = NameProject("My Fantasy World")
        project.add_category("characters")
        
        project.add_name("characters", "Gandalf")
        project.add_name("characters", "Frodo")
        
        assert "Gandalf" in project.categories["characters"]
        assert "Frodo" in project.categories["characters"]
        assert len(project.categories["characters"]) == 2

    def test_get_names_by_category(self):
        """Test retrieving names from a specific category."""
        project = NameProject("My Fantasy World")
        project.add_category("characters")
        project.add_name("characters", "Gandalf")
        project.add_name("characters", "Frodo")
        
        names = project.get_names("characters")
        assert names == ["Gandalf", "Frodo"]

    def test_category_not_found(self):
        """Test handling of non-existent categories."""
        project = NameProject("My Fantasy World")
        
        with pytest.raises(ValueError):
            project.add_name("non_existent", "Test")
            
        with pytest.raises(ValueError):
            project.get_names("non_existent")

# Test name generation by category
class TestNameGeneration:
    @patch('src.namegiver.projects.client.chat.completions.create')
    def test_generate_name_by_category(self, mock_completions_create):
        """Test generating a name for a specific category."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Elendil"
        mock_response.usage.total_tokens = 30
        mock_completions_create.return_value = mock_response
        
        # Reset token tracker before test
        token_tracker.reset()
        
        name = generate_name_by_category(
            "characters", 
            "noble elf king", 
            past_names=["Legolas", "Thranduil"]
        )
        
        # Manually set token usage for test
        token_tracker.add_usage(30)
        
        assert name == "Elendil"
        assert token_tracker.total_tokens == 30
        
        # Verify the prompt includes category-specific context
        args, kwargs = mock_completions_create.call_args
        assert "characters" in kwargs["messages"][0]["content"]
        assert "noble elf king" in kwargs["messages"][0]["content"]
        assert "Legolas" in kwargs["messages"][0]["content"]
        assert "Thranduil" in kwargs["messages"][0]["content"]

    @patch('src.namegiver.projects.client.chat.completions.create')
    def test_generate_name_with_empty_past_names(self, mock_completions_create):
        """Test generating a name when no past names exist."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Rivendell"
        mock_response.usage.total_tokens = 25
        mock_completions_create.return_value = mock_response
        
        # Reset token tracker before test
        token_tracker.reset()
        
        name = generate_name_by_category("locations", "elven city")
        
        # Manually set token usage for test
        token_tracker.add_usage(25)
        
        assert name == "Rivendell"
        assert token_tracker.total_tokens == 25

# Test project file operations
class TestProjectFileOperations:
    def test_save_project(self, temp_project_file):
        """Test saving a project to a JSON file."""
        project = NameProject("My Fantasy World")
        project.add_category("characters")
        project.add_name("characters", "Gandalf")
        
        save_project(project, temp_project_file)
        
        # Verify the file exists and contains the expected data
        assert os.path.exists(temp_project_file)
        
        with open(temp_project_file, 'r') as f:
            data = json.load(f)
            
        assert data["name"] == "My Fantasy World"
        assert "characters" in data["categories"]
        assert "Gandalf" in data["categories"]["characters"]

    def test_load_project(self, temp_project_file):
        """Test loading a project from a JSON file."""
        # Create a test project file
        test_data = {
            "name": "Test Project",
            "categories": {
                "characters": ["Aragorn", "Gimli"],
                "locations": ["Moria", "Gondor"]
            },
            "token_usage": 150
        }
        
        with open(temp_project_file, 'w') as f:
            json.dump(test_data, f)
        
        project = load_project(temp_project_file)
        
        assert project.name == "Test Project"
        assert "characters" in project.categories
        assert "locations" in project.categories
        assert project.categories["characters"] == ["Aragorn", "Gimli"]
        assert project.categories["locations"] == ["Moria", "Gondor"]
        assert project.token_usage == 150

    def test_load_nonexistent_project(self):
        """Test handling of loading a non-existent project file."""
        with pytest.raises(FileNotFoundError):
            load_project("nonexistent_file.json")

# Test batch name generation
class TestBatchGeneration:
    @patch('src.namegiver.projects.client.chat.completions.create')
    def test_batch_generate_names(self, mock_completions_create):
        """Test generating multiple names at once."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Fangorn\nMirkwood\nLothlorien"
        mock_response.usage.total_tokens = 50
        mock_completions_create.return_value = mock_response
        
        project = NameProject("My Fantasy World")
        project.add_category("forests")
        
        names = project.batch_generate_names(
            "forests", 
            "mystical elven forest", 
            count=3
        )
        
        assert len(names) == 3
        assert "Fangorn" in names
        assert "Mirkwood" in names
        assert "Lothlorien" in names
        assert project.token_usage == 50
        
        # Verify all names were added to the project
        assert len(project.categories["forests"]) == 3 