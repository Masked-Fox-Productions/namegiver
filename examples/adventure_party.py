import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.namegiver.namegiver import TokenTracker, token_tracker
from src.namegiver.projects import (
    NameProject, 
    generate_name_by_category,
    save_project
)

def create_fantasy_project():
    """
    Create a fantasy-themed name project with locations and characters.
    
    Returns:
        NameProject: A fantasy project with generated names and descriptions
    """
    # Create a new project with a description
    project = NameProject(
        "Fantasy Adventure World",
        "A magical realm of ancient forests, towering mountains, and hidden mysteries."
    )
    
    # Add categories
    project.add_category("locations")
    project.add_category("characters")
    
    # Generate a location for our adventure
    location_prompt = "mystical elven forest kingdom with ancient trees and magical rivers"
    location_name = generate_name_by_category(
        "locations", 
        location_prompt,
        should_generate_description=True
    )
    
    # Add the location to our project
    project.add_name("locations", location_name["name"], location_name["description"])
    
    # Fantasy party member descriptions
    fantasy_party_members = [
        "noble paladin who upholds justice",
        "mysterious elven ranger from the ancient woods",
        "wise and elderly wizard specializing in fire magic",
        "cheerful halfling rogue with quick fingers",
        "dwarven cleric devoted to the forge god"
    ]
    
    # Generate names for each party member
    past_names = []
    for member_desc in fantasy_party_members:
        character = generate_name_by_category(
            "characters", 
            member_desc,
            past_names=past_names,
            should_generate_description=True,
            description_prompt=f"character from {location_name['name']}"
        )
        
        project.add_name("characters", character["name"], character["description"])
        past_names.append(character["name"])
    
    return project

def create_scifi_project():
    """
    Create a sci-fi themed name project with locations and characters.
    
    Returns:
        NameProject: A sci-fi project with generated names and descriptions
    """
    # Create a new project with a description
    project = NameProject(
        "Space Opera Universe",
        "A vast cosmos of advanced technology, interstellar politics, and untamed frontiers."
    )
    
    # Add categories
    project.add_category("locations")
    project.add_category("characters")
    
    # Generate a location for our adventure
    location_prompt = "bustling space station at the edge of known space, filled with traders and mercenaries"
    location_name = generate_name_by_category(
        "locations", 
        location_prompt,
        should_generate_description=True
    )
    
    # Add the location to our project
    project.add_name("locations", location_name["name"], location_name["description"])
    
    # Sci-Fi party member descriptions
    scifi_party_members = [
        "grizzled space mining captain",
        "cyberpunk hacker prodigy",
        "hotshot starship pilot",
        "ex-military combat engineer",
        "xenobiologist specializing in alien life"
    ]
    
    # Generate names for each party member
    past_names = []
    for member_desc in scifi_party_members:
        character = generate_name_by_category(
            "characters", 
            member_desc,
            past_names=past_names,
            should_generate_description=True,
            description_prompt=f"character from {location_name['name']}"
        )
        
        project.add_name("characters", character["name"], character["description"])
        past_names.append(character["name"])
    
    return project

def print_wiki_entry(name, description):
    """Print a wiki-style entry for a name and its description."""
    print(f"\n## {name}")
    print(f"{description}")
    print("-" * 70)

def print_project_wiki(project):
    """Print all names and descriptions in a project as wiki entries."""
    print(f"\n# {project.name}")
    print(f"_{project.description}_")
    print("=" * 70)
    
    # Print locations
    print("\n# LOCATIONS")
    for location in project.get_names("locations"):
        print_wiki_entry(location, project.get_description("locations", location))
    
    # Print characters
    print("\n# CHARACTERS")
    for character in project.get_names("characters"):
        print_wiki_entry(character, project.get_description("characters", character))

def main():
    # Reset token counter
    token_tracker.reset()
    
    # Create our fantasy project
    print("Generating Fantasy Adventure World...")
    fantasy_project = create_fantasy_project()
    
    # Create our sci-fi project
    print("Generating Space Opera Universe...")
    scifi_project = create_scifi_project()
    
    # Print wiki entries for both projects
    print_project_wiki(fantasy_project)
    print_project_wiki(scifi_project)
    
    # Save the projects to files
    save_project(fantasy_project, "fantasy_adventure.json")
    save_project(scifi_project, "space_opera.json")
    
    print(f"\nProjects saved to fantasy_adventure.json and space_opera.json")
    
    # Print token usage report
    print("\n📊 Token Usage Report")
    print("==================")
    print(f"Total tokens used: {token_tracker.total_tokens}")

if __name__ == "__main__":
    main()
