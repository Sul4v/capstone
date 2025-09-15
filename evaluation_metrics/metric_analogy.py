"""
metric_analogy.py

A small, well-documented utility for estimating analogical reasoning density in a text.

The main entrypoint is `calculate_analogical_reasoning(text: str) -> float`, which:
- Validates input and handles empty/non-string inputs by returning 0.0
- Defines groups of analogical signal phrases (using regex word boundaries \b)
- Builds a single combined regex (sorted longest-first) to avoid over-counting
- Counts analogical phrase hits and computes a per-100-words density score

This file also includes a simple test runner (`test_analogical_reasoning`) that
demonstrates usage and prints an interpretation guide for the resulting score.

Design notes:
- The combined regex pattern is constructed from grouped phrases to avoid double
  counting overlapping fragments. Sorting by descending length gives longer, more
  specific phrases priority when the regex engine finds non-overlapping matches.
- We intentionally keep the implementation simple and readable. The metric does
  not require heavy NLP; a clean regex approach is sufficient and robust.
"""

from __future__ import annotations

import re
from typing import List


def calculate_analogical_reasoning(text: str) -> float:
    """Compute analogical reasoning density per 100 words in the provided text.

    The function looks for a curated set of analogical and comparative signal
    phrases (e.g., "is like", "just as", "can be thought of as"). It counts how
    many times any of these phrases appear and returns a density score defined as:

        (total_analogy_phrases / total_words) * 100

    If the input is empty or not a string, the function returns 0.0.

    Parameters
    ----------
    text : str
        Input text to evaluate.

    Returns
    -------
    float
        Analogical phrase density per 100 words. Returns 0.0 for empty input or
        when the text has zero words.
    """
    # 1) Validate input early; keep behavior explicit and predictable.
    if not isinstance(text, str) or not text.strip():
        return 0.0

    # 2) Define grouped analogical signal phrases. Each phrase uses \b word
    #    boundaries to match the whole phrase. We use double-quoted raw strings
    #    to avoid escaping apostrophes in "it's" and to keep patterns readable.
    #
    #    Group A: Direct Analogy Phrases
    direct_analogy_phrases: List[str] = [
        r"\bis like\b",
        r"\bis similar to\b",
        r"\bis analogous to\b",
        r"\bthink of it as\b",
        r"\ban analogy for this is\b",
    ]

    #    Group B: Imaginative Prompts
    imaginative_prompts: List[str] = [
        r"\bimagine that\b",
        r"\bpicture this\b",
        r"\bsuppose you have\b",
        r"\bconsider a scenario\b",
    ]

    #    Group C: Comparative Phrases
    comparative_phrases: List[str] = [
        r"\bjust as\b",
        r"\bin the same way that\b",
        r"\bacts like\b",
        r"\bfunctions like\b",
    ]

    #    Group D: Metaphorical Bridges
    #    Match both straight and curly apostrophes in "it's" for robustness.
    metaphorical_bridges: List[str] = [
        r"\bcan be thought of as\b",
        r"\bserves as a bridge to\b",
        r"\bit[’']s a blueprint for\b",
    ]

    # 3) Combine all phrases, sort by length (desc) to prioritize longer, more
    #    specific phrases and reduce the chance of overlapping counts.
    all_phrases: List[str] = (
        direct_analogy_phrases
        + imaginative_prompts
        + comparative_phrases
        + metaphorical_bridges
    )

    phrases_sorted_desc: List[str] = sorted(all_phrases, key=len, reverse=True)

    combined_pattern_str: str = "(?:" + "|".join(phrases_sorted_desc) + ")"
    combined_pattern = re.compile(combined_pattern_str, flags=re.IGNORECASE)

    # 4) Count total words in the text. A simple tokenization using \b\w+\b is
    #    sufficient for this metric and keeps the implementation simple.
    words = re.findall(r"\b\w+\b", text)
    total_words = len(words)

    if total_words == 0:
        return 0.0

    # 5) Count the number of analogical phrases using the combined pattern. We
    #    use finditer to count non-overlapping matches.
    total_analogy_phrases = sum(1 for _ in combined_pattern.finditer(text))

    # 6) Compute density per 100 words and return.
    score = (total_analogy_phrases / total_words) * 100.0
    return score


def test_analogical_reasoning() -> None:
    """Run basic tests and print scores with a brief interpretation guide.

    We evaluate three representative cases:
      1) Strong analogical reasoning (multiple phrases present)
      2) No analogical reasoning (control text)
      3) Empty string (edge case)
    """
    strong_text = (
        "Think of it as a network: just as roads connect cities, data flows between nodes. "
        "In the same way that a blueprint guides builders, it's a blueprint for assembling components. "
        "This pipeline acts like a conveyor belt and functions like a relay team; an analogy for this is a postal system. "
        "You can imagine that each service serves as a bridge to the next."
    )

    none_text = (
        "This document explains the system architecture, listing modules, interfaces, and data formats. "
        "It focuses on configuration, versioning, and deployment without using comparative language."
    )

    empty_text = ""

    cases = [
        ("Strong analogical reasoning", strong_text),
        ("No analogical reasoning", none_text),
        ("Empty string", empty_text),
    ]

    print("Analogical Reasoning Density Score (per 100 words)\n")
    for label, sample in cases:
        score = calculate_analogical_reasoning(sample)
        print(f"- {label}: {score:.3f}")

    print("\nScore Interpretation:")
    print("- Strong: > 1.5 (frequent analogical/comparative phrasing)")
    print("- Moderate: 0.5–1.5 (occasional analogical indicators)")
    print("- Minimal: < 0.5 (rare or incidental analogical phrasing)")
    print("- None: 0.0 (no analogical phrases detected)")


if __name__ == "__main__":
    test_analogical_reasoning()


