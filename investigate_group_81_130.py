import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import find_column_mapping, group_participants, extract_emails_from_accountability_buddies, normalize_email

def investigate_group_81_130():
    """Investigate why Requested Group 81 and 130 should be combined"""
    
    print("🔍 INVESTIGATING GROUP 81 AND 130 COMBINATION")
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
    
    # Find the users from the images
    user_1710 = None  # Mark Leste Mandaluyo
    user_2013 = None  # Mark Anth Mandaluyo  
    user_1754 = None  # Al Baljon Mandaluyo
    missing_user = None  # alwhilanbaljon@gmail.com
    
    for row in data:
        user_id = get_value(row, 'user_id', '')
        if str(user_id).strip() == '1710':
            user_1710 = row
        elif str(user_id).strip() == '2013':
            user_2013 = row
        elif str(user_id).strip() == '1754':
            user_1754 = row
    
    # Also find the missing user by email
    email_mapping = {}
    for row in data:
        email = normalize_email(get_value(row, 'email', ''), email_mapping)
        if email == 'alwhilanbaljon@gmail.com':
            missing_user = row
            break
    
    print(f"\n📋 USER DETAILS:")
    
    if user_1710:
        print(f"  User 1710: {get_value(user_1710, 'name', '')}")
        print(f"    Email: {get_value(user_1710, 'email', '')}")
        print(f"    Team: {get_value(user_1710, 'temporary_team_name', '')}")
        print(f"    Has Accountability Buddies: {get_value(user_1710, 'has_accountability_buddies', '')}")
        print(f"    Accountability Buddies: {get_value(user_1710, 'accountability_buddies', '')}")
    
    if user_2013:
        print(f"  User 2013: {get_value(user_2013, 'name', '')}")
        print(f"    Email: {get_value(user_2013, 'email', '')}")
        print(f"    Team: {get_value(user_2013, 'temporary_team_name', '')}")
        print(f"    Has Accountability Buddies: {get_value(user_2013, 'has_accountability_buddies', '')}")
        print(f"    Accountability Buddies: {get_value(user_2013, 'accountability_buddies', '')}")
    
    if user_1754:
        print(f"  User 1754: {get_value(user_1754, 'name', '')}")
        print(f"    Email: {get_value(user_1754, 'email', '')}")
        print(f"    Team: {get_value(user_1754, 'temporary_team_name', '')}")
        print(f"    Has Accountability Buddies: {get_value(user_1754, 'has_accountability_buddies', '')}")
        print(f"    Accountability Buddies: {get_value(user_1754, 'accountability_buddies', '')}")
    
    if missing_user:
        print(f"  Missing User (alwhilanbaljon@gmail.com): {get_value(missing_user, 'name', '')}")
        print(f"    User ID: {get_value(missing_user, 'user_id', '')}")
        print(f"    Team: {get_value(missing_user, 'temporary_team_name', '')}")
        print(f"    Has Accountability Buddies: {get_value(missing_user, 'has_accountability_buddies', '')}")
        print(f"    Accountability Buddies: {get_value(missing_user, 'accountability_buddies', '')}")
    else:
        print(f"  ❌ Missing user with email alwhilanbaljon@gmail.com not found in data")
    
    # Extract emails and check relationships
    print(f"\n🔍 RELATIONSHIP ANALYSIS:")
    
    if user_1710:
        email_1710 = normalize_email(get_value(user_1710, 'email', ''), email_mapping)
        buddies_1710 = get_value(user_1710, 'accountability_buddies', '')
        extracted_1710 = extract_emails_from_accountability_buddies(buddies_1710, email_mapping)
        print(f"  User 1710 ({email_1710}) references: {extracted_1710}")
    
    if user_2013:
        email_2013 = normalize_email(get_value(user_2013, 'email', ''), email_mapping)
        buddies_2013 = get_value(user_2013, 'accountability_buddies', '')
        extracted_2013 = extract_emails_from_accountability_buddies(buddies_2013, email_mapping)
        print(f"  User 2013 ({email_2013}) references: {extracted_2013}")
    
    if user_1754:
        email_1754 = normalize_email(get_value(user_1754, 'email', ''), email_mapping)
        buddies_1754 = get_value(user_1754, 'accountability_buddies', '')
        extracted_1754 = extract_emails_from_accountability_buddies(buddies_1754, email_mapping)
        print(f"  User 1754 ({email_1754}) references: {extracted_1754}")
    
    if missing_user:
        email_missing = normalize_email(get_value(missing_user, 'email', ''), email_mapping)
        buddies_missing = get_value(missing_user, 'accountability_buddies', '')
        extracted_missing = extract_emails_from_accountability_buddies(buddies_missing, email_mapping)
        print(f"  Missing User ({email_missing}) references: {extracted_missing}")
    
    # Check for connections between these users
    print(f"\n🔗 CHECKING CONNECTIONS:")
    
    all_emails = []
    if user_1710:
        all_emails.append(email_1710)
    if user_2013:
        all_emails.append(email_2013)
    if user_1754:
        all_emails.append(email_1754)
    if missing_user:
        all_emails.append(email_missing)
    
    print(f"  All emails: {all_emails}")
    
    # Check if any user references another
    connections_found = []
    for i, email1 in enumerate(all_emails):
        for j, email2 in enumerate(all_emails):
            if i != j:
                # Check if email1 references email2
                if user_1710 and email1 == email_1710 and email2 in extracted_1710:
                    connections_found.append(f"{email1} -> {email2}")
                elif user_2013 and email1 == email_2013 and email2 in extracted_2013:
                    connections_found.append(f"{email1} -> {email2}")
                elif user_1754 and email1 == email_1754 and email2 in extracted_1754:
                    connections_found.append(f"{email1} -> {email2}")
                elif missing_user and email1 == email_missing and email2 in extracted_missing:
                    connections_found.append(f"{email1} -> {email2}")
    
    if connections_found:
        print(f"  ✅ Connections found: {connections_found}")
    else:
        print(f"  ❌ No direct connections found between these users")
    
    # Test grouping with just these users
    print(f"\n🚀 TESTING GROUPING WITH THESE USERS:")
    
    test_users = []
    if user_1710:
        test_users.append(user_1710)
    if user_2013:
        test_users.append(user_2013)
    if user_1754:
        test_users.append(user_1754)
    if missing_user:
        test_users.append(missing_user)
    
    if test_users:
        solo_groups, grouped, excluded_users, requested_groups = group_participants(test_users, column_mapping)
        
        print(f"\n📊 RESULTS:")
        print(f"  Solo groups: {len(solo_groups)}")
        print(f"  Regular groups: {len(grouped)}")
        print(f"  Requested groups: {len(requested_groups)}")
        print(f"  Excluded users: {len(excluded_users)}")
        
        # Check where users ended up
        print(f"\n🔍 WHERE USERS ENDED UP:")
        
        for i, group in enumerate(requested_groups):
            print(f"  Requested Group {i+1} ({len(group)} members):")
            for j, member in enumerate(group):
                user_id = get_value(member, 'user_id', '')
                name = get_value(member, 'name', '')
                email = get_value(member, 'email', '')
                print(f"    {j+1}. {user_id} {name} ({email})")
        
        # Check if all users are in the same group
        all_user_ids = [str(get_value(user, 'user_id', '')).strip() for user in test_users]
        all_in_same_group = False
        
        for i, group in enumerate(requested_groups):
            group_user_ids = [str(get_value(member, 'user_id', '')).strip() for member in group]
            if all(uid in group_user_ids for uid in all_user_ids):
                all_in_same_group = True
                print(f"\n🎉 SUCCESS! All users are in Requested Group {i+1}")
                break
        
        if not all_in_same_group:
            print(f"\n❌ FAILURE! Not all users are in the same group")
    
    # Test with full dataset to see where they end up
    print(f"\n🚀 TESTING WITH FULL DATASET:")
    solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)
    
    # Find where our users ended up in the full dataset
    user_1710_group = None
    user_2013_group = None
    user_1754_group = None
    missing_user_group = None
    
    for i, group in enumerate(requested_groups):
        user_ids = [get_value(member, 'user_id', '') for member in group]
        if '1710' in user_ids:
            user_1710_group = i + 1
        if '2013' in user_ids:
            user_2013_group = i + 1
        if '1754' in user_ids:
            user_1754_group = i + 1
        if missing_user and str(get_value(missing_user, 'user_id', '')).strip() in user_ids:
            missing_user_group = i + 1
    
    print(f"\n📊 FULL DATASET RESULTS:")
    print(f"  User 1710: Requested Group {user_1710_group}")
    print(f"  User 2013: Requested Group {user_2013_group}")
    print(f"  User 1754: Requested Group {user_1754_group}")
    if missing_user:
        print(f"  Missing User: Requested Group {missing_user_group}")
    
    # Check if they should be in the same group
    groups = [user_1710_group, user_2013_group, user_1754_group]
    if missing_user:
        groups.append(missing_user_group)
    
    groups = [g for g in groups if g is not None]
    
    if len(set(groups)) == 1:
        print(f"\n🎉 PERFECT! All users are in the same group: Requested Group {groups[0]}")
        print(f"✅ GROUPS SHOULD BE COMBINED!")
    else:
        print(f"\n❌ FAILURE! Users are in different groups: {groups}")
        print(f"❌ GROUPS SHOULD BE COMBINED BUT AREN'T!")

if __name__ == "__main__":
    investigate_group_81_130() 