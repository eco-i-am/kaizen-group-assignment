import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import find_column_mapping, group_participants, extract_emails_from_accountability_buddies, normalize_email

def test_without_team_names():
    """Test by temporarily removing team names to see if mutual buddy groups work"""
    
    print("🧪 TESTING WITHOUT TEAM NAMES")
    print("=" * 60)
    
    # Read the new Excel file
    INPUT_FILE = 'merged_users_grouping_preferences_20250719_004359.xlsx'
    
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
    
    # Helper function to get value safely
    def get_value(row, key, default=''):
        if column_mapping and key in column_mapping:
            if isinstance(row, dict):
                return row.get(column_mapping[key], default)
            else:
                return default
        else:
            return default
    
    # Find Morris and Gerard
    morris_user = None
    gerard_user = None
    
    for row in data:
        user_id = get_value(row, 'user_id', '')
        if str(user_id).strip() == '2360':
            morris_user = row
        elif str(user_id).strip() == '2123':
            gerard_user = row
    
    if not morris_user or not gerard_user:
        print(f"❌ Could not find Morris or Gerard")
        return
    
    # Create a copy of the data with team names removed
    test_data = []
    for row in data:
        # Create a copy of the row
        new_row = row.copy()
        
        # Remove team name for testing
        if column_mapping and 'temporary_team_name' in column_mapping:
            new_row[column_mapping['temporary_team_name']] = None
        
        test_data.append(new_row)
    
    print(f"\n📋 TEST DATA (with team names removed):")
    print(f"  Morris: {get_value(morris_user, 'name', '')} (ID: {get_value(morris_user, 'user_id', '')})")
    print(f"    Has Accountability Buddies: {get_value(morris_user, 'has_accountability_buddies', '')}")
    print(f"    Accountability Buddies: {get_value(morris_user, 'accountability_buddies', '')}")
    print(f"    Team Name: {get_value(morris_user, 'temporary_team_name', '')} (will be removed)")
    
    print(f"  Gerard: {get_value(gerard_user, 'name', '')} (ID: {get_value(gerard_user, 'user_id', '')})")
    print(f"    Has Accountability Buddies: {get_value(gerard_user, 'has_accountability_buddies', '')}")
    print(f"    Accountability Buddies: {get_value(gerard_user, 'accountability_buddies', '')}")
    print(f"    Team Name: {get_value(gerard_user, 'temporary_team_name', '')} (will be removed)")
    
    # Run grouping on the modified data
    print(f"\n🚀 RUNNING GROUPING ON MODIFIED DATA...")
    solo_groups, grouped, excluded_users, requested_groups = group_participants(test_data, column_mapping)
    
    print(f"\n📊 RESULTS:")
    print(f"  Solo groups: {len(solo_groups)}")
    print(f"  Regular groups: {len(grouped)}")
    print(f"  Requested groups: {len(requested_groups)}")
    print(f"  Excluded users: {len(excluded_users)}")
    
    # Check where Morris and Gerard ended up
    print(f"\n🔍 WHERE MORRIS AND GERARD ENDED UP:")
    
    # Check solo groups
    for i, group in enumerate(solo_groups):
        for member in group:
            user_id = get_value(member, 'user_id', '')
            name = get_value(member, 'name', '')
            if str(user_id).strip() in ['2123', '2360']:
                print(f"  {name} (ID: {user_id}) found in Solo Group {i+1}")
    
    # Check requested groups
    for i, group in enumerate(requested_groups):
        print(f"  Requested Group {i+1} ({len(group)} members):")
        for j, member in enumerate(group):
            user_id = get_value(member, 'user_id', '')
            name = get_value(member, 'name', '')
            email = get_value(member, 'email', '')
            print(f"    {j+1}. {user_id} {name} ({email})")
    
    # Check regular groups
    for group_name, members in grouped.items():
        for member in members:
            user_id = get_value(member, 'user_id', '')
            name = get_value(member, 'name', '')
            if str(user_id).strip() in ['2123', '2360']:
                print(f"  {name} (ID: {user_id}) found in Regular Group: {group_name}")
    
    # Check excluded users
    for user in excluded_users:
        user_id = get_value(user, 'user_id', '')
        name = get_value(user, 'name', '')
        if str(user_id).strip() in ['2123', '2360']:
            print(f"  {name} (ID: {user_id}) found in excluded users")

if __name__ == "__main__":
    test_without_team_names() 