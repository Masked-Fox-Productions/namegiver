import os
import json
from typing import List, Dict, Optional, Union, Any
from pathlib import Path
import tempfile

# Import directly from namegiver module to access client and MODEL
from src.namegiver.namegiver import (
    generate_unique_name,
    generate_description,
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
        description (str): A description of the project.
        categories (Dict[str, Dict[str, str]]): Dictionary mapping category names to dictionaries of names and descriptions.
        token_usage (int): Total token usage for this project.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a new name project.
        
        Args:
            name (str): The name of the project.
            description (str, optional): A description of the project.
        """
        self.name = name
        self.description = description
        self.categories = {}
        self.token_usage = 0
    
    def add_category(self, category: str) -> None:
        """
        Add a new category to the project.
        
        Args:
            category (str): The name of the category to add.
        """
        if category not in self.categories:
            self.categories[category] = {}
    
    def add_name(self, category: str, name: str, description: str = "") -> None:
        """
        Add a name with an optional description to a specific category.
        
        Args:
            category (str): The category to add the name to.
            name (str): The name to add.
            description (str, optional): A description of the name.
            
        Raises:
            ValueError: If the category does not exist.
        """
        if category not in self.categories:
            raise ValueError(f"Category '{category}' does not exist.")
        
        self.categories[category][name] = description
    
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
        
        return list(self.categories[category].keys())
    
    def get_description(self, category: str, name: str) -> str:
        """
        Get the description for a specific name in a category.
        
        Args:
            category (str): The category containing the name.
            name (str): The name to get the description for.
            
        Returns:
            str: The description of the name.
            
        Raises:
            ValueError: If the category or name does not exist.
        """
        if category not in self.categories:
            raise ValueError(f"Category '{category}' does not exist.")
        
        if name not in self.categories[category]:
            raise ValueError(f"Name '{name}' does not exist in category '{category}'.")
        
        return self.categories[category][name]
    
    def generate_description(self, category: str, name: str, prompt: str = None, max_tokens: int = 100) -> str:
        """
        Generate and store a description for an existing name.
        
        Args:
            category (str): The category containing the name.
            name (str): The name to generate a description for.
            prompt (str, optional): Additional context for the description.
            max_tokens (int): Maximum tokens for the description.
            
        Returns:
            str: The generated description.
            
        Raises:
            ValueError: If the category or name does not exist.
        """
        if category not in self.categories:
            raise ValueError(f"Category '{category}' does not exist.")
        
        if name not in self.categories[category]:
            raise ValueError(f"Name '{name}' does not exist in category '{category}'.")
        
        description = generate_description(name, category, prompt, max_tokens)
        
        # Update the description
        self.categories[category][name] = description
        
        return description
    
    def batch_generate_names(
        self, 
        category: str, 
        prompt: str, 
        count: int = 3, 
        max_tokens: int = 50,
        should_generate_descriptions: bool = False,
        description_prompt: str = None
    ) -> List[str]:
        """
        Generate multiple names at once for a specific category.
        
        Args:
            category (str): The category to generate names for.
            prompt (str): Description of the names to generate.
            count (int): Number of names to generate.
            max_tokens (int): Maximum number of tokens for the response.
            should_generate_descriptions (bool): Whether to also generate descriptions for the names.
            description_prompt (str, optional): Additional context for descriptions.
            
        Returns:
            List[str]: List of generated names.
            
        Raises:
            ValueError: If the category does not exist.
        """
        if category not in self.categories:
            raise ValueError(f"Category '{category}' does not exist.")
        
        past_names = list(self.categories[category].keys())
        
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
                    description = ""
                    if should_generate_descriptions:
                        description = generate_description(name, category, description_prompt)
                    self.categories[category][name] = description
            
            return generated_names
            
        except Exception as e:
            raise RuntimeError(f"Error generating names: {str(e)}")

    def context_aware_generate(
        self, 
        category: str, 
        prompt: str, 
        max_tokens: int = 50,
        should_generate_description: bool = False,
        description_prompt: str = None
    ) -> str:
        """
        Generate a name using the entire project as context.
        
        This method uploads the current project data to OpenAI,
        allowing the model to generate names that are aware of
        the entire worldbuilding context.
        
        Args:
            category (str): The category to generate a name for.
            prompt (str): Description of the name to generate.
            max_tokens (int): Maximum tokens for the name.
            should_generate_description (bool): Whether to also generate a description.
            description_prompt (str, optional): Additional context for the description.
            
        Returns:
            str: The generated name (and description if requested).
            
        Raises:
            ValueError: If the category does not exist.
        """
        if category not in self.categories:
            self.add_category(category)
        
        # Get all existing names across all categories
        all_names = []
        for cat in self.categories:
            all_names.extend(self.get_names(cat))
        
        # Create a temporary JSON file with the current project data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            project_data = {
                "name": self.name,
                "description": self.description,
                "categories": self.categories
            }
            json.dump(project_data, temp_file, indent=2)
            temp_file_path = temp_file.name
        
        try:
            # Upload the temporary file to OpenAI
            with open(temp_file_path, "rb") as file:
                file_obj = client.files.create(
                    file=file,
                    purpose="assistants"
                )
            
            # Create an assistant with the file attached
            assistant = client.beta.assistants.create(
                name=f"Namegiver for {self.name}",
                instructions=f"""
                You are a creative naming assistant for the project '{self.name}'. 
                Your task is to generate a name that fits the provided prompt while maintaining
                consistency with the existing worldbuilding context in the attached project file.
                
                Important guidelines:
                1. Generate a name that fits the '{category}' category
                2. The name should be consistent with the style and tone of existing names
                3. Avoid generating names too similar to existing ones
                4. Consider relationships between names and locations in the project
                5. The name should reflect the prompt: '{prompt}'
                """,
                model=MODEL,
                tools=[{"type": "retrieval"}],
                file_ids=[file_obj.id]
            )
            
            # Create a thread
            thread = client.beta.threads.create()
            
            # Add a message to the thread
            message_text = f"""
            Generate a unique name for a {category} with the following description: {prompt}.
            
            The name should be consistent with the style and world of '{self.name}' and
            consider the existing names and descriptions in the project.
            
            Avoid names too similar to these: {', '.join(all_names)}.
            """
            
            if should_generate_description:
                message_text += "\nAlso generate a brief, evocative description for this name."
                if description_prompt:
                    message_text += f" Consider this additional context: {description_prompt}"
            
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message_text
            )
            
            # Run the assistant
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
            
            # Poll for completion
            import time
            while run.status != "completed":
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run.status in ["failed", "cancelled", "expired"]:
                    raise ValueError(f"Assistant run failed with status: {run.status}")
            
            # Get the assistant's response
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            # Extract the generated name (and description if requested)
            assistant_message = next((m for m in messages.data if m.role == "assistant"), None)
            if not assistant_message:
                raise ValueError("No response received from the assistant")
            
            response_text = assistant_message.content[0].text.value
            
            # Parse the response
            if should_generate_description:
                # Attempt to split name and description if both were generated
                lines = [line.strip() for line in response_text.strip().split('\n') if line.strip()]
                if len(lines) >= 2:
                    name = lines[0]
                    description = '\n'.join(lines[1:])
                else:
                    # Fallback: treat the whole response as a name if can't parse properly
                    name = response_text.strip()
                    description = ""
                
                # Add the name and description to the project
                self.add_name(category, name, description)
                return name
            else:
                # Just extract the name (first non-empty line)
                name = next((line.strip() for line in response_text.strip().split('\n') if line.strip()), "")
                self.add_name(category, name, "")
                return name
                
        except Exception as e:
            raise ValueError(f"Error in context-aware generation: {str(e)}")
        finally:
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass  # Ignore cleanup errors
            
            # Delete the file from OpenAI
            try:
                client.files.delete(file_obj.id)
            except:
                pass  # Ignore cleanup errors


def generate_name_by_category(
    category: str, 
    prompt: str, 
    past_names: Optional[List[str]] = None, 
    max_tokens: int = 10, 
    max_attempts: int = 5,
    should_generate_description: bool = False,
    description_prompt: str = None
) -> Union[str, Dict[str, str]]:
    """
    Generate a unique name for a specific category.
    
    Args:
        category (str): The category of name to generate (e.g., "characters", "locations").
        prompt (str): Description of the name type.
        past_names (List[str], optional): Names to avoid generating similar ones.
        max_tokens (int): Maximum number of output tokens for the name.
        max_attempts (int): Maximum retries if a name is too similar to past ones.
        should_generate_description (bool): Whether to also generate a description.
        description_prompt (str, optional): Additional context for the description.
        
    Returns:
        Union[str, Dict[str, str]]: The generated name, or a dict with name and description if should_generate_description is True.
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
            if should_generate_description:
                description = generate_description(generated_name, category, description_prompt)
                return {"name": generated_name, "description": description}
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
        "description": project.description,
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
        
        project = NameProject(data["name"], data.get("description", ""))
        project.token_usage = data.get("token_usage", 0)
        
        for category, names_dict in data["categories"].items():
            project.add_category(category)
            for name, description in names_dict.items():
                project.add_name(category, name, description)
        
        return project
        
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Invalid project file: {str(e)}") 