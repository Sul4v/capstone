#!/usr/bin/env python3
"""
Extract only the `generated_prompt` column from the three source CSV files and
write them to three new CSVs. This script uses only Python's standard library
for portability and simplicity.

Why this script?
- Keep it simple, readable, and dependency-free (no pandas needed).
- Make only the minimal necessary changes: read, filter one column, write.
- Add clear comments to explain each step in plain language.

How it works (high-level):
1) Define the input and output file names.
2) For each input file, read rows using csv.DictReader.
3) Validate that the `generated_prompt` column exists.
4) Write a new CSV with a single header: `generated_prompt`.
5) Copy values row-by-row, writing empty strings if a row is missing the value.

Testing:
- Run the script. It will produce three new CSVs in the same directory.
- Open the outputs to verify they have one header `generated_prompt` and rows.
"""

import csv
import os
from typing import List, Tuple


# IMPORTANT: We use absolute paths so the script works regardless of CWD.
# Adjust BASE_DIR if you move this script to another location.
BASE_DIR = \
    "/Users/sulavshrestha/Documents/[1] Academics/Capstone/[0] Code/Prompt_Generation"


# Define (input_file, output_file) pairs. Outputs are simple and descriptive.
CSV_PAIRS: List[Tuple[str, str]] = [
    ("generated_responses_openai.csv", "openai_generated_prompts.csv"),
    ("generated_responses_claude.csv", "claude_generated_prompts.csv"),
    ("generated_responses_gemini.csv", "gemini_generated_prompts.csv"),
]


def ensure_dir_exists(path: str) -> None:
    """Ensure the directory for the given path exists.

    This avoids errors if the destination directory is missing.
    """

    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def extract_single_column(
    source_csv_path: str,
    destination_csv_path: str,
    column_name: str = "generated_prompt",
) -> None:
    """Extract one column from source CSV and write it to destination CSV.

    - Reads the source CSV using DictReader for header-based access.
    - Verifies the column exists; raises a clear error if not found.
    - Writes a new CSV with a single header (column_name) and rows.
    - Missing row values are written as empty strings to keep row count aligned.
    """

    # Build absolute paths to avoid ambiguity.
    abs_source = os.path.join(BASE_DIR, source_csv_path)
    abs_destination = os.path.join(BASE_DIR, destination_csv_path)

    # Ensure destination directory exists (defensive).
    ensure_dir_exists(abs_destination)

    if not os.path.exists(abs_source):
        raise FileNotFoundError(
            f"Source CSV not found: {abs_source}. Please check the file name."
        )

    # Open the source CSV in universal newline mode, with utf-8 encoding.
    with open(abs_source, "r", encoding="utf-8", newline="") as src_file:
        reader = csv.DictReader(src_file)

        if reader.fieldnames is None:
            raise ValueError(
                f"No header row found in {abs_source}. Expected a header with '{column_name}'."
            )

        # Be strict but helpful: verify the required column exists by exact name.
        if column_name not in reader.fieldnames:
            raise KeyError(
                (
                    f"Column '{column_name}' not found in {abs_source}. "
                    f"Available columns: {reader.fieldnames}"
                )
            )

        # Write the destination CSV with only the desired column and header.
        with open(abs_destination, "w", encoding="utf-8", newline="") as dst_file:
            writer = csv.writer(dst_file)
            writer.writerow([column_name])

            for row in reader:
                value = row.get(column_name, "")
                # Guard against None; always write a string.
                writer.writerow([value if value is not None else ""])


def main() -> None:
    """Run extraction for all configured (input, output) CSV pairs."""

    for input_name, output_name in CSV_PAIRS:
        extract_single_column(
            source_csv_path=input_name,
            destination_csv_path=output_name,
            column_name="generated_prompt",
        )


if __name__ == "__main__":
    # Execute the main function when run as a script.
    main()


