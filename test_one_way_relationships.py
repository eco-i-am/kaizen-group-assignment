import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import find_column_mapping, group_participants, extract_emails_from_accountability_buddies, normalize_email

def test_one_way_relationships():
    """Test that one-way accountability buddy relationships work correctly"""
    
    print("🧪 TESTING ONE-WAY ACCOUNTABILITY BUDDY RELATIONSHIPS")
    print("=" * 70)
    
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
    
    # Find the key users for testing one-way relationships
    morris_user = None
    gerard_user = None
    john_user = None
    patricia_user = None
    
    for row in data:
        user_id = get_value(row, 'user_id', '')
        if str(user_id).strip() == '2360':
            morris_user = row
        elif str(user_id).strip() == '2123':
            gerard_user = row
        elif str(user_id).strip() == '2817':
            john_user = row
        elif str(user_id).strip() == '2539':
            patricia_user = row
    
    if not all([morris_user, gerard_user, john_user, patricia_user]):
        print(f"❌ Could not find all four test users")
        return
    
    print(f"\n📋 TEST CASE: ONE-WAY RELATIONSHIPS")
    print(f"  Morris (ID 2360): {get_value(morris_user, 'name', '')}")
    print(f"    References: {get_value(morris_user, 'accountability_buddies', '')}")
    print(f"    Has Accountability Buddies: {get_value(morris_user, 'has_accountability_buddies', '')}")
    
    print(f"  Gerard (ID 2123): {get_value(gerard_user, 'name', '')}")
    print(f"    References: {get_value(gerard_user, 'accountability_buddies', '')}")
    print(f"    Has Accountability Buddies: {get_value(gerard_user, 'has_accountability_buddies', '')}")
    
    print(f"  John (ID 2817): {get_value(john_user, 'name', '')}")
    print(f"    References: {get_value(john_user, 'accountability_buddies', '')}")
    print(f"    Has Accountability Buddies: {get_value(john_user, 'has_accountability_buddies', '')}")
    
    print(f"  Patricia (ID 2539): {get_value(patricia_user, 'name', '')}")
    print(f"    References: {get_value(patricia_user, 'accountability_buddies', '')}")
    print(f"    Has Accountability Buddies: {get_value(patricia_user, 'has_accountability_buddies', '')}")
    
    # Create email mapping
    email_mapping = {}
    
    # Extract emails
    morris_email = normalize_email(get_value(morris_user, 'email', ''), email_mapping)
    gerard_email = normalize_email(get_value(gerard_user, 'email', ''), email_mapping)
    john_email = normalize_email(get_value(john_user, 'email', ''), email_mapping)
    patricia_email = normalize_email(get_value(patricia_user, 'email', ''), email_mapping)
    
    print(f"\n📧 EMAILS:")
    print(f"  Morris: {morris_email}")
    print(f"  Gerard: {gerard_email}")
    print(f"  John: {john_email}")
    print(f"  Patricia: {patricia_email}")
    
    # Check relationships
    print(f"\n🔍 RELATIONSHIP ANALYSIS:")
    
    # Check Morris's references
    morris_buddies = get_value(morris_user, 'accountability_buddies', '')
    morris_extracted = extract_emails_from_accountability_buddies(morris_buddies, email_mapping)
    print(f"  Morris references: {morris_extracted}")
    
    # Check John's references
    john_buddies = get_value(john_user, 'accountability_buddies', '')
    john_extracted = extract_emails_from_accountability_buddies(john_buddies, email_mapping)
    print(f"  John references: {john_extracted}")
    
    # Check Gerard's references
    gerard_buddies = get_value(gerard_user, 'accountability_buddies', '')
    gerard_extracted = extract_emails_from_accountability_buddies(gerard_buddies, email_mapping)
    print(f"  Gerard references: {gerard_extracted}")
    
    # Check Patricia's references
    patricia_buddies = get_value(patricia_user, 'accountability_buddies', '')
    patricia_extracted = extract_emails_from_accountability_buddies(patricia_buddies, email_mapping)
    print(f"  Patricia references: {patricia_extracted}")
    
    # Verify one-way relationships
    print(f"\n🤝 ONE-WAY RELATIONSHIP VERIFICATION:")
    
    # Morris -> Gerard (one-way)
    if gerard_email in morris_extracted:
        print(f"  ✅ Morris -> Gerard (one-way)")
    else:
        print(f"  ❌ Morris -X-> Gerard")
    
    # John -> Morris (one-way)
    if morris_email in john_extracted:
        print(f"  ✅ John -> Morris (one-way)")
    else:
        print(f"  ❌ John -X-> Morris")
    
    # John -> Patricia (one-way)
    if patricia_email in john_extracted:
        print(f"  ✅ John -> Patricia (one-way)")
    else:
        print(f"  ❌ John -X-> Patricia")
    
    # Gerard -> Morris (should be false - one-way)
    if morris_email in gerard_extracted:
        print(f"  ✅ Gerard -> Morris")
    else:
        print(f"  ❌ Gerard -X-> Morris (correct - one-way relationship)")
    
    # Patricia -> John (should be false - one-way)
    if john_email in patricia_extracted:
        print(f"  ✅ Patricia -> John")
    else:
        print(f"  ❌ Patricia -X-> John (correct - one-way relationship)")
    
    # Test the grouping logic
    print(f"\n🚀 TESTING GROUPING LOGIC:")
    
    # Create test data with just these four users
    test_data = [morris_user, gerard_user, john_user, patricia_user]
    
    # Run grouping
    solo_groups, grouped, excluded_users, requested_groups = group_participants(test_data, column_mapping)
    
    print(f"\n📊 RESULTS:")
    print(f"  Solo groups: {len(solo_groups)}")
    print(f"  Regular groups: {len(grouped)}")
    print(f"  Requested groups: {len(requested_groups)}")
    print(f"  Excluded users: {len(excluded_users)}")
    
    # Check where users ended up
    print(f"\n🔍 WHERE USERS ENDED UP:")
    
    # Check requested groups
    for i, group in enumerate(requested_groups):
        print(f"  Requested Group {i+1} ({len(group)} members):")
        for j, member in enumerate(group):
            user_id = get_value(member, 'user_id', '')
            name = get_value(member, 'name', '')
            email = get_value(member, 'email', '')
            print(f"    {j+1}. {user_id} {name} ({email})")
    
    # Check if all four users are in the same group
    all_in_same_group = False
    for i, group in enumerate(requested_groups):
        user_ids = [get_value(member, 'user_id', '') for member in group]
        if all(str(uid) in user_ids for uid in ['2360', '2123', '2817', '2539']):
            all_in_same_group = True
            print(f"\n🎉 SUCCESS! All four users are in Requested Group {i+1}")
            break
    
    if not all_in_same_group:
        print(f"\n❌ FAILURE! Not all four users are in the same group")
    
    # Test with full dataset
    print(f"\n🚀 TESTING WITH FULL DATASET:")
    solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)
    
    # Find where the four users ended up in the full dataset
    morris_group = None
    gerard_group = None
    john_group = None
    patricia_group = None
    
    for i, group in enumerate(requested_groups):
        user_ids = [get_value(member, 'user_id', '') for member in group]
        if '2360' in user_ids:
            morris_group = i + 1
        if '2123' in user_ids:
            gerard_group = i + 1
        if '2817' in user_ids:
            john_group = i + 1
        if '2539' in user_ids:
            patricia_group = i + 1
    
    print(f"\n📊 FULL DATASET RESULTS:")
    print(f"  Morris: Requested Group {morris_group}")
    print(f"  Gerard: Requested Group {gerard_group}")
    print(f"  John: Requested Group {john_group}")
    print(f"  Patricia: Requested Group {patricia_group}")
    
    if morris_group == gerard_group == john_group == patricia_group:
        print(f"\n🎉 PERFECT! All four users are in the same group: Requested Group {morris_group}")
        print(f"✅ ONE-WAY RELATIONSHIPS WORKING CORRECTLY!")
    else:
        print(f"\n❌ FAILURE! Users are in different groups")
        print(f"❌ ONE-WAY RELATIONSHIPS NOT WORKING!")

if __name__ == "__main__":
    test_one_way_relationships() 