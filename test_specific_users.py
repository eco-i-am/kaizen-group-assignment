import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import find_column_mapping, group_participants

def test_specific_users():
    """Test to find exactly where the three users end up in the full dataset"""
    
    print("🔍 TESTING SPECIFIC USERS IN FULL DATASET")
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
    
    # Run grouping
    print(f"\n🚀 RUNNING GROUPING:")
    solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)
    
    # Find our specific users
    user_1710_found = False
    user_2013_found = False
    user_1754_found = False
    
    print(f"\n🔍 SEARCHING FOR USERS IN ALL GROUP TYPES:")
    
    # Check solo groups
    print(f"\n📋 SOLO GROUPS:")
    for i, solo_group in enumerate(solo_groups):
        for member in solo_group:
            user_id = get_value(member, 'user_id', '')
            if str(user_id).strip() in ['1710', '2013', '1754']:
                name = get_value(member, 'name', '')
                email = get_value(member, 'email', '')
                print(f"  Solo Group {i+1}: {user_id} {name} ({email})")
                if str(user_id).strip() == '1710':
                    user_1710_found = True
                elif str(user_id).strip() == '2013':
                    user_2013_found = True
                elif str(user_id).strip() == '1754':
                    user_1754_found = True
    
    # Check regular groups
    print(f"\n📋 REGULAR GROUPS:")
    for group_name, members in grouped.items():
        for member in members:
            user_id = get_value(member, 'user_id', '')
            if str(user_id).strip() in ['1710', '2013', '1754']:
                name = get_value(member, 'name', '')
                email = get_value(member, 'email', '')
                print(f"  {group_name}: {user_id} {name} ({email})")
                if str(user_id).strip() == '1710':
                    user_1710_found = True
                elif str(user_id).strip() == '2013':
                    user_2013_found = True
                elif str(user_id).strip() == '1754':
                    user_1754_found = True
    
    # Check requested groups
    print(f"\n📋 REQUESTED GROUPS:")
    for i, group in enumerate(requested_groups):
        for member in group:
            user_id = get_value(member, 'user_id', '')
            if str(user_id).strip() in ['1710', '2013', '1754']:
                name = get_value(member, 'name', '')
                email = get_value(member, 'email', '')
                team_name = get_value(member, 'temporary_team_name', '')
                has_buddies = get_value(member, 'has_accountability_buddies', '')
                buddies = get_value(member, 'accountability_buddies', '')
                print(f"  Requested Group {i+1}: {user_id} {name} ({email})")
                print(f"    Team: {team_name}")
                print(f"    Has Buddies: {has_buddies}")
                print(f"    Buddies: {buddies}")
                if str(user_id).strip() == '1710':
                    user_1710_found = True
                elif str(user_id).strip() == '2013':
                    user_2013_found = True
                elif str(user_id).strip() == '1754':
                    user_1754_found = True
    
    # Check excluded users
    print(f"\n📋 EXCLUDED USERS:")
    for member in excluded_users:
        user_id = get_value(member, 'user_id', '')
        if str(user_id).strip() in ['1710', '2013', '1754']:
            name = get_value(member, 'name', '')
            email = get_value(member, 'email', '')
            print(f"  Excluded: {user_id} {name} ({email})")
            if str(user_id).strip() == '1710':
                user_1710_found = True
            elif str(user_id).strip() == '2013':
                user_2013_found = True
            elif str(user_id).strip() == '1754':
                user_1754_found = True
    
    print(f"\n🔍 SUMMARY:")
    if not user_1710_found:
        print("❌ User 1710 (Mark Lester) not found in any group")
    if not user_2013_found:
        print("❌ User 2013 (Mark Anthony) not found in any group")
    if not user_1754_found:
        print("❌ User 1754 (Al Baljon) not found in any group")
    
    # Check if they're all in the same requested group
    print(f"\n🔍 CHECKING IF ALL USERS ARE IN THE SAME REQUESTED GROUP:")
    
    # Find which requested group contains each user
    user_1710_group = None
    user_2013_group = None
    user_1754_group = None
    
    for i, group in enumerate(requested_groups):
        user_ids = [get_value(member, 'user_id', '') for member in group]
        if '1710' in user_ids:
            user_1710_group = i + 1
        if '2013' in user_ids:
            user_2013_group = i + 1
        if '1754' in user_ids:
            user_1754_group = i + 1
    
    print(f"  User 1710: Requested Group {user_1710_group}")
    print(f"  User 2013: Requested Group {user_2013_group}")
    print(f"  User 1754: Requested Group {user_1754_group}")
    
    if user_1710_group == user_2013_group == user_1754_group and user_1710_group is not None:
        print(f"\n🎉 SUCCESS! All three users are in the same Requested Group: {user_1710_group}")
        print(f"✅ GROUPS ARE PROPERLY COMBINED!")
    else:
        print(f"\n❌ FAILURE! Users are in different groups")
        print(f"❌ GROUPS ARE NOT COMBINED!")

if __name__ == "__main__":
    test_specific_users() 