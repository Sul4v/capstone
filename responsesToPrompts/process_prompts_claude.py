import os
import csv
from anthropic import Anthropic, RateLimitError
from dotenv import load_dotenv
import time

# Load environment variables from a .env file
load_dotenv()

# --- Configuration ---
# Get the API keys from environment variables
API_KEYS_STR = os.getenv("ANTHROPIC_API_KEYS")
if not API_KEYS_STR:
    # Fall back to single API key if multiple keys not provided
    single_key = os.getenv("ANTHROPIC_API_KEY")
    if single_key:
        API_KEYS = [single_key]
    else:
        raise ValueError("Neither ANTHROPIC_API_KEYS nor ANTHROPIC_API_KEY found in environment variables. Please set one in your .env file.")
else:
    API_KEYS = [key.strip() for key in API_KEYS_STR.split(',')]

if not API_KEYS:
    raise ValueError("No API keys found.")

current_api_key_index = 0
# Instantiate the Anthropic client (defaults to os.environ.get("ANTHROPIC_API_KEY"))
client = Anthropic(api_key=API_KEYS[current_api_key_index])

# Specify the input and output file names
INPUT_CSV_FILE = 'generated_prompts.csv'
OUTPUT_CSV_FILE = 'generated_responses_claude.csv'
PROMPT_COLUMN_NAME = 'generated_prompt'

# Model to use (Claude 4 Sonnet is the latest and most capable model)
CLAUDE_MODEL = 'claude-sonnet-4-20250514'


def switch_api_key():
    """
    Switches to the next available API key in the list.
    Returns True if a new key was successfully set, False otherwise.
    """
    global current_api_key_index, client
    current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
    print(f"Switching to Claude API key index {current_api_key_index}.")
    # Create new client with the new API key
    client = Anthropic(api_key=API_KEYS[current_api_key_index])
    time.sleep(1)
    return True


def process_prompts():
    print(f"Starting to process prompts from '{INPUT_CSV_FILE}' with Claude...")

    try:
        with open(INPUT_CSV_FILE, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['claude_response']

            with open(OUTPUT_CSV_FILE, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                rows = list(reader)
                row_index = 0
                while row_index < len(rows):
                    row = rows[row_index]
                    prompt = row[PROMPT_COLUMN_NAME]
                    print(f"Processing row {row_index + 1}: Sending prompt to Claude API...")
                    try:
                        # Claude API uses messages.create() instead of chat.completions.create()
                        response = client.messages.create(
                            model=CLAUDE_MODEL,
                            max_tokens=512,
                            temperature=0.7,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        # Claude response structure is different - content is a list
                        claude_response = response.content[0].text.strip()
                        row['claude_response'] = claude_response
                        writer.writerow(row)
                        outfile.flush()
                        print(f"Successfully received and saved response for row {row_index + 1}.")
                        row_index += 1
                    except RateLimitError:
                        print(f"Rate limit hit for Claude API key index {current_api_key_index}. Attempting to switch key.")
                        if not switch_api_key():
                            print("All Claude API keys have been rate-limited. Waiting before retrying.")
                            time.sleep(60)
                        continue
                    except Exception as e:
                        print(f"An error occurred while processing row {row_index + 1}: {e}")
                        row['claude_response'] = f"Error: {e}"
                        writer.writerow(row)
                        outfile.flush()
                        row_index += 1
                    time.sleep(1)
    except FileNotFoundError:
        print(f"Error: The file '{INPUT_CSV_FILE}' was not found.")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return
    print(f"\nProcessing complete. All responses have been saved to '{OUTPUT_CSV_FILE}'.")


if __name__ == "__main__":
    process_prompts() 