#!/usr/bin/env python3

"""
Example of context-aware name generation using a project file.

This example demonstrates how to:
1. Load an existing project file
2. Generate a name that's aware of the project context
3. Save the updated project
"""

import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.namegiver.projects import load_project, save_project

def main():
    """Main function demonstrating context-aware name generation."""
    
    # Path to your project file
    project_file = "fantasy_adventure.json"
    
    try:
        # Load the project
        project = load_project(project_file)
        print(f"Loaded project: {project.name}")
        print(f"Project description: {project.description}")
        print(f"Existing categories: {', '.join(project.categories.keys())}")
        
        # Print existing names in each category
        for category in project.categories:
            names = project.get_names(category)
            print(f"\n{category.capitalize()} ({len(names)}):")
            for name in names:
                # Print a shortened description to avoid clutter
                desc = project.get_description(category, name)
                short_desc = desc[:50] + "..." if len(desc) > 50 else desc
                print(f"- {name}: {short_desc}")
        
        # Generate a new character name with context awareness
        print("\nGenerating a new character with context awareness...")
        prompt = "a wise sage who mentors the heroes"
        
        new_name = project.context_aware_generate(
            category="characters",
            prompt=prompt,
            should_generate_description=True
        )
        
        # Get the generated description
        description = project.get_description("characters", new_name)
        
        print(f"\nGenerated name: {new_name}")
        print(f"Description: {description}")
        
        # Save the updated project
        save_project(project, "updated_" + project_file)
        print(f"\nUpdated project saved to: updated_{project_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 