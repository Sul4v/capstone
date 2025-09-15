"""
metric_scaffolding.py

Conceptual Scaffolding Metric
-----------------------------
This module estimates how well a text explains potentially unfamiliar/jargon terms.
It identifies candidate jargon words by filtering out common English words and stopwords,
then checks if those terms are defined in nearby context within the same sentence.

Scoring:
- Score = (# of jargon terms that are explained) / (total # of jargon terms)
- Edge case: If the input is empty or non-string, return 1.0 (no scaffolding needed).
- If no jargon is detected, return 1.0 (perfectly scaffolded for the audience).

External Data:
- Uses "common_words_top_30000.csv" with columns "word,count" (top words by frequency)
  Save this file next to the script. If it is not present, the script continues with
  an empty set (more terms may be treated as jargon).

NLTK Resources:
- Requires NLTK with 'punkt' (for sentence tokenization) and 'stopwords'. The script will
  attempt to download them on first run if missing.
"""

from __future__ import annotations

import os
import csv
import re
import logging
from typing import Set, List

import nltk
from nltk.corpus import stopwords


# Set up a simple module-level logger for helpful runtime messages.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _ensure_nltk_resource(resource_path: str, download_id: str) -> None:
    """Ensure an NLTK resource is available; download if not found.

    Parameters
    ----------
    resource_path : str
        e.g., 'tokenizers/punkt' or 'corpora/stopwords'
    download_id : str
        e.g., 'punkt' or 'stopwords' for nltk.download
    """
    try:
        nltk.data.find(resource_path)
    except LookupError:
        logger.info(f"Downloading NLTK resource: {download_id}")
        try:
            nltk.download(download_id, quiet=True)
        except Exception as ex:
            logger.warning(f"Failed to download NLTK resource '{download_id}': {ex}")


def _load_common_words() -> Set[str]:
    """Load common English words from 'common_words_top_30000.csv' (word,count).

    Returns an empty set if the file is missing or unreadable.
    """
    script_dir = os.path.dirname(__file__)
    csv_path = os.path.join(script_dir, 'common_words_top_30000.csv')

    if not os.path.exists(csv_path):
        logger.warning("common_words_top_30000.csv not found; COMMON_WORDS will be empty.")
        return set()

    common_words_from_csv: Set[str] = set()
    try:
        with open(csv_path, 'r', encoding='utf-8', newline='') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                word = (row.get('word') or '').strip().lower()
                if word and word.isalpha():
                    common_words_from_csv.add(word)
        logger.info(f"Loaded {len(common_words_from_csv)} common words from common_words_top_30000.csv")
    except Exception as ex:
        logger.warning(f"Error loading common_words_top_30000.csv: {ex}. COMMON_WORDS will be empty.")

    return common_words_from_csv


def _load_stop_words() -> Set[str]:
    """Load NLTK English stopwords with a safe fallback to an empty set."""
    _ensure_nltk_resource('corpora/stopwords', 'stopwords')
    try:
        return set(stopwords.words('english'))
    except Exception as ex:
        logger.warning(f"Failed to load NLTK stopwords: {ex}. STOP_WORDS will be empty.")
        return set()


# Ensure required NLTK resources are present for sentence tokenization and stopwords.
_ensure_nltk_resource('tokenizers/punkt', 'punkt')

# Global sets for fast membership checks.
COMMON_WORDS: Set[str] = _load_common_words()
STOP_WORDS: Set[str] = _load_stop_words()


def _safe_sent_tokenize(text: str) -> List[str]:
    """Tokenize text into sentences, falling back to a simple regex if needed.

    This keeps the function robust even if NLTK resources are unavailable.
    """
    try:
        return nltk.sent_tokenize(text)
    except LookupError:
        # Try one more time after ensuring resource
        _ensure_nltk_resource('tokenizers/punkt', 'punkt')
        try:
            return nltk.sent_tokenize(text)
        except Exception:
            pass
    except Exception:
        pass

    # Fallback: naive sentence split based on punctuation.
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s]


def calculate_conceptual_scaffolding(text: str) -> float:
    """Estimate how well the text explains potentially unfamiliar terms.

    Steps:
    1) Identify candidate jargon terms (length > 4, not common, not stopword).
    2) For each candidate, search for an inline definition within the same sentence.
    3) Score = (# defined terms) / (# candidate terms). Edge cases return 1.0.

    Parameters
    ----------
    text : str
        Input text to evaluate.

    Returns
    -------
    float
        Ratio of explained terms to total candidate terms (0.0 to 1.0).
    """
    # Handle empty or non-string input: perfectly scaffolded (no help needed)
    if not isinstance(text, str) or not text.strip():
        return 1.0

    sentences = _safe_sent_tokenize(text)

    # Step 1: Identify Potential Jargon
    jargon_terms: Set[str] = set()
    for word in re.findall(r"\b\w+\b", text):
        lower_word = word.lower()
        if len(lower_word) > 4 and lower_word.isalpha():
            if lower_word not in COMMON_WORDS and lower_word not in STOP_WORDS:
                jargon_terms.add(lower_word)

    # If no jargon is found, consider the text perfectly scaffolded
    if not jargon_terms:
        return 1.0

    # Step 2: Check for Definitions
    defined_jargon_count = 0
    for term in jargon_terms:
        term_word_boundary = rf"\b{re.escape(term)}\b"
        found_definition_for_term = False

        # Build definition patterns that include the term in context
        # - Parenthetical explanation: ( ... term ... )
        # - Term followed by definition indicators: which means, is defined as, also known as, refers to
        patterns = [
            rf"\([^)]*?{term_word_boundary}[^)]*?\)",
            rf"{term_word_boundary}[^.]*?\bwhich means\b",
            rf"{term_word_boundary}[^.]*?\bis defined as\b",
            rf"{term_word_boundary}[^.]*?\balso known as\b",
            rf"{term_word_boundary}[^.]*?\brefers to\b",
        ]

        for sentence in sentences:
            # Term must be present in the sentence first
            if not re.search(term_word_boundary, sentence, flags=re.IGNORECASE):
                continue

            # Check if any definition cue appears with the term
            for pat in patterns:
                if re.search(pat, sentence, flags=re.IGNORECASE):
                    defined_jargon_count += 1
                    found_definition_for_term = True
                    break
            if found_definition_for_term:
                break  # Move to the next term once defined

    # Step 3: Calculate Final Score
    score = defined_jargon_count / len(jargon_terms)
    return score


def test_conceptual_scaffolding() -> None:
    """Run simple tests to illustrate the metric and print an interpretation guide."""
    text_defined = (
        "We will study polymorphism, which means 'many forms', and encapsulation (hiding data)."
    )
    text_undefined = (
        "The algorithm uses polymorphism and encapsulation."
    )
    text_simple = (
        "Cats run fast and jump high."
    )

    cases = [
        ("Defines its jargon", text_defined),
        ("Uses jargon without defining", text_undefined),
        ("Simple text with no jargon", text_simple),
    ]

    print("Conceptual Scaffolding Score (explained terms / total candidate terms)\n")
    for label, sample in cases:
        score = calculate_conceptual_scaffolding(sample)
        print(f"- {label}: {score:.3f}")

    print("\nScore Interpretation:")
    print("- 1.0 = Excellent (all potential jargon is explained)")
    print("- 0.5–0.9 = Good (many terms are explained)")
    print("- < 0.5 = Poor (few or no terms are explained)")


if __name__ == "__main__":
    test_conceptual_scaffolding()


