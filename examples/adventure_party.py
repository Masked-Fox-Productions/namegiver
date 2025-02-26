import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.namegiver import generate_unique_name, get_token_usage

def generate_party_names(party_members, past_names=None):
    """
    Generate unique names for a party of characters based on their roles.
    
    Args:
        party_members (list): List of character role descriptions
        past_names (list): Optional list of names to avoid
    
    Returns:
        dict: Mapping of roles to generated names
    """
    past_names = past_names or []
    party = {}
    
    for member in party_members:
        name = generate_unique_name(member, past_names)
        if name:
            party[member] = name
            past_names.append(name)
    
    return party

def print_party(title, party):
    """Pretty print the party members and their names."""
    print(f"\n{title}")
    print("=" * len(title))
    for role, name in party.items():
        print(f"{name:20} - {role}")

def main():
    # Fantasy Party
    fantasy_party_members = [
        "noble paladin who upholds justice",
        "mysterious elven ranger from the ancient woods",
        "wise and elderly wizard specializing in fire magic",
        "cheerful halfling rogue with quick fingers",
        "dwarven cleric devoted to the forge god"
    ]
    
    fantasy_party = generate_party_names(fantasy_party_members)
    print_party("🗡️  Fantasy Adventure Party", fantasy_party)
    
    # Keep track of all names to ensure uniqueness across both parties
    all_names = list(fantasy_party.values())
    
    # Sci-Fi Party
    scifi_party_members = [
        "grizzled space mining captain",
        "cyberpunk hacker prodigy",
        "hotshot starship pilot",
        "ex-military combat engineer",
        "xenobiologist specializing in alien life"
    ]
    
    scifi_party = generate_party_names(scifi_party_members, all_names)
    print_party("🚀 Space Opera Crew", scifi_party)
    
    # Print token usage report
    print("\n📊 Token Usage Report")
    print("==================")
    print(get_token_usage())

if __name__ == "__main__":
    main()
