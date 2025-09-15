import os
import csv
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
import time

# Load environment variables from a .env file
load_dotenv()

# --- Configuration ---
# Get the API keys from environment variables
# Align behavior with Claude script: support both multiple keys and single key fallback.
API_KEYS_STR = os.getenv("OPENAI_API_KEYS")
if not API_KEYS_STR:
    # Fallback to single key if multiple keys not provided
    single_key = os.getenv("OPENAI_API_KEY")
    if single_key:
        API_KEYS = [single_key]
    else:
        raise ValueError(
            "Neither OPENAI_API_KEYS nor OPENAI_API_KEY found in environment variables. Please set one in your .env file."
        )
else:
    API_KEYS = [key.strip() for key in API_KEYS_STR.split(',')]

if not API_KEYS:
    raise ValueError("No API keys found.")

API_KEY = API_KEYS[0]
# Instantiate the OpenAI client
client = OpenAI(api_key=API_KEY)

# Specify the input and output file names
INPUT_CSV_FILE = 'generated_prompts.csv'
OUTPUT_CSV_FILE = 'generated_responses_openai.csv'
PROMPT_COLUMN_NAME = 'generated_prompt'

# Allow overriding the model via env var while preserving the current default.
# Using GPT-5 as requested - it's a reasoning model that needs specific handling
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-5')


def process_prompts():
    print(f"Starting to process prompts from '{INPUT_CSV_FILE}' with OpenAI...")

    try:
        with open(INPUT_CSV_FILE, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['openai_response']

            with open(OUTPUT_CSV_FILE, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                rows = list(reader)
                row_index = 0
                while row_index < len(rows):
                    row = rows[row_index]
                    prompt = row[PROMPT_COLUMN_NAME]
                    print(f"Processing row {row_index + 1}: Sending prompt to OpenAI API...")
                    try:
                        # Use the correct GPT-5 API: client.responses.create()
                        # Based on official documentation with reasoning and verbosity controls
                        response = client.responses.create(
                            model=OPENAI_MODEL,
                            input=prompt,
                            reasoning={"effort": "medium"},  # Set reasoning effort to medium
                            text={"verbosity": "medium"}     # Set text verbosity to medium
                        )
                        
                        # Extract the response using the correct GPT-5 response structure
                        if hasattr(response, 'output_text') and response.output_text:
                            openai_response = response.output_text.strip()
                            print(f"✓ GPT-5 response received ({len(response.output_text)} chars)")
                        else:
                            # Try alternative response fields if output_text is not available
                            print(f"Debug - Full response structure: {response}")
                            print(f"Debug - Available attributes: {dir(response)}")
                            openai_response = "GPT-5 response received but output_text field is empty or missing"
                            
                        row['openai_response'] = openai_response
                        writer.writerow(row)
                        outfile.flush()
                        print(f"Successfully received and saved response for row {row_index + 1}.")
                        row_index += 1
                    except RateLimitError:
                        print("Rate limit hit. Waiting 60 seconds before retrying the same row.")
                        time.sleep(60)
                        continue
                    except Exception as e:
                        print(f"An error occurred while processing row {row_index + 1}: {e}")
                        row['openai_response'] = f"Error: {e}"
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