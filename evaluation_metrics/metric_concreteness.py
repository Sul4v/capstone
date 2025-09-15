#!/usr/bin/env python3
"""
Concreteness Score Metric Calculator

This script provides a function to calculate concreteness scores based on:
1. Word-level concreteness ratings from Brysbaert et al. (2014)
2. Presence of explicit example phrases

The concreteness score measures how concrete vs. abstract the language in a text is.
Higher scores indicate more concrete, tangible language.

"""

import pandas as pd
import re
import os
from typing import Dict, List, Tuple


# Global variable to store the concreteness lexicon
CONCRETENESS_LEXICON: Dict[str, float] = {}


def load_concreteness_lexicon(file_path: str = None) -> Dict[str, float]:
    """
    Load the concreteness ratings lexicon from a CSV file.
    
    This function loads the Brysbaert et al. (2014) concreteness norms dataset
    and creates a dictionary for fast word lookup.
    
    Args:
        file_path (str): Path to the concreteness ratings CSV file
        
    Returns:
        Dict[str, float]: Dictionary mapping words to their concreteness scores
        
    Note:
        The expected CSV format should have columns:
        - 'Word': The word/term
        - 'Conc.M': Mean concreteness rating (typically 1-5 scale)
        
        If the file doesn't exist, returns an empty dictionary.
    """
    global CONCRETENESS_LEXICON
    
    # If no file path provided, try to find the file in the evaluation_metrics directory
    if file_path is None:
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, "concreteness_ratings.csv")
    
    try:
        if os.path.exists(file_path):
            print(f"Loading concreteness lexicon from: {file_path}")
            
            # Load the CSV file
            df = pd.read_csv(file_path)
            
            # Check if required columns exist
            if 'Word' in df.columns and 'Conc.M' in df.columns:
                # Create dictionary mapping words to concreteness scores
                lexicon = dict(zip(df['Word'].str.lower(), df['Conc.M']))
                print(f"Successfully loaded {len(lexicon)} words from concreteness lexicon")
                return lexicon
            else:
                print(f"Warning: Required columns 'Word' and 'Conc.M' not found in {file_path}")
                print(f"Available columns: {list(df.columns)}")
                return {}
        else:
            print(f"Warning: Concreteness ratings file not found: {file_path}")
            print("Please download the Brysbaert concreteness norms dataset.")
            print("You can find it by searching for 'Brysbaert concreteness norms' online.")
            return {}
            
    except Exception as e:
        print(f"Error loading concreteness lexicon: {e}")
        return {}


def count_example_phrases(text: str) -> int:
    """
    Count the number of explicit example phrases in the text.
    
    These phrases indicate that the text is providing concrete examples,
    which contributes to the overall concreteness score.
    
    Args:
        text (str): The text to analyze for example phrases
        
    Returns:
        int: Count of example phrases found
    """
    # Define common example phrases that indicate concreteness
    example_phrases = [
        r'\bfor example\b',
        r'\bfor instance\b',
        r'\bconsider\b',
        r'\bsuch as\b',
        r'\blike\b',
        r'\bspecifically\b',
        r'\bto illustrate\b',
        r'\btake\b',
        r'\bsuppose\b',
        r'\bimagine\b',
        r'\bthink of\b',
        r'\bhere\'s\b',
        r'\bthis is\b',
        r'\bthat is\b'
    ]
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Count occurrences of each example phrase
    total_count = 0
    for phrase_pattern in example_phrases:
        matches = len(re.findall(phrase_pattern, text_lower))
        total_count += matches
    
    return total_count


def calculate_concreteness(text: str) -> float:
    """
    Calculate the concreteness score for a given text.
    
    This function combines two measures of concreteness:
    1. Average word-level concreteness from the Brysbaert lexicon
    2. Count of explicit example phrases
    
    Args:
        text (str): The text to analyze for concreteness
        
    Returns:
        float: Combined concreteness score
        
    Note:
        The final score combines:
        - Average word concreteness (normalized to 0-1 scale)
        - Example phrase count (weighted by 0.1)
    """
    # Handle empty or None text
    if not text or not isinstance(text, str):
        return 0.0
    
    # Use the global lexicon that was loaded at module import time
    if not CONCRETENESS_LEXICON:
        print("Warning: Concreteness lexicon not loaded. Please load it first.")
        return 0.0
    
    # Step 1: Count explicit example phrases
    example_phrase_count = count_example_phrases(text)
    
    # Step 2: Process text and calculate word-level concreteness
    # Convert to lowercase and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Look up concreteness scores for each word
    word_scores = []
    for word in words:
        if word in CONCRETENESS_LEXICON:
            word_scores.append(CONCRETENESS_LEXICON[word])
    
    # Calculate average word concreteness
    if word_scores:
        average_word_concreteness = sum(word_scores) / len(word_scores)
    else:
        average_word_concreteness = 0.0
    
    # Step 3: Combine the scores using the specified formula
    # Formula: (average_word_concreteness / 5) + (count_of_example_phrases * 0.1)
    # Division by 5 normalizes the 1-5 scale to 0-1
    normalized_word_score = average_word_concreteness / 5.0
    example_phrase_score = example_phrase_count * 0.1
    
    final_score = normalized_word_score + example_phrase_score
    
    return final_score


# Load the lexicon when the module is imported
CONCRETENESS_LEXICON = load_concreteness_lexicon()


def test_concreteness_calculation():
    """
    Test function to demonstrate the calculate_concreteness function.
    
    This function provides examples of how the concreteness calculator works
    with different types of text, showing the relationship between
    language specificity and concreteness scores.
    """
    print("Testing Concreteness Score Calculator")
    print("=" * 40)
    
    # Test case 1: Concrete text with examples
    test_text_1 = """
    For example, consider a red apple. Think of the smooth, shiny surface. 
    The apple is round and fits in your hand. It has a stem at the top.
    """
    
    score_1 = calculate_concreteness(test_text_1)
    print(f"Test 1 - Score: {score_1:.3f}")
    print(f"Text: {test_text_1.strip()}")
    print()
    
    # Test case 2: Abstract text with few concrete words
    test_text_2 = """
    The concept of justice involves moral principles and ethical considerations.
    It encompasses fairness, equality, and the distribution of resources.
    """
    
    score_2 = calculate_concreteness(test_text_2)
    print(f"Test 2 - Score: {score_2:.3f}")
    print(f"Text: {test_text_2.strip()}")
    print()
    
    # Test case 3: Mixed concrete and abstract text
    test_text_3 = """
    Democracy is a system where people vote. For instance, citizens go to 
    polling stations and mark ballots. The process involves counting votes 
    and determining winners.
    """
    
    score_3 = calculate_concreteness(test_text_3)
    print(f"Test 3 - Score: {score_3:.3f}")
    print(f"Text: {test_text_3.strip()}")
    print()
    
    # Test case 4: Empty text
    test_text_4 = ""
    score_4 = calculate_concreteness(test_text_4)
    print(f"Test 4 - Score: {score_4:.3f}")
    print(f"Text: (empty)")
    print()
    
    print("Testing completed!")
    print("\nNote: Scores will be 0.0 until the concreteness lexicon is loaded.")
    print("Please download the Brysbaert concreteness norms dataset and save it as 'concreteness_ratings.csv'")


def main():
    """
    Main function to demonstrate the concreteness metric system.
    
    This function shows how to load the lexicon and calculate scores.
    """
    print("Concreteness Metric System")
    print("=" * 30)
    
    # Try to load the concreteness lexicon
    global CONCRETENESS_LEXICON
    CONCRETENESS_LEXICON = load_concreteness_lexicon()
    
    if CONCRETENESS_LEXICON:
        print("✓ Concreteness lexicon loaded successfully!")
        print(f"  Loaded {len(CONCRETENESS_LEXICON)} words")
    else:
        print("✗ Concreteness lexicon not loaded")
        print("\nTo use this system, you need to:")
        print("1. Download the Brysbaert concreteness norms dataset")
        print("2. Save it as 'concreteness_ratings.csv' in the same directory")
        print("3. Ensure it has 'Word' and 'Conc.M' columns")
    
    print("\nRunning test cases...")
    test_concreteness_calculation()


if __name__ == "__main__":
    # Run the main function when script is executed directly
    main()
