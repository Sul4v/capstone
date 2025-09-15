#!/usr/bin/env python3
"""
CSV Merger Tool

This script merges multiple CSV files that share common columns but have unique columns.
Each CSV file should have the same base columns plus one unique column.

Common columns expected:
- base_question_id
- category  
- base_question
- assigned_persona
- prompt_type
- generated_prompt

Each file will have one additional unique column.
The script will merge all files based on base_question_id to create a comprehensive dataset.
"""

import pandas as pd
import os
import sys
from pathlib import Path


def get_csv_files():
    """
    Prompt user to input CSV file paths and validate they exist.
    
    Returns:
        list: List of valid CSV file paths
    """
    csv_files = []
    print("CSV File Merger Tool")
    print("=" * 50)
    print("Please enter the paths to your CSV files.")
    print("Press Enter after each file path.")
    print("Type 'done' when you've entered all files.\n")
    
    while True:
        file_path = input(f"Enter CSV file path #{len(csv_files) + 1} (or 'done' to finish): ").strip()
        
        if file_path.lower() == 'done':
            if len(csv_files) < 2:
                print("Error: You need at least 2 CSV files to merge. Please add more files.")
                continue
            break
            
        if not file_path:
            continue
            
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist. Please check the path and try again.")
            continue
            
        # Check if it's a CSV file
        if not file_path.lower().endswith('.csv'):
            print(f"Error: '{file_path}' is not a CSV file. Please provide a .csv file.")
            continue
            
        csv_files.append(file_path)
        print(f"✓ Added: {file_path}")
    
    return csv_files


def analyze_csv_structure(file_path):
    """
    Analyze the structure of a CSV file to identify columns.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        tuple: (dataframe, common_columns, unique_columns)
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Define expected common columns
        expected_common_cols = [
            'base_question_id', 'category', 'base_question', 
            'assigned_persona', 'prompt_type', 'generated_prompt'
        ]
        
        # Find which expected columns are present
        present_common_cols = [col for col in expected_common_cols if col in df.columns]
        
        # Find unique columns (columns not in the expected common set)
        unique_cols = [col for col in df.columns if col not in expected_common_cols]
        
        return df, present_common_cols, unique_cols
        
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return None, [], []


def merge_csv_files(csv_files, output_path):
    """
    Merge multiple CSV files with common and unique columns.
    
    Args:
        csv_files (list): List of CSV file paths
        output_path (str): Path for the output merged CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\nAnalyzing {len(csv_files)} CSV files...")
    
    # Store dataframes and their column info
    file_data = []
    all_common_cols = set()
    all_unique_cols = []
    
    # Analyze each file
    for i, file_path in enumerate(csv_files):
        print(f"Analyzing file {i+1}: {Path(file_path).name}")
        
        df, common_cols, unique_cols = analyze_csv_structure(file_path)
        
        if df is None:
            print(f"Skipping {file_path} due to errors.")
            continue
            
        print(f"  - Rows: {len(df)}")
        print(f"  - Common columns found: {len(common_cols)}")
        print(f"  - Unique columns: {unique_cols}")
        
        file_data.append({
            'path': file_path,
            'df': df,
            'common_cols': common_cols,
            'unique_cols': unique_cols
        })
        
        all_common_cols.update(common_cols)
        all_unique_cols.extend(unique_cols)
    
    if not file_data:
        print("Error: No valid CSV files to process.")
        return False
    
    print(f"\nMerging strategy:")
    print(f"  - Total common columns across all files: {len(all_common_cols)}")
    print(f"  - Total unique columns: {len(all_unique_cols)}")
    print(f"  - Common columns: {sorted(all_common_cols)}")
    print(f"  - Unique columns: {all_unique_cols}")
    
    # Start with the first file as base
    base_df = file_data[0]['df'].copy()
    merge_key = 'base_question_id'  # Primary key for merging
    
    # Check if merge key exists
    if merge_key not in base_df.columns:
        print(f"Warning: '{merge_key}' not found. Using row index for merging.")
        merge_key = None
    
    # Merge each subsequent file
    for i in range(1, len(file_data)):
        current_file = file_data[i]
        current_df = current_file['df']
        
        print(f"Merging file {i+1}: {Path(current_file['path']).name}")
        
        if merge_key and merge_key in current_df.columns:
            # Merge on base_question_id
            # Only merge the unique columns to avoid duplicating common columns
            unique_cols_to_merge = current_file['unique_cols']
            if unique_cols_to_merge:
                merge_cols = [merge_key] + unique_cols_to_merge
                temp_df = current_df[merge_cols]
                base_df = base_df.merge(temp_df, on=merge_key, how='left')
            else:
                print(f"  Warning: No unique columns found in {current_file['path']}")
        else:
            # Merge by index if no common key
            unique_cols_to_merge = current_file['unique_cols']
            if unique_cols_to_merge:
                for col in unique_cols_to_merge:
                    if len(current_df) == len(base_df):
                        base_df[col] = current_df[col].values
                    else:
                        print(f"  Warning: Row count mismatch for {current_file['path']}")
    
    # Save the merged dataframe
    try:
        base_df.to_csv(output_path, index=False)
        print(f"\n✓ Successfully merged {len(file_data)} files!")
        print(f"✓ Output saved to: {output_path}")
        print(f"✓ Final dataset shape: {base_df.shape[0]} rows × {base_df.shape[1]} columns")
        print(f"✓ Final columns: {list(base_df.columns)}")
        return True
        
    except Exception as e:
        print(f"Error saving merged file: {str(e)}")
        return False


def main():
    """
    Main function to orchestrate the CSV merging process.
    """
    try:
        # Get CSV files from user
        csv_files = get_csv_files()
        
        if not csv_files:
            print("No CSV files provided. Exiting.")
            return
        
        # Get output file path
        print(f"\nYou've selected {len(csv_files)} CSV files to merge:")
        for i, file_path in enumerate(csv_files, 1):
            print(f"  {i}. {Path(file_path).name}")
        
        # Suggest output filename
        default_output = "/Users/sulavshrestha/Documents/[1] Academics/Capstone/[0] Code/Prompt_Generation/merged_csv_output.csv"
        output_path = input(f"\nEnter output file path (default: {default_output}): ").strip()
        
        if not output_path:
            output_path = default_output
        
        # Ensure output has .csv extension
        if not output_path.lower().endswith('.csv'):
            output_path += '.csv'
        
        # Perform the merge
        success = merge_csv_files(csv_files, output_path)
        
        if success:
            print(f"\n🎉 Merge completed successfully!")
            print(f"📁 Merged file location: {output_path}")
        else:
            print(f"\n❌ Merge failed. Please check the error messages above.")
            
    except KeyboardInterrupt:
        print(f"\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")


if __name__ == "__main__":
    main()
