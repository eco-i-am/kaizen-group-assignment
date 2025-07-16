import pandas as pd
from group_assignment_to_excel import find_column_mapping

def debug_philippines_data(file_path):
    """Debug the Philippines resident data to understand why count is 0"""
    
    try:
        # Read the Excel file
        data = pd.read_excel(file_path, sheet_name='Merged Data')
        print(f"✅ Successfully read file with {len(data)} records")
        print(f"Available columns: {list(data.columns)}")
        print()
        
        # Find column mapping
        column_mapping = find_column_mapping(data)
        print("Column mapping:")
        for key, value in column_mapping.items():
            if value:
                print(f"  {key}: {value}")
        print()
        
        # Check the lingInPhilippineExperience column
        ph_col = column_mapping.get('residing_ph')
        if ph_col:
            print(f"📊 Philippines column '{ph_col}' analysis:")
            print(f"  Column type: {data[ph_col].dtype}")
            print(f"  Unique values: {data[ph_col].unique()}")
            print(f"  Value counts:")
            value_counts = data[ph_col].value_counts()
            for value, count in value_counts.items():
                print(f"    '{value}' (type: {type(value)}): {count}")
            
            # Test different conditions
            print(f"\n🔍 Testing different conditions:")
            print(f"  == 1: {len(data[data[ph_col] == 1])}")
            print(f"  == '1': {len(data[data[ph_col] == '1'])}")
            print(f"  == True: {len(data[data[ph_col] == True])}")
            print(f"  == 'True': {len(data[data[ph_col] == 'True'])}")
            print(f"  == 'yes': {len(data[data[ph_col] == 'yes'])}")
            print(f"  == 'Yes': {len(data[data[ph_col] == 'Yes'])}")
            print(f"  == 'philippines': {len(data[data[ph_col].astype(str).str.lower() == 'philippines'])}")
            print(f"  == 'ph': {len(data[data[ph_col].astype(str).str.lower() == 'ph'])}")
            
            # Check for any non-null values
            non_null = data[ph_col].notna()
            print(f"  Non-null values: {non_null.sum()}")
            
            # Show sample values
            print(f"\n📋 Sample values (first 10):")
            for i, value in enumerate(data[ph_col].head(10)):
                print(f"  Row {i+1}: '{value}' (type: {type(value)})")
                
        else:
            print("❌ No Philippines column found in mapping")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Try different possible file names
    possible_files = [
        "merged_users_grouping_preferences.xlsx",
        "sample_merged_data.xlsx", 
        "test_merged_data.xlsx",
        "grouped_participants_merged_20250716_215553.xlsx"
    ]
    
    for file_path in possible_files:
        try:
            print(f"🔍 Trying file: {file_path}")
            debug_philippines_data(file_path)
            break
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            continue
        except Exception as e:
            print(f"❌ Error with {file_path}: {e}")
            continue 