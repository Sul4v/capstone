#!/usr/bin/env python3
"""
Main Evaluator Script for Response Analysis

This script processes a CSV file containing AI model responses and adds evaluation scores
for various metrics including motivational tone, clarity, concreteness, and causal depth.

"""

import pandas as pd
import logging
import re
import os
import argparse
from typing import Dict, Any

# Import all metric functions
from metric_motivational import calculate_motivational_tone
from metric_clarity import calculate_clarity
from metric_concreteness import calculate_concreteness
from metric_causal import calculate_causal_depth
from metric_analogy import calculate_analogical_reasoning
from metric_scaffolding import calculate_conceptual_scaffolding

# Set up logging for debugging and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)














def evaluate_response(text: str, model_name: str) -> Dict[str, float]:
    """
    Evaluate a single response using all available metrics.
    
    Args:
        text (str): The response text to evaluate
        model_name (str): Name of the model (for logging purposes)
        
    Returns:
        Dict[str, float]: Dictionary containing all evaluation scores
    """
    # Handle empty or None text
    if not text or pd.isna(text):
        logger.warning(f"Empty response for {model_name}, setting all scores to 0")
        return {
            'motivational_tone': 0.0,
            'clarity_score': 0.0,
            'concreteness_score': 0.0,
            'causal_depth': 0.0,
            'analogical_reasoning': 0.0,
            'conceptual_scaffolding': 1.0
        }
    
    # Calculate all evaluation scores using imported functions
    scores = {
        'motivational_tone': calculate_motivational_tone(text),
        'clarity_score': calculate_clarity(text),
        'concreteness_score': calculate_concreteness(text),
        'causal_depth': calculate_causal_depth(text),
        'analogical_reasoning': calculate_analogical_reasoning(text),
        'conceptual_scaffolding': calculate_conceptual_scaffolding(text)
    }
    
    logger.debug(f"Evaluated {model_name} response: {scores}")
    return scores


def main(input_csv_path: str, output_csv_path: str) -> None:
    """
    Main function to process the CSV file and add evaluation scores.
    
    Args:
        input_csv_path (str): Path to the input CSV file
        output_csv_path (str): Path to save the output CSV with scores
    """
    try:
        logger.info(f"Loading CSV file from: {input_csv_path}")
        
        # Load the input CSV into a pandas DataFrame with robust parsing for complex text
        df = pd.read_csv(input_csv_path, quoting=1, escapechar='\\', on_bad_lines='skip', lineterminator='\n')
        
        # Clean up column names (remove any carriage returns)
        df.columns = df.columns.str.strip().str.replace('\r', '')
        logger.info(f"Loaded DataFrame with {len(df)} rows and {len(df.columns)} columns")
        
        # Display the original columns for verification
        logger.info(f"Original columns: {list(df.columns)}")
        
        # Create new evaluation score columns for each model
        models = ['claude', 'gemini', 'openai']
        metrics = ['motivational_tone', 'clarity_score', 'concreteness_score', 'causal_depth', 'analogical_reasoning', 'conceptual_scaffolding']
        
        # Initialize all new columns with 0.0
        for model in models:
            for metric in metrics:
                column_name = f"{model}_{metric}"
                df[column_name] = 0.0
                logger.debug(f"Created column: {column_name}")
        
        logger.info("Created all evaluation score columns")
        
        # Iterate through each row and evaluate responses
        logger.info("Starting evaluation of responses...")
        
        for index, row in df.iterrows():
            if index % 1000 == 0:  # Log progress every 1000 rows
                logger.info(f"Processing row {index + 1}/{len(df)}")
            
            # Evaluate each model's response
            for model in models:
                response_column = f"{model}_response"
                
                if response_column in df.columns:
                    response_text = row[response_column]
                    scores = evaluate_response(response_text, model)
                    
                    # Store the scores in the corresponding columns
                    for metric in metrics:
                        column_name = f"{model}_{metric}"
                        df.at[index, column_name] = scores[metric]
                else:
                    logger.warning(f"Column {response_column} not found in DataFrame")
        
        logger.info("Completed evaluation of all responses")
        
        # Save the updated DataFrame to the output CSV file
        logger.info(f"Saving results to: {output_csv_path}")
        df.to_csv(output_csv_path, index=False)
        
        # Display summary statistics
        logger.info("Evaluation Summary:")
        for model in models:
            for metric in metrics:
                column_name = f"{model}_{metric}"
                if column_name in df.columns:
                    mean_score = df[column_name].mean()
                    logger.info(f"{column_name}: Mean = {mean_score:.3f}")
        
        logger.info("Script completed successfully!")
        
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_csv_path}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    """CLI entrypoint.

    Usage examples:
      - Use your generated prompts CSV (absolute path provided):
          python evaluation_metrics/main_evaluator.py \
            --input \
            "/Users/sulavshrestha/Documents/[1] Academics/Capstone/[0] Code/Prompt_Generation/responsesToPrompts/generated_prompts.csv" \
            --output \
            "/Users/sulavshrestha/Documents/[1] Academics/Capstone/[0] Code/Prompt_Generation/responsesToPrompts/generated_prompts_with_scores.csv"

      - Use any other CSV and write results next to it:
          python evaluation_metrics/main_evaluator.py --input /path/to/input.csv

    Notes:
      - If the CSV does not contain response columns like 'claude_response',
        'gemini_response', or 'openai_response', the script will still run and
        add score columns (initialized as 0.0), logging warnings for missing
        response columns.
    """

    parser = argparse.ArgumentParser(description="Evaluate AI responses with multiple metrics and save scores to CSV.")
    default_input = \
        "/Users/sulavshrestha/Documents/[1] Academics/Capstone/[0] Code/Prompt_Generation/responsesToPrompts/generated_prompts.csv"
    parser.add_argument(
        "--input",
        "-i",
        dest="input_csv",
        default=default_input,
        help="Path to input CSV (default: your generated_prompts.csv)",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output_csv",
        default=None,
        help="Path to output CSV (default: <input_dir>/output_with_scores.csv)",
    )

    args = parser.parse_args()
    input_file = args.input_csv
    if args.output_csv:
        output_file = args.output_csv
    else:
        input_dir = os.path.dirname(os.path.abspath(input_file)) or "."
        output_file = os.path.join(input_dir, "output_with_scores.csv")

    logger.info("Starting main evaluator script")
    logger.info(f"Input file: {input_file}")
    logger.info(f"Output file: {output_file}")

    main(input_file, output_file)
