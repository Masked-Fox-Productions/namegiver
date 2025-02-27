import os
import json
from typing import List, Dict, Optional, Union
from pathlib import Path

# Import directly from namegiver module to access client and MODEL
from namegiver.namegiver import (
    generate_unique_name,
    is_too_similar,
    token_tracker,
    client,
    MODEL
)

class NameProject:
    """
    A class to manage collections of generated names organized by categories.
    
    Attributes:
        name (str): The name of the project.
        categories (Dict[str, List[str]]): Dictionary mapping category names to lists of names.
        token_usage (int): Total token usage for this project.
    """
    
    def __init__(self, name: str):
        """
        Initialize a new name project.
        
        Args:
            name (str): The name of the project.
        """
        self.name = name
        self.categories = {}
        self.token_usage = 0
    
    def add_category(self, category: str) -> None:
        """
        Add a new category to the project.
        
        Args:
            category (str): The name of the category to add.
        """
        if category not in self.categories:
            self.categories[category] = []
    
    def add_name(self, category: str, name: str) -> None:
        """
        Add a name to a specific category.
        
        Args:
            category (str): The category to add the name to.
            name (str): The name to add.
            
        Raises:
            ValueError: If the category does not exist.
        """
        if category not in self.categories:
            raise ValueError(f"Category '{category}' does not exist.")
        
        self.categories[category].append(name)
    
    def get_names(self, category: str) -> List[str]:
        """
        Get all names in a specific category.
        
        Args:
            category (str): The category to get names from.
            
        Returns:
            List[str]: List of names in the category.
            
        Raises:
            ValueError: If the category does not exist.
        """
        if category not in self.categories:
            raise ValueError(f"Category '{category}' does not exist.")
        
        return self.categories[category]
    
    def batch_generate_names(
        self, 
        category: str, 
        prompt: str, 
        count: int = 3, 
        max_tokens: int = 50
    ) -> List[str]:
        """
        Generate multiple names at once for a specific category.
        
        Args:
            category (str): The category to generate names for.
            prompt (str): Description of the names to generate.
            count (int): Number of names to generate.
            max_tokens (int): Maximum number of tokens for the response.
            
        Returns:
            List[str]: List of generated names.
            
        Raises:
            ValueError: If the category does not exist.
        """
        if category not in self.categories:
            raise ValueError(f"Category '{category}' does not exist.")
        
        past_names = self.categories[category]
        
        avoid_list = ", ".join(past_names) if past_names else "None"
        full_prompt = f"""
        Generate {count} unique {category} names following this description: {prompt}.
        Each name should be on a new line.
        Avoid names too similar to these: {avoid_list}.
        """
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=max_tokens
            )
            
            if not response.choices:
                raise ValueError("Invalid API response")
            
            generated_names = response.choices[0].message.content.strip().split('\n')
            generated_names = [name.strip() for name in generated_names if name.strip()]
            
            # Update token usage
            if hasattr(response, 'usage') and hasattr(response.usage, 'total_tokens'):
                # Use the global token_tracker
                token_tracker.add_usage(response.usage.total_tokens)
                self.token_usage += response.usage.total_tokens
            
            # Add names to the category
            for name in generated_names:
                if not is_too_similar(name, past_names):
                    self.categories[category].append(name)
            
            return generated_names
            
        except Exception as e:
            raise RuntimeError(f"Error generating names: {str(e)}")


def generate_name_by_category(
    category: str, 
    prompt: str, 
    past_names: Optional[List[str]] = None, 
    max_tokens: int = 10, 
    max_attempts: int = 5
) -> Optional[str]:
    """
    Generate a unique name for a specific category.
    
    Args:
        category (str): The category of name to generate (e.g., "characters", "locations").
        prompt (str): Description of the name type.
        past_names (List[str], optional): Names to avoid generating similar ones.
        max_tokens (int): Maximum number of output tokens for the name.
        max_attempts (int): Maximum retries if a name is too similar to past ones.
        
    Returns:
        Optional[str]: The generated name, or None if no unique name could be generated.
    """
    category_prompt = f"Generate a unique {category} name following this description: {prompt}."
    
    if not past_names:
        past_names = []
        
    avoid_list = ", ".join(past_names) if past_names else "None"
    full_prompt = f"""
    Generate a unique {category} name following this description: {prompt}.
    Avoid names too similar to these: {avoid_list}.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=max_tokens
        )

        if not response.choices:
            raise ValueError("Invalid API response")

        generated_name = response.choices[0].message.content.strip()
        
        if hasattr(response, 'usage') and hasattr(response.usage, 'total_tokens'):
            token_tracker.add_usage(response.usage.total_tokens)

        if not is_too_similar(generated_name, past_names):
            return generated_name
            
    except Exception as e:
        raise RuntimeError(f"Error generating name: {str(e)}")
        
    return None


def save_project(project: NameProject, filepath: Union[str, Path]) -> None:
    """
    Save a project to a JSON file.
    
    Args:
        project (NameProject): The project to save.
        filepath (Union[str, Path]): Path to save the project to.
        
    Raises:
        IOError: If the file cannot be written.
    """
    data = {
        "name": project.name,
        "categories": project.categories,
        "token_usage": project.token_usage
    }
    
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise IOError(f"Error saving project: {str(e)}")


def load_project(filepath: Union[str, Path]) -> NameProject:
    """
    Load a project from a JSON file.
    
    Args:
        filepath (Union[str, Path]): Path to load the project from.
        
    Returns:
        NameProject: The loaded project.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid project file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Project file not found: {filepath}")
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        project = NameProject(data["name"])
        project.token_usage = data.get("token_usage", 0)
        
        for category, names in data["categories"].items():
            project.add_category(category)
            for name in names:
                project.add_name(category, name)
        
        return project
        
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Invalid project file: {str(e)}") 