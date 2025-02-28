# Namegiver: AI-based Character Name Generator

A lightweight, OpenAI-powered Python library for generating **unique fictional character names** based on user-provided prompts. Designed for writers, game developers, and world-builders.

## Features
**AI-Generated Names** – Distinctive names based on user descriptions.  
**Ensures Name Distinctiveness** – Avoids generating names too similar to previous ones.  
**Supports CLI & API** – Use from the terminal or integrate into Python projects.  
**Economy Mode** – Uses GPT-3.5 by default; switch to GPT-4 if needed.  
**Token Usage Tracking** – Monitor OpenAI API token consumption.  

## Installation

### 1. Install via pip
```bash
pip install namegiver
```

This will install the package and all its dependencies.

### 2. Set Up API Key
Create a `.env` file in your project directory:

```ini
OPENAI_API_KEY=your-api-key-here
ECONOMY_MODE=True
```

Alternatively, set it in your shell:

```bash
export OPENAI_API_KEY="your-api-key-here"
export ECONOMY_MODE="True"
```

## Usage

### 1. Using the Python API
```python
from namegiver import generate_unique_name, get_token_usage

past_names = ["Elwin", "Alvin", "Elvin"]

# Generate a unique name while avoiding past names
print(generate_unique_name("sci-fi bounty hunter", past_names))

# Show token usage
print("Token Usage Report:", get_token_usage())
```

### 2. Using the CLI

#### Generate a Name
```bash
namegen "medieval knight"
```

Example Output:
```
Sir Aldrin of Westmere
```

#### Specify Maximum Token Length
```bash
namegen "steampunk engineer" --max-tokens 5
```

Example Output:
```
Brasswick
```

#### Avoid Similar Names
```bash
namegen "elf warrior" --past-names Legolas Thranduil Elrond
```

Example Output:
```
Faerion
```

#### Check Token Usage
```bash
namegen --report
```

Example Output:
```yaml
Token Usage Report: {'total_tokens_used': 50}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| OPENAI_API_KEY | (Required) | Your OpenAI API key |
| ECONOMY_MODE | True | If True, uses gpt-3.5-turbo. Set to False for GPT-4 |

## How It Works
- The library queries OpenAI's LLM to generate a name.
- If `past_names` is provided, it asks OpenAI to avoid those names.
- After generation, the name is checked using Levenshtein distance to prevent near-duplicates.
- If the generated name is too similar, the system regenerates up to 5 times.

## Development

### Run Locally
Clone the repo and install dependencies:

```bash
git clone https://github.com/yourusername/namegiver.git
cd namegiver
pip install -e .
```

### Run Tests
Run the test suite with:

```bash
pytest tests/
```

## Contributing
Contributions are welcome! Submit issues or pull requests.

## Roadmap

The following features are planned for future releases:

### Enhanced Name Generation
- **Multiple Categories** – Generate names for Characters, Locations, Historical Events, Artifacts, Monsters, and more
- **Category-Specific Prompting** – Tailored generation strategies for each name category
- **Batch Generation** – Create multiple names at once with consistent theming

### Project Management
- **Project Files** – Save and load collections of names as JSON project files
- **Categorized Storage** – Organize generated names by type within projects
- **Name History** – Track all previously generated names within a project

### Rich Content Generation
- **Descriptions** – Generate detailed descriptions for any named entity
- **Custom Prompting** – Fine-tune description generation with user-provided context
- **Context-Aware Generation** – Use existing project data as context for new generations

### User Interfaces
- **Flask Web Application** – Browse and manage projects through a web interface
- **Interactive Dashboard** – Visualize name relationships and categories
- **Export Options** – Save projects in various formats (JSON, CSV, PDF)

### Advanced Features
- **Name Relationships** – Define connections between generated entities
- **World Building Tools** – Generate consistent name sets for cohesive fictional worlds
- **API Improvements** – Enhanced developer tools for integration

## Context-Aware Name Generation

The context-aware generation feature uses the OpenAI Assistants API to generate names that are consistent with your existing worldbuilding.

### Using the Python API

```python
from namegiver.projects import load_project, save_project

# Load your project file
project = load_project("my_world.json")

# Generate a name that considers the project context
new_name = project.context_aware_generate(
    category="characters",
    prompt="a wise old wizard who lives in the northern mountains",
    should_generate_description=True
)

# The name is automatically added to your project
print(f"Generated: {new_name}")
print(f"Description: {project.get_description('characters', new_name)}")

# Save the updated project
save_project(project, "my_world.json")
```

### Using the CLI

```bash
# Generate a name with project context awareness
namegen "wise old wizard from the northern mountains" --context-aware --project-file my_world.json --category characters --description

# This will:
# 1. Load your project file
# 2. Generate a name consistent with existing worldbuilding
# 3. Add it to your project
# 4. Save the updated project
```

### How It Works

The context-aware generation feature:
1. Uploads your project file to OpenAI as an assistant file
2. Creates a specialized assistant with instructions to maintain consistency
3. Generates names that consider all existing names, descriptions, and relationships
4. Automatically handles cleanup of temporary resources

This creates a more cohesive naming experience where new generations fit naturally with your existing worldbuilding.

## License
This project is licensed under the MIT License.
