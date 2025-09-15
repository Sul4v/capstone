#!/usr/bin/env python3
"""
Causal Metrics (Strict Connectives + Density and Sentence Ratio)

This module provides small, clear functions to measure how much a text uses
explicit causal connectives. It intentionally uses simple regex-based logic
for transparency and speed, following best practices in cohesion analysis
(similar in spirit to Coh-Metrix causal connectives incidence).

Provided metrics:
- calculate_causal_density(text, mode): causal connectives per 100 words
- calculate_causal_sentence_ratio(text, mode): fraction of sentences with ≥1 causal connective

Backward compatibility:
- calculate_causal_depth(text): wrapper that returns strict causal density (per 100 words)

Design choices:
- Two lists of connectives are supplied: "strict" (high-precision) and "expanded"
  (a bit broader). Use "strict" by default. Avoid ambiguous items (e.g., correlational
  or evidential verbs) to reduce false positives.
"""

import re
from typing import List


def _get_causal_phrases(mode: str = "strict") -> List[str]:
    """Return a curated list of causal connectives.

    - strict: High-precision explicit causal markers
    - expanded: Includes additional variants (e.g., "since" in causal sense)

    Notes
    -----
    We use regex with word boundaries and simple inflection patterns where helpful.
    Keep phrases non-overlapping as much as possible to avoid double counting.
    """
    strict_phrases: List[str] = [
        r"\bbecause\b",
        r"\bbecause of\b",
        r"\btherefore\b",
        r"\bthus\b",
        r"\bhence\b",
        r"\bconsequently\b",
        r"\bas a result\b",
        r"\bas a consequence\b",
        r"\bdue to\b",
        r"\bowing to\b",
        r"\bon account of\b",
        r"\bthereby\b",
        r"\blead(?:s|ing)? to\b",
        r"\bresult(?:s|ing)? in\b",
    ]

    expanded_only: List[str] = [
        # Potentially ambiguous but often causal in expository text
        r"\bsince\b",
        r"\bso that\b",
        r"\bin turn\b",
    ]

    if mode == "expanded":
        return strict_phrases + expanded_only
    return strict_phrases


def _compile_causal_pattern(phrases: List[str]) -> re.Pattern:
    """Compile a non-overlapping alternation regex, longest-first.

    Sorting by descending length reduces overlapping matches, so longer, more
    specific phrases (e.g., "as a result") are matched before shorter ones.
    """
    phrases_sorted = sorted(phrases, key=len, reverse=True)
    combined = "(?:" + "|".join(phrases_sorted) + ")"
    return re.compile(combined, flags=re.IGNORECASE)


def _count_causal_hits(text: str, mode: str = "strict") -> int:
    """Count the number of causal connective hits using the selected phrase list."""
    if not isinstance(text, str) or not text.strip():
        return 0
    pattern = _compile_causal_pattern(_get_causal_phrases(mode))
    return sum(1 for _ in pattern.finditer(text))


def calculate_causal_density(text: str, mode: str = "strict") -> float:
    """Calculate causal connective density per 100 words.

    Parameters
    ----------
    text : str
        Input text to evaluate.
    mode : str
        "strict" (default) or "expanded". Strict uses high-precision connectives.

    Returns
    -------
    float
        (num causal hits / total words) * 100. Returns 0.0 when text is empty
        or contains zero words.
    """
    if not isinstance(text, str) or not text.strip():
        return 0.0

    words = re.findall(r"\b\w+\b", text)
    total_words = len(words)
    if total_words == 0:
        return 0.0

    hits = _count_causal_hits(text, mode)
    return (hits / total_words) * 100.0


def _split_sentences(text: str) -> List[str]:
    """Naively split text into sentences using punctuation.

    This is intentionally simple to avoid heavy dependencies. Good enough for
    ratio-based metrics on expository text.
    """
    if not isinstance(text, str) or not text.strip():
        return []
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def calculate_causal_sentence_ratio(text: str, mode: str = "strict") -> float:
    """Fraction of sentences containing ≥1 causal connective (0.0–1.0).

    Parameters
    ----------
    text : str
        Input text to evaluate.
    mode : str
        "strict" (default) or "expanded".
    """
    sentences = _split_sentences(text)
    if not sentences:
        return 0.0
    pattern = _compile_causal_pattern(_get_causal_phrases(mode))
    num_causal_sentences = sum(1 for s in sentences if pattern.search(s) is not None)
    return num_causal_sentences / len(sentences)


def calculate_causal_depth(text: str) -> float:
    """Backward-compatible wrapper: strict causal density per 100 words.

    Example
    -------
    >>> text = "Because of the rain, the ground is wet. Therefore, we cannot play outside."
    >>> calculate_causal_depth(text)
    8.33  # 2 hits in 24 words ≈ 8.33 per 100 words
    """
    return calculate_causal_density(text, mode="strict")


def test_causal_depth():
    """Print example scores for strict/expanded density and sentence ratio.

    This helps quickly see how the metric behaves on representative texts.
    """
    print("Causal Metrics Demo")
    print("=" * 30)

    test_text_1 = (
        "Because the temperature dropped below freezing, the water froze. "
        "As a result, the pipes burst. Consequently, we had to call a plumber. "
        "Due to this emergency, we couldn't use the water. Therefore, we had to stay in a hotel."
    )

    test_text_2 = (
        "The algorithm processes data efficiently. Because it uses hash tables, lookups are fast. "
        "This leads to better performance. The implementation handles large datasets well."
    )

    test_text_3 = (
        "The computer processes information. Data flows through circuits. "
        "Memory stores results. The processor executes instructions."
    )

    cases = [
        ("Many causal connectives", test_text_1),
        ("Moderate causal language", test_text_2),
        ("Minimal causal language", test_text_3),
        ("Empty", ""),
    ]

    for label, sample in cases:
        strict_density = calculate_causal_density(sample, mode="strict")
        expanded_density = calculate_causal_density(sample, mode="expanded")
        strict_ratio = calculate_causal_sentence_ratio(sample, mode="strict")
        print(f"- {label}:")
        print(f"  strict density (/100w): {strict_density:.2f}")
        print(f"  expanded density (/100w): {expanded_density:.2f}")
        print(f"  strict sentence ratio: {strict_ratio:.2f}")
        print()

    print("Score Interpretation (density per 100 words):")
    print("- 0–2: Low causal language")
    print("- 2–5: Moderate causal language")
    print("- 5–10: High causal language")
    print("- >10: Very high causal language")


if __name__ == "__main__":
    # Run the test function when script is executed directly
    test_causal_depth()
