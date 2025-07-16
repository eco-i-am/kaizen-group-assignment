#!/usr/bin/env python3
"""
Test script for using merged user grouping preference data with group assignment.
This script shows how to:
1. Generate sample merged data
2. Use the updated group assignment script
3. Handle different column name variations
"""

import pandas as pd
import numpy as np
from datetime import datetime
from group_assignment_to_excel import find_column_mapping, group_participants, save_to_excel

def create_sample_merged_data():
    """Create sample merged data to test the group assignment"""
    
    # Sample data structure that might come from the merged Excel file
    sample_data = {
        'user_id': range(1, 51),
        'full_name': [f'User {i}' for i in range(1, 51)],
        'gender_identity': np.random.choice(['Male', 'Female', 'LGBTQ+'], 50),
        'biological_sex': np.random.choice(['male', 'female'], 50),
        'residing_in_philippines': np.random.choice(['1', '0'], 50),
        'grouping_preference': np.random.choice(['same_gender', 'no_preference'], 50),
        'country': np.random.choice(['Philippines', 'United States', 'Canada', 'Japan', 'Australia'], 50),
        'state_province': np.random.choice(['Metro Manila', 'California', 'Ontario', 'Tokyo', 'New South Wales'], 50),
        'city': np.random.choice(['Manila', 'Los Angeles', 'Toronto', 'Tokyo', 'Sydney'], 50),
        'region': np.random.choice(['NCR', 'CA', 'ON', 'JP', 'NSW'], 50),
        'prefer_solo': np.random.choice(['1', '0'], 50, p=[0.1, 0.9])  # 10% prefer solo
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Save as Excel with multiple sheets (like the merged file)
    output_file = 'sample_merged_data.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main merged data
        df.to_excel(writer, sheet_name='Merged Data', index=False)
        
        # Individual datasets (simulated)
        users_df = df[['user_id', 'full_name', 'gender_identity', 'biological_sex', 'country']].copy()
        grouping_df = df[['user_id', 'residing_in_philippines', 'grouping_preference', 'prefer_solo']].copy()
        
        users_df.to_excel(writer, sheet_name='Users Data', index=False)
        grouping_df.to_excel(writer, sheet_name='Grouping Preferences', index=False)
        
        # Summary sheet
        summary_data = {
            'Metric': ['Total Records', 'Users Data', 'Grouping Preferences', 'Merged Records'],
            'Count': [len(df), len(users_df), len(grouping_df), len(df)]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"Created sample merged data file: {output_file}")
    print(f"Sample data preview:")
    print(df.head())
    print(f"\nColumns: {list(df.columns)}")
    
    return output_file

def test_group_assignment_with_merged_data(input_file):
    """Test the group assignment with merged data"""
    
    print(f"\n{'='*60}")
    print("TESTING GROUP ASSIGNMENT WITH MERGED DATA")
    print(f"{'='*60}")
    
    # Read the merged Excel file
    try:
        df = pd.read_excel(input_file, sheet_name='Merged Data')
        print(f"✅ Successfully read merged data with {len(df)} records")
        print(f"📋 Available columns: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return
    
    # Find column mapping
    column_mapping = find_column_mapping(df)
    print(f"\n🔍 Column mapping found:")
    for key, value in column_mapping.items():
        print(f"  {key}: {value}")
    
    # Check for missing columns
    missing_columns = [key for key, value in column_mapping.items() if value is None]
    if missing_columns:
        print(f"\n⚠️  Warning: Missing columns: {missing_columns}")
    
    # Convert DataFrame to list of dictionaries
    data = df.to_dict('records')
    
    # Group participants
    print(f"\n👥 Starting group assignment...")
    solo_groups, grouped = group_participants(data, column_mapping)
    
    print(f"\n📊 Grouping Results:")
    print(f"  Solo groups: {len(solo_groups)}")
    print(f"  Regular groups: {len(grouped)}")
    
    # Show some group examples
    print(f"\n📋 Sample groups:")
    for i, (group_name, members) in enumerate(list(grouped.items())[:3]):
        print(f"  {group_name}: {len(members)} members")
        for member in members[:2]:  # Show first 2 members
            user_id = member.get(column_mapping.get('user_id'), 'Unknown')
            name = member.get(column_mapping.get('name'), 'Unknown')
            print(f"    - {user_id}: {name}")
    
    # Save to Excel
    output_file = f'grouped_participants_merged_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    print(f"\n💾 Saving results to: {output_file}")
    save_to_excel(solo_groups, grouped, output_file, column_mapping)
    
    print(f"\n✅ Group assignment completed successfully!")
    return output_file

def main():
    """Main function to run the test"""
    
    print("🧪 TESTING MERGED USER GROUPING PREFERENCE INTEGRATION")
    print("=" * 60)
    
    # Step 1: Create sample merged data
    print("\n1️⃣ Creating sample merged data...")
    sample_file = create_sample_merged_data()
    
    # Step 2: Test group assignment
    print("\n2️⃣ Testing group assignment...")
    result_file = test_group_assignment_with_merged_data(sample_file)
    
    print(f"\n🎉 Test completed!")
    print(f"📁 Sample data: {sample_file}")
    print(f"📁 Results: {result_file}")
    
    print(f"\n📝 To use with your actual merged data:")
    print(f"1. Update INPUT_FILE in group_assignment_to_excel.py to point to your merged Excel file")
    print(f"2. Run: python group_assignment_to_excel.py")
    print(f"3. The script will automatically detect column names and create groups")

if __name__ == "__main__":
    main() 