#!/usr/bin/env python3

"""
Integration test for context-aware name generation.

This script tests the context-aware generation feature with a real API call.
It requires a valid OpenAI API key in the environment.

To run:
1. Make sure your OPENAI_API_KEY is set in .env or environment variables
2. Run this script directly:
   python examples/test_context_aware_integration.py

The script will:
1. Create a small test project
2. Save it to a temporary file
3. Generate a name using context-aware generation
4. Display the results
5. Clean up the temporary file
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.namegiver.projects import NameProject, save_project, load_project

def main():
    """Main function for testing context-aware generation."""
    print("Starting context-aware name generation integration test...")
    
    # Check for API key
    from dotenv import load_dotenv
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment variables.")
        return
    
    # Create a temporary file for the test
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
        temp_file_path = tmp_file.name
    
    try:
        # Create a test project
        print("\nCreating test project...")
        project = NameProject("Test Fantasy World", "A small test world for integration testing")
        
        # Add some categories and names
        project.add_category("characters")
        project.add_name("characters", "Elira Dawnbringer", 
                        "A noble paladin with golden armor and a radiant aura, dedicated to vanquishing darkness.")
        project.add_name("characters", "Thorne Shadowwalker", 
                        "A mysterious rogue who moves silently through the shadows, with dark clothing and keen eyes.")
        
        project.add_category("locations")
        project.add_name("locations", "Brighthold", 
                        "A fortified city of white stone walls that gleam in the sunlight, known for its libraries and temples.")
        
        # Save the project
        save_project(project, temp_file_path)
        print(f"Project saved to temporary file: {temp_file_path}")
        
        # Load the project to simulate a real usage scenario
        loaded_project = load_project(temp_file_path)
        print("\nProject loaded successfully.")
        print(f"Project name: {loaded_project.name}")
        print(f"Categories: {', '.join(loaded_project.categories.keys())}")
        
        for category in loaded_project.categories:
            names = loaded_project.get_names(category)
            print(f"\n{category.capitalize()} ({len(names)}):")
            for name in names:
                # Print a shortened description
                desc = loaded_project.get_description(category, name)
                short_desc = desc[:50] + "..." if len(desc) > 50 else desc
                print(f"- {name}: {short_desc}")
        
        # Generate a new character with context awareness
        print("\nGenerating a new character with context awareness...")
        prompt = "an elderly wizard who serves as an advisor to the rulers of Brighthold"
        
        try:
            start_time = __import__('time').time()
            new_name = loaded_project.context_aware_generate(
                category="characters",
                prompt=prompt,
                should_generate_description=True
            )
            end_time = __import__('time').time()
            
            print(f"\nGeneration completed in {end_time - start_time:.2f} seconds")
            
            # Display the results
            print(f"\nGenerated name: {new_name}")
            description = loaded_project.get_description("characters", new_name)
            print(f"Description: {description}")
            
            # Save the updated project
            save_project(loaded_project, temp_file_path)
            print(f"\nUpdated project saved to: {temp_file_path}")
            
            # Test generating a location that references the new character
            print("\nGenerating a location that references the new character...")
            location_prompt = f"the tower where {new_name} conducts magical research"
            
            location_name = loaded_project.context_aware_generate(
                category="locations",
                prompt=location_prompt,
                should_generate_description=True
            )
            
            print(f"\nGenerated location: {location_name}")
            location_description = loaded_project.get_description("locations", location_name)
            print(f"Description: {location_description}")
            
            # Print final project stats
            print("\nFinal project statistics:")
            print(f"Characters: {len(loaded_project.get_names('characters'))}")
            print(f"Locations: {len(loaded_project.get_names('locations'))}")
            
            print("\nIntegration test completed successfully!")
            return True
            
        except Exception as e:
            print(f"\nError during context-aware generation: {str(e)}")
            return False
    
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_file_path)
            print(f"\nCleaned up temporary file: {temp_file_path}")
        except Exception as e:
            print(f"Warning: Could not delete temporary file: {str(e)}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 