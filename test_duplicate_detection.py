#!/usr/bin/env python3

import pandas as pd
import sys
import os

# Add the current directory to the path so we can import the grouping module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from group_assignment_to_excel import group_participants, find_column_mapping

def test_with_participants_csv():
    """Test the grouping logic with participants.csv to check for duplicate users"""
    print("=== Testing with participants.csv ===")
    
    # Read the participants.csv file
    try:
        df = pd.read_csv('participants.csv')
        print(f"Successfully read participants.csv with {len(df)} records")
        print(f"Available columns: {list(df.columns)}")
    except Exception as e:
        print(f"Error reading participants.csv: {e}")
        return
    
    # Find column mapping
    column_mapping = find_column_mapping(df)
    print(f"Column mapping found: {column_mapping}")
    
    # Convert DataFrame to list of dictionaries
    data = df.to_dict('records')
    print(f"Converted to {len(data)} records")
    
    # Run the grouping logic
    original_data_count = len(df)
    solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping, original_data_count)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_with_participants_csv() 