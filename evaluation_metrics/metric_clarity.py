#!/usr/bin/env python3
"""
Clarity Score Metric Calculator

This script provides a function to calculate clarity scores based on the
Flesch Reading Ease score from the textstat library.

The Flesch Reading Ease score measures how easy a text is to read:
- Higher scores (90-100) = Very easy to read
- Lower scores (0-30) = Very difficult to read

The function normalizes this score to a 0-1 range for easier interpretation.

"""

import textstat
from typing import Union


def calculate_clarity(text: str) -> float:
    """
    Calculate the clarity score for a given text using Flesch Reading Ease.
    
    This function uses the textstat library to compute the Flesch Reading Ease score,
    which measures how easy a text is to read. The score is then normalized to a 0-1 range
    where 1 represents very easy reading and 0 represents very difficult reading.
    
    Args:
        text (str): The text to analyze for clarity and readability
        
    Returns:
        float: Normalized clarity score between 0.0 and 1.0
        
    Example:
        >>> text = "This is a simple sentence. It is easy to read."
        >>> calculate_clarity(text)
        0.85  # This would be the normalized score
        
    Note:
        - Score of 100+ (very easy) → normalized to 1.0
        - Score of 0 or less (very difficult) → normalized to 0.0
        - Scores in between are proportionally scaled
    """
    # Handle empty or None text
    if not text or not isinstance(text, str):
        return 0.0
    
    try:
        # Calculate the Flesch Reading Ease score using textstat
        # Higher scores mean easier reading (90-100 = very easy, 0-30 = very difficult)
        flesch_score = textstat.flesch_reading_ease(text)
        
        # Normalize the score to a 0-1 range
        # Formula: max(0, min(score / 100, 1))
        # This ensures:
        # - Scores of 100+ become 1.0
        # - Scores of 0 or less become 0.0
        # - Scores in between are proportionally scaled
        normalized_score = max(0.0, min(flesch_score / 100.0, 1.0))
        
        return normalized_score
        
    except Exception as e:
        # Handle any errors that might occur during textstat processing
        # This could happen with very short texts, special characters, etc.
        print(f"Warning: Error calculating clarity score: {e}")
        return 0.0


def test_clarity_calculation():
    """
    Test function to demonstrate the calculate_clarity function.
    
    This function provides examples of how the clarity calculator works
    with different types of text, showing the relationship between
    text complexity and clarity scores.
    """
    print("Testing Clarity Score Calculator")
    print("=" * 40)
    
    # Test case 1: Simple, easy-to-read text
    test_text_1 = """
    This is a simple sentence. It uses basic words. The grammar is easy.
    A child could read this text. It has short sentences. The vocabulary is simple.
    """
    
    score_1 = calculate_clarity(test_text_1)
    print(f"Test 1 - Score: {score_1:.3f}")
    print(f"Text: {test_text_1.strip()}")
    print()
    
    # Test case 2: Medium complexity text
    test_text_2 = """
    The algorithm processes data in linear time complexity. It utilizes a hash table 
    for efficient lookups. The implementation demonstrates good programming practices.
    """
    
    score_2 = calculate_clarity(test_text_2)
    print(f"Test 2 - Score: {score_2:.3f}")
    print(f"Text: {test_text_2.strip()}")
    print()
    
    # Test case 3: Complex, technical text
    test_text_3 = """
    The quantum mechanical principles underlying the superposition of states necessitate 
    a fundamental reconsideration of classical computational paradigms. The entanglement 
    phenomena exhibit non-local correlations that challenge our intuitive understanding 
    of physical reality.
    """
    
    score_3 = calculate_clarity(test_text_3)
    print(f"Test 3 - Score: {score_3:.3f}")
    print(f"Text: {test_text_3.strip()}")
    print()
    
    # Test case 4: Empty text
    test_text_4 = ""
    score_4 = calculate_clarity(test_text_4)
    print(f"Test 4 - Score: {score_4:.3f}")
    print(f"Text: (empty)")
    print()
    
    # Test case 5: Very short text
    test_text_5 = "Hi."
    score_5 = calculate_clarity(test_text_5)
    print(f"Test 5 - Score: {score_5:.3f}")
    print(f"Text: {test_text_5}")
    print()
    
    print("Testing completed!")
    print("\nScore Interpretation:")
    print("- 0.8-1.0: Very easy to read")
    print("- 0.6-0.8: Easy to read")
    print("- 0.4-0.6: Moderate difficulty")
    print("- 0.2-0.4: Difficult to read")
    print("- 0.0-0.2: Very difficult to read")


if __name__ == "__main__":
    # Run the test function when script is executed directly
    test_clarity_calculation()
