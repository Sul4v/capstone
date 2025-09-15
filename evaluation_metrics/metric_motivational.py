#!/usr/bin/env python3
"""
Motivational Tone Metric Calculator

This script provides a function to calculate motivational tone scores based on
the presence of specific motivational language patterns in text.

The function analyzes text for three types of motivational phrases:
1. Curiosity phrases - encourage exploration and interest
2. Confidence phrases - build self-assurance and capability
3. Anxiety-reducing phrases - provide comfort and reassurance

"""

import re
from typing import List


def calculate_motivational_tone(text: str) -> int:
    """
    Calculate the motivational tone score for a given text.
    
    This function counts occurrences of motivational phrases across three categories:
    - Curiosity phrases that encourage exploration and interest
    - Confidence phrases that build self-assurance and capability  
    - Anxiety-reducing phrases that provide comfort and reassurance
    
    Args:
        text (str): The text to analyze for motivational language patterns
        
    Returns:
        int: Total count of motivational phrases found in the text
        
    Example:
        >>> text = "Interestingly, this is a straightforward process. Don't worry if you find it challenging."
        >>> calculate_motivational_tone(text)
        3
    """
    # Handle empty or None text
    if not text or not isinstance(text, str):
        return 0
    
    # Define the three categories of motivational phrases
    curiosity_phrases = [
        'interestingly',
        'a surprising fact is',
        'have you ever wondered',
        'what if',
        'imagine if',
        'consider this',
        'think about',
        'suppose that',
        'let\'s explore',
        'here\'s something fascinating',
        'did you know',
        'it\'s remarkable that',
        'one intriguing aspect',
        'curiously enough',
        'fascinatingly'
    ]
    
    confidence_phrases = [
        'as you can see',
        'it\'s a straightforward process',
        'you already have the tools',
        'with a little practice',
        'you\'ll find that',
        'it becomes clear that',
        'you\'ll discover',
        'you\'ll notice',
        'you\'ll see how',
        'you\'ll understand',
        'you\'ll realize',
        'you\'ll get the hang of',
        'it\'s simple when',
        'you\'ve got this',
        'you can do this',
        'you\'re capable of',
        'you have what it takes'
    ]
    
    anxiety_reducing_phrases = [
        'don\'t worry if',
        'this is a common hurdle',
        'it\'s okay to',
        'no need to panic',
        'take your time',
        'there\'s no rush',
        'everyone struggles with',
        'it\'s normal to',
        'don\'t stress about',
        'relax, you\'ll get it',
        'be patient with yourself',
        'mistakes are part of learning',
        'it\'s fine to',
        'don\'t be afraid to',
        'there\'s nothing to fear',
        'you\'re doing great',
        'keep going, you\'re almost there'
    ]
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Initialize counters for each category
    curiosity_count = 0
    confidence_count = 0
    anxiety_reducing_count = 0
    
    # Count occurrences of curiosity phrases
    for phrase in curiosity_phrases:
        # Use word boundary matching to avoid partial matches
        pattern = r'\b' + re.escape(phrase) + r'\b'
        matches = len(re.findall(pattern, text_lower))
        curiosity_count += matches
    
    # Count occurrences of confidence phrases
    for phrase in confidence_phrases:
        pattern = r'\b' + re.escape(phrase) + r'\b'
        matches = len(re.findall(pattern, text_lower))
        confidence_count += matches
    
    # Count occurrences of anxiety-reducing phrases
    for phrase in anxiety_reducing_phrases:
        pattern = r'\b' + re.escape(phrase) + r'\b'
        matches = len(re.findall(pattern, text_lower))
        anxiety_reducing_count += matches
    
    # Calculate total motivational tone score
    total_score = curiosity_count + confidence_count + anxiety_reducing_count
    
    # Optional: Print detailed breakdown for debugging
    # print(f"Curiosity phrases: {curiosity_count}")
    # print(f"Confidence phrases: {confidence_count}")
    # print(f"Anxiety-reducing phrases: {anxiety_reducing_count}")
    # print(f"Total motivational tone score: {total_score}")
    
    return total_score


def test_motivational_tone():
    """
    Test function to demonstrate the calculate_motivational_tone function.
    
    This function provides examples of how the motivational tone calculator works
    with different types of text.
    """
    print("Testing Motivational Tone Calculator")
    print("=" * 40)
    
    # Test case 1: Text with multiple motivational phrases
    test_text_1 = """
    Interestingly, this is a straightforward process that you can master. 
    As you can see, you already have the tools needed. Don't worry if you 
    find it challenging at first - this is a common hurdle. With a little 
    practice, you'll discover how simple it becomes. It's okay to take your 
    time, and you'll get the hang of it soon enough.
    """
    
    score_1 = calculate_motivational_tone(test_text_1)
    print(f"Test 1 - Score: {score_1}")
    print(f"Text: {test_text_1.strip()}")
    print()
    
    # Test case 2: Text with no motivational phrases
    test_text_2 = """
    The algorithm processes data in linear time. It uses a hash table for 
    efficient lookups. The time complexity is O(n) and space complexity is O(n).
    """
    
    score_2 = calculate_motivational_tone(test_text_2)
    print(f"Test 2 - Score: {score_2}")
    print(f"Text: {test_text_2.strip()}")
    print()
    
    # Test case 3: Empty text
    test_text_3 = ""
    score_3 = calculate_motivational_tone(test_text_3)
    print(f"Test 3 - Score: {score_3}")
    print(f"Text: (empty)")
    print()
    
    print("Testing completed!")


if __name__ == "__main__":
    # Run the test function when script is executed directly
    test_motivational_tone()
