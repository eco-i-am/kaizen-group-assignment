#!/usr/bin/env python3
"""
Simple wrapper script to run group assignment with merged user grouping preference data.
This script allows you to easily specify your input file and run the group assignment.
"""

import sys
import os
import argparse
from group_assignment_to_excel import main as run_group_assignment

def main():
    parser = argparse.ArgumentParser(description='Run group assignment with merged user data')
    parser.add_argument('input_file', nargs='?', default='merged_users_grouping_preferences.xlsx',
                       help='Path to the merged Excel file (default: merged_users_grouping_preferences.xlsx)')
    parser.add_argument('--output', '-o', default='grouped_participants.xlsx',
                       help='Output file name (default: grouped_participants.xlsx)')
    parser.add_argument('--test', '-t', action='store_true',
                       help='Run with sample data for testing')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Running test with sample data...")
        from test_merged_grouping import main as run_test
        run_test()
        return
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' not found!")
        print("\nAvailable files:")
        for file in os.listdir('.'):
            if file.endswith('.xlsx') or file.endswith('.csv'):
                print(f"  - {file}")
        print(f"\nUsage examples:")
        print(f"  python run_group_assignment.py your_file.xlsx")
        print(f"  python run_group_assignment.py --test")
        return
    
    print(f"📁 Using input file: {args.input_file}")
    print(f"📁 Output will be saved to: {args.output}")
    
    # Temporarily update the input file in the module
    import group_assignment_to_excel
    original_input = group_assignment_to_excel.INPUT_FILE
    original_output = group_assignment_to_excel.OUTPUT_FILE
    
    try:
        group_assignment_to_excel.INPUT_FILE = args.input_file
        group_assignment_to_excel.OUTPUT_FILE = args.output
        
        print(f"\n🚀 Starting group assignment...")
        run_group_assignment()
        
        print(f"\n✅ Group assignment completed!")
        print(f"📁 Results saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error during group assignment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Restore original values
        group_assignment_to_excel.INPUT_FILE = original_input
        group_assignment_to_excel.OUTPUT_FILE = original_output

if __name__ == "__main__":
    main() 