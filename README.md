# Namegiver: AI-based Character Name Generator

A lightweight, OpenAI-powered Python library for generating **unique fictional character names** based on user-provided prompts. Designed for writers, game developers, and world-builders.

## Features
✅ **AI-Generated Names** – Distinctive names based on user descriptions.  
✅ **Ensures Name Distinctiveness** – Avoids generating names too similar to previous ones.  
✅ **Supports CLI & API** – Use from the terminal or integrate into Python projects.  
✅ **Economy Mode** – Uses GPT-3.5 by default; switch to GPT-4 if needed.  
✅ **Token Usage Tracking** – Monitor OpenAI API token consumption.  

## Installation

### 1. Install via pip
```bash
pip install openai python-dotenv python-Levenshtein
```

### 2. Set Up API Key
Create a `.env` file in the project directory:

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
from name_generator import generate_unique_name, get_token_usage

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
git clone https://github.com/yourusername/character-name-generator.git
cd character-name-generator
pip install -e .
```

### Run Tests
(TBD: Add test cases)

```bash
pytest tests/
```

## Contributing
Contributions are welcome! Submit issues or pull requests.

## License
This project is licensed under the MIT License.