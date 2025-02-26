import os
import openai
import argparse
from dotenv import load_dotenv
from Levenshtein import distance

# Load API key from .env file or environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ECONOMY_MODE = os.getenv("ECONOMY_MODE", "True").lower() == "true"

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# OpenAI Model selection
MODEL = "gpt-3.5-turbo" if ECONOMY_MODE else "gpt-4"

# Track token usage
class TokenTracker:
    def __init__(self):
        self.total_tokens = 0

    def add_usage(self, token_count):
        self.total_tokens += token_count

    def report(self):
        return {"total_tokens_used": self.total_tokens}
        
    def reset(self):
        """Reset the token counter back to 0."""
        self.total_tokens = 0

# Global tracker instance
token_tracker = TokenTracker()

def is_too_similar(new_name, past_names, threshold=2):
    """
    Checks if a newly generated name is too similar to past names using Levenshtein distance.

    Args:
        new_name (str): The newly generated name.
        past_names (list): List of previously generated names.
        threshold (int): Max similarity score to allow. Lower means stricter filtering.

    Returns:
        bool: True if name is too similar, False otherwise.
    """
    return any(distance(new_name.lower(), old.lower()) <= threshold for old in past_names)

def generate_unique_name(prompt: str, past_names=None, max_tokens=10, max_attempts=5):
    """
    Generates a distinct character name while avoiding past names.

    Args:
        prompt (str): Description of the name type.
        past_names (list, optional): Names to avoid generating similar ones.
        max_tokens (int): Maximum number of output tokens for the name.
        max_attempts (int): Maximum retries if a name is too similar to past ones.

    Returns:
        str: The generated name.
    """
    global token_tracker  # Declare global at the start of function
    
    if not os.getenv("OPENAI_API_KEY"):  # Check environment directly
        raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY as an environment variable.")

    past_names = past_names or []  # Default to empty list if None

    for _ in range(max_attempts):
        avoid_list = ", ".join(past_names) if past_names else "None"
        full_prompt = f"""
        Generate a unique character name following this description: {prompt}.
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
            return f"Error generating name: {str(e)}"

    return None  # Return None if no distinct name found

def get_token_usage():
    """
    Returns a report of the total OpenAI tokens used.
    """
    return token_tracker.report()

# Command Line Interface
def main():
    parser = argparse.ArgumentParser(description="Generate a fictional character name using AI.")
    parser.add_argument("prompt", type=str, help="Description of the name type (e.g., 'cyberpunk hacker')")
    parser.add_argument("--past-names", nargs="*", help="List of previously generated names to avoid")
    parser.add_argument("--max-tokens", type=int, default=10, help="Maximum number of output tokens (default: 10)")
    parser.add_argument("--report", action="store_true", help="Show token usage report")

    args = parser.parse_args()

    if args.report:
        print("Token Usage Report:", get_token_usage())
    else:
        print(generate_unique_name(args.prompt, args.past_names or []))

if __name__ == "__main__":
    main()
