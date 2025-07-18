import pandas as pd
from collections import defaultdict
import sys
sys.path.append('.')

# Import the functions from the main script
from group_assignment_to_excel import group_participants, save_to_excel, find_column_mapping

# File paths
INPUT_FILE = 'merged_users_grouping_preferences_20250717_201414.xlsx'
OUTPUT_FILE = 'debug_excel_output.xlsx'

def main():
    print("Debugging Excel output issue...")
    print("="*50)
    
    # Read the merged Excel file
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name='Merged Data')
        print(f"✅ Successfully read input file with {len(df)} records")
    except Exception as e:
        try:
            df = pd.read_csv(INPUT_FILE)
            print(f"✅ Successfully read CSV file with {len(df)} records")
        except Exception as e2:
            print(f"❌ Error reading input file: {e2}")
            return
    
    # Find column mapping
    column_mapping = find_column_mapping(df)
    print(f"\n📋 Column mapping found:")
    for key, value in column_mapping.items():
        if value:
            print(f"  ✅ {key}: {value}")
        else:
            print(f"  ❌ {key}: NOT FOUND")
    
    # Convert DataFrame to list of dictionaries
    data = df.to_dict('records')
    
    print(f"\n🚀 Starting group assignment process...")
    
    # Group participants
    solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)
    
    print(f"\n🔍 Checking specific users in requested groups...")
    
    # Check for the specific missing users
    missing_users = [
        'lilyroseanne.gutierrez@gmail.com',
        'carolineongco0392@yahoo.com.au', 
        'karenpicache@gmail.com'
    ]
    
    for email in missing_users:
        print(f"\nLooking for: {email}")
        found = False
        
        for i, group in enumerate(requested_groups):
            group_emails = []
            for member in group:
                member_email = member.get(column_mapping.get('email'), '')
                if member_email and '@' in member_email:
                    group_emails.append(member_email.lower().strip())
            
            if email.lower().strip() in group_emails:
                print(f"  ✅ Found in requested group {i+1}")
                print(f"  Group members: {group_emails}")
                found = True
                break
        
        if not found:
            print(f"  ❌ NOT FOUND in any requested group")
    
    print(f"\n💾 Saving results to Excel...")
    
    # Save to Excel
    save_to_excel(solo_groups, grouped, OUTPUT_FILE, column_mapping, excluded_users, requested_groups)
    
    print(f"\n📊 Checking Excel output...")
    
    # Read the Excel file back and check for the users
    try:
        excel_df = pd.read_excel(OUTPUT_FILE)
        print(f"✅ Successfully read Excel output with {len(excel_df)} rows")
        
        # Check for the missing users in the Excel output
        for email in missing_users:
            print(f"\nLooking for in Excel: {email}")
            found = False
            
            # Check all name columns (Name 1, Name 2, etc.)
            for i in range(1, 8):  # Check Name 1 through Name 7
                name_col = f'Name {i}'
                if name_col in excel_df.columns:
                    # Look for the email in the data
                    for idx, row in excel_df.iterrows():
                        # We need to find the user by email, but we only have names in the Excel
                        # Let's check if we can find the user by looking at the original data
                        for member in data:
                            member_email = member.get(column_mapping.get('email'), '')
                            member_name = member.get(column_mapping.get('name'), '')
                            if member_email.lower().strip() == email.lower().strip():
                                if member_name == row[name_col]:
                                    print(f"  ✅ Found in row {idx+1}, column {name_col}")
                                    print(f"  Group: {row['Group Name']}")
                                    found = True
                                    break
                        if found:
                            break
                if found:
                    break
            
            if not found:
                print(f"  ❌ NOT FOUND in Excel output")
        
    except Exception as e:
        print(f"❌ Error reading Excel output: {e}")

if __name__ == "__main__":
    main() 