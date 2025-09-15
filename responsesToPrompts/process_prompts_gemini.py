import os
import csv
import google.generativeai as genai
from dotenv import load_dotenv
import time
import re

# Load environment variables from a .env file
# This is a secure way to manage your API keys.
# Make sure you have a .env file in the same directory with:
# GOOGLE_API_KEYS="your_api_key_1,your_api_key_2,..."
load_dotenv()

# --- Configuration ---
# Get the API keys from environment variables
API_KEYS_STR = os.getenv("GOOGLE_API_KEYS")
if not API_KEYS_STR:
    raise ValueError("GOOGLE_API_KEYS not found in environment variables. Please set it in your .env file.")

# Split the comma-separated string into a list of keys
API_KEYS = [key.strip() for key in API_KEYS_STR.split(',')]
if not API_KEYS:
    raise ValueError("No API keys found in GOOGLE_API_KEYS.")

# Keep track of the current API key index
current_api_key_index = 0

# Configure the generative AI model with the first API key
genai.configure(api_key=API_KEYS[current_api_key_index])

# Specify the input and output file names
INPUT_CSV_FILE = 'generated_prompts.csv'
OUTPUT_CSV_FILE = 'generated_responses_gemini.csv'

# Specify the name of the column containing the prompts
PROMPT_COLUMN_NAME = 'generated_prompt'

# --- Model and Safety Settings ---
# Initialize the Generative Model
# You can choose the model that best suits your needs.
model = genai.GenerativeModel('gemini-2.5-pro')

# We are disabling all safety settings.
# This is not recommended for all use cases, but for this specific
# task, we assume the prompts are safe and we want to avoid
# blocking any responses.
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

def switch_api_key():
    """
    Switches to the next available API key in the list.
    Returns True if a new key was successfully set, False otherwise.
    """
    global current_api_key_index
    current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
    print(f"Switching to API key index {current_api_key_index}.")
    genai.configure(api_key=API_KEYS[current_api_key_index])
    # Give a moment for the new key to be recognized
    time.sleep(1)
    return True

def process_prompts():
    """
    Reads prompts from a CSV file, sends them to the Gemini API with key rotation,
    (key rotation is done if there are multiple keys in the .env file)
    and writes the results to a new CSV file.
    """
    print(f"Starting to process prompts from '{INPUT_CSV_FILE}'...")

    try:
        # Open the input CSV file for reading
        with open(INPUT_CSV_FILE, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['gemini_response']

            # Open the output CSV file for writing
            with open(OUTPUT_CSV_FILE, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                rows = list(reader)  # Read all rows into memory to allow retries

                row_index = 0
                while row_index < len(rows):
                    row = rows[row_index]
                    prompt = row[PROMPT_COLUMN_NAME]

                    print(f"Processing row {row_index + 1}: Sending prompt to Gemini API...")

                    try:
                        # Send the prompt to the Gemini API
                        response = model.generate_content(prompt, safety_settings=safety_settings)
                        gemini_response = response.text.strip()
                        row['gemini_response'] = gemini_response
                        writer.writerow(row)
                        outfile.flush()
                        print(f"Successfully received and saved response for row {row_index + 1}.")
                        row_index += 1  # Move to the next row

                    except Exception as e:
                        error_message = str(e)
                        # Check if the error is a rate limit error (429)
                        if "429" in error_message:
                            print(f"Rate limit hit for API key index {current_api_key_index}. Attempting to switch key.")
                            if not switch_api_key():
                                # This case is unlikely with the circular list but good for safety
                                print("All API keys have been rate-limited. Waiting before retrying.")
                                time.sleep(60) # Wait for a minute if all keys fail
                            # Do not increment row_index, so we retry the same row with the new key
                            continue
                        else:
                            # For other errors, record the error and move on
                            print(f"An error occurred while processing row {row_index + 1}: {e}")
                            row['gemini_response'] = f"Error: {e}"
                            writer.writerow(row)
                            outfile.flush()
                            row_index += 1 # Move to the next row

                    # A small delay to be considerate to the API
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