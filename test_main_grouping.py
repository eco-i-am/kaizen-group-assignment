import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import group_participants, find_column_mapping

def test_main_grouping():
    """Test the main grouping function for duplicates"""
    
    print("🧪 TESTING MAIN GROUPING FUNCTION")
    print("=" * 60)
    
    # Read the merged Excel file
    INPUT_FILE = 'merged_users_grouping_preferences_20250718_221747.xlsx'
    
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name='Merged Data')
        print(f"✅ Successfully read input file with {len(df)} records")
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        return
    
    # Find column mapping
    column_mapping = find_column_mapping(df)
    
    # Convert DataFrame to list of dictionaries
    data = df.to_dict('records')
    
    # Test the main grouping function
    print(f"\n🚀 Testing main group assignment...")
    solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)
    
    # Check for duplicates
    all_users = set()
    duplicate_users = set()
    
    def get_value(row, key, default=''):
        if column_mapping and key in column_mapping:
            if isinstance(row, dict):
                return row.get(column_mapping[key], default)
            else:
                return default
        else:
            return default
    
    # Collect all users
    for group in solo_groups:
        for member in group:
            user_id = get_value(member, 'user_id', 'Unknown')
            if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
                user_key = str(user_id).strip()
                if user_key in all_users:
                    duplicate_users.add(user_key)
                else:
                    all_users.add(user_key)
    
    for group_name, members in grouped.items():
        for member in members:
            user_id = get_value(member, 'user_id', 'Unknown')
            if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
                user_key = str(user_id).strip()
                if user_key in all_users:
                    duplicate_users.add(user_key)
                else:
                    all_users.add(user_key)
    
    for group in requested_groups:
        for member in group:
            user_id = get_value(member, 'user_id', 'Unknown')
            if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
                user_key = str(user_id).strip()
                if user_key in all_users:
                    duplicate_users.add(user_key)
                else:
                    all_users.add(user_key)
    
    for user in excluded_users:
        user_id = get_value(user, 'user_id', 'Unknown')
        if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
            user_key = str(user_id).strip()
            if user_key in all_users:
                duplicate_users.add(user_key)
            else:
                all_users.add(user_key)
    
    print(f"\n📊 RESULTS:")
    print(f"Total unique users in output: {len(all_users)}")
    print(f"Duplicate users: {len(duplicate_users)}")
    
    if duplicate_users:
        print(f"\n❌ DUPLICATE USERS FOUND:")
        for user_id in sorted(duplicate_users)[:20]:  # Show first 20
            print(f"  - User ID: {user_id}")
        if len(duplicate_users) > 20:
            print(f"  ... and {len(duplicate_users) - 20} more")
    else:
        print(f"\n✅ NO DUPLICATE USERS FOUND!")
    
    # Group breakdown
    solo_count = sum(len(group) for group in solo_groups)
    regular_count = sum(len(members) for members in grouped.values())
    requested_count = sum(len(group) for group in requested_groups)
    excluded_count = len(excluded_users)
    
    print(f"\n📋 GROUP SUMMARY:")
    print(f"Solo users: {solo_count}")
    print(f"Regular group users: {regular_count}")
    print(f"Requested group users: {requested_count}")
    print(f"Excluded users: {excluded_count}")
    print(f"Total output users: {solo_count + regular_count + requested_count + excluded_count}")

if __name__ == "__main__":
    test_main_grouping() 