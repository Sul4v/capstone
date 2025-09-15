import os
import csv
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from a .env file
load_dotenv()

# IMPORTANT: Create a file named .env in the same directory as this script.
# In that file, add the following line:
# GOOGLE_API_KEY='YOUR_API_KEY'
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please ensure it is set in your .env file.")

# Configure the Gemini client
genai.configure(api_key=API_KEY)

# Define the model and generation settings
# Using gemini-1.5-flash as it's fast and cost-effective for this task.
model = genai.GenerativeModel('gemini-2.5-pro')

# Define input and output file names
INPUT_CSV = '60questions.csv'
OUTPUT_CSV = 'generated_prompts.csv'

# Define the headers for the output file
OUTPUT_HEADERS = [
    'base_question_id',
    'category',
    'base_question',
    'assigned_persona',
    'prompt_type',
    'generated_prompt'
]

# --- System Prompt ---
# This is the core instruction for the LLM, telling it exactly how to format its response.
SYSTEM_PROMPT = """
You are an AI assistant specializing in educational prompt design for a research project. Your task is to rephrase a single base question into three distinct variants according to specific rules.

For each user request, you will receive a `BASE_QUESTION` and an assigned `PERSONA`.

Your goal is to generate three new questions (prompts) based on this input, following these exact styles:

1.  **Vanilla Question:** A direct command for an explanation. It MUST be structured as: `Explain [the BASE_QUESTION]`.

2.  **Mentor Persona Question:** A prompt that creates a teaching scenario. It MUST be structured like: `Imagine you are [PERSONA]. Explain [the BASE_QUESTION] to a student.`

3.  **Microlearning Question:** A concise, direct command that includes the persona and all constraints. It MUST follow the pattern: `In the style of [PERSONA], explain [the BASE_QUESTION] in under 150 words, using a clear metaphor or analogy.`

You MUST format your entire output as a single, valid JSON object. Do not include any text or markdown before or after the JSON block. The JSON object must contain exactly these three keys: `vanilla_question`, `mentor_persona_question`, and `microlearning_question`.

"""

def create_user_prompt(question, persona):
    """Formats the user prompt for the API call."""
    return f"BASE_QUESTION: {question}\nPERSONA: {persona}"

def generate_prompts(question, persona):
    """
    Sends a request to the Gemini API to generate the three prompt variants.

    Args:
        question (str): The base question.
        persona (str): The assigned persona.

    Returns:
        dict: A dictionary containing the three generated prompts, or None if an error occurs.
    """
    user_prompt = create_user_prompt(question, persona)
    full_prompt = [SYSTEM_PROMPT, user_prompt]

    try:
        # The response from Gemini should be a JSON string.
        # We set the response mime type to ensure JSON output.
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        response = model.generate_content(full_prompt, generation_config=generation_config)

        # The response text should be a clean JSON string.
        # We parse it into a Python dictionary.
        # Added robust error handling for cases where the response is not valid JSON.
        try:
            # The actual JSON content is in response.text
            generated_json = json.loads(response.text)
            return generated_json
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from response text: {response.text}")
            return None

    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return None

def main():
    """
    Main function to read the input CSV, process each row,
    call the Gemini API, and write the results to a new CSV.
    """
    print("Starting prompt generation process...")

    # Prepare the output file
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(OUTPUT_HEADERS)

        # Read the input file
        try:
            with open(INPUT_CSV, 'r', newline='', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                
                # UPDATED: Check for the user's specific column names
                required_columns = ['Question_ID', 'Category', 'Question', 'Suggested_Persona']
                if not all(col in reader.fieldnames for col in required_columns):
                    print(f"Error: Input CSV '{INPUT_CSV}' must contain the columns: {', '.join(required_columns)}")
                    return

                for row in reader:
                    # UPDATED: Using your column names 'Question_ID' and 'Suggested_Persona'
                    question_id = row['Question_ID']
                    category = row['Category']
                    base_question = row['Question']
                    persona = row['Suggested_Persona']

                    print(f"Processing Question #{question_id}: '{base_question[:50]}...'")

                    # Generate the prompts using the Gemini API
                    prompts_dict = generate_prompts(base_question, persona)

                    if prompts_dict:
                        # Write the three generated prompts to the output file
                        writer.writerow([
                            question_id, category, base_question, persona,
                            'vanilla', prompts_dict.get('vanilla_question', 'GENERATION_ERROR')
                        ])
                        writer.writerow([
                            question_id, category, base_question, persona,
                            'mentor_persona', prompts_dict.get('mentor_persona_question', 'GENERATION_ERROR')
                        ])
                        writer.writerow([
                            question_id, category, base_question, persona,
                            'microlearning', prompts_dict.get('microlearning_question', 'GENERATION_ERROR')
                        ])
                        print(f"  -> Successfully generated and saved 3 prompts for Question #{question_id}.")
                    else:
                        # Handle cases where the API call failed
                        print(f"  -> Failed to generate prompts for Question #{question_id}. Skipping.")
                        # Write error rows for tracking
                        writer.writerow([question_id, category, base_question, persona, 'vanilla', 'API_CALL_FAILED'])
                        writer.writerow([question_id, category, base_question, persona, 'mentor_persona', 'API_CALL_FAILED'])
                        writer.writerow([question_id, category, base_question, persona, 'microlearning', 'API_CALL_FAILED'])

        except FileNotFoundError:
            print(f"Error: The input file '{INPUT_CSV}' was not found.")
            print("Please make sure the file exists and has the correct name and format.")
            return

    print(f"\nProcess complete. All generated prompts have been saved to '{OUTPUT_CSV}'.")

if __name__ == '__main__':
    main()
