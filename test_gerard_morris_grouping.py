import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import find_column_mapping, group_participants, extract_emails_from_accountability_buddies, normalize_email

def test_gerard_morris_grouping():
    """Test the specific Gerard-Morris grouping issue"""
    
    print("🧪 TESTING GERARD-MORRIS GROUPING")
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
    
    # Find Gerard and Morris
    gerard_user = None
    morris_user = None
    
    for row in data:
        user_id = get_value(row, 'user_id', '')
        email = get_value(row, 'email', '')
        
        if str(user_id).strip() == '2123':  # Gerard
            gerard_user = row
        elif str(user_id).strip() == '2360':  # Morris
            morris_user = row
    
    if not gerard_user or not morris_user:
        print(f"❌ Could not find Gerard or Morris")
        return
    
    print(f"\n🔍 GERARD DATA:")
    print(f"  User ID: {get_value(gerard_user, 'user_id', '')}")
    print(f"  Name: {get_value(gerard_user, 'name', '')}")
    print(f"  Email: {get_value(gerard_user, 'email', '')}")
    print(f"  Has Accountability Buddies: {get_value(gerard_user, 'has_accountability_buddies', '')}")
    print(f"  Accountability Buddies: {get_value(gerard_user, 'accountability_buddies', '')}")
    print(f"  Joining as Student: {get_value(gerard_user, 'joining_as_student', '')}")
    
    print(f"\n🔍 MORRIS DATA:")
    print(f"  User ID: {get_value(morris_user, 'user_id', '')}")
    print(f"  Name: {get_value(morris_user, 'name', '')}")
    print(f"  Email: {get_value(morris_user, 'email', '')}")
    print(f"  Has Accountability Buddies: {get_value(morris_user, 'has_accountability_buddies', '')}")
    print(f"  Accountability Buddies: {get_value(morris_user, 'accountability_buddies', '')}")
    
    # Test email extraction from Morris's accountability buddies
    morris_buddies = get_value(morris_user, 'accountability_buddies', '')
    print(f"\n🔍 MORRIS'S ACCOUNTABILITY BUDDIES EXTRACTION:")
    print(f"  Raw value: {morris_buddies}")
    
    # Create email mapping
    email_mapping = {}
    
    extracted_emails = extract_emails_from_accountability_buddies(morris_buddies, email_mapping)
    print(f"  Extracted emails: {extracted_emails}")
    
    gerard_email = normalize_email(get_value(gerard_user, 'email', ''), email_mapping)
    print(f"  Gerard's normalized email: {gerard_email}")
    
    if gerard_email in extracted_emails:
        print(f"  ✅ Gerard's email found in Morris's buddies!")
    else:
        print(f"  ❌ Gerard's email NOT found in Morris's buddies!")
        
        # Check if there's a case sensitivity issue
        gerard_email_lower = gerard_email.lower()
        extracted_lower = [email.lower() for email in extracted_emails]
        if gerard_email_lower in extracted_lower:
            print(f"  ⚠️  Found after converting to lowercase")
        else:
            print(f"  ❌ Still not found after converting to lowercase")
    
    # Test the filtering logic
    print(f"\n🔍 TESTING FILTERING LOGIC:")
    joining_value = get_value(gerard_user, 'joining_as_student', 'True')
    joining_str = str(joining_value).strip().lower()
    print(f"  Gerard's joiningAsStudent: {joining_value}")
    print(f"  As string: '{joining_str}'")
    
    if joining_str in ['false', '0', '0.0', 'no']:
        print(f"  ❌ Gerard would be EXCLUDED by filtering logic")
    else:
        print(f"  ✅ Gerard would be KEPT by filtering logic")
    
    # Test if Gerard would be included in accountability participants
    print(f"\n🔍 TESTING ACCOUNTABILITY PARTICIPANTS LOGIC:")
    has_accountability_buddies = get_value(gerard_user, 'has_accountability_buddies', '0')
    has_buddies = str(has_accountability_buddies).strip().lower() in ['1', '1.0', 'true', 'yes']
    print(f"  Gerard's has_accountability_buddies: {has_accountability_buddies}")
    print(f"  Has buddies (boolean): {has_buddies}")
    
    if has_buddies:
        print(f"  ✅ Gerard would be included due to has_accountability_buddies=True")
    else:
        print(f"  ❌ Gerard would NOT be included due to has_accountability_buddies=False")
        
        # Check if he's referenced by others
        gerard_email_normalized = normalize_email(get_value(gerard_user, 'email', ''), email_mapping)
        referenced_buddies = set()
        
        for row in data:
            accountability_buddies = get_value(row, 'accountability_buddies', '')
            if accountability_buddies:
                emails = extract_emails_from_accountability_buddies(accountability_buddies, email_mapping)
                referenced_buddies.update(emails)
        
        print(f"  All referenced emails: {referenced_buddies}")
        
        if gerard_email_normalized in referenced_buddies:
            print(f"  ✅ Gerard would be included because he's referenced by others")
        else:
            print(f"  ❌ Gerard would NOT be included because he's not referenced by others")
    
    # Run the actual grouping function
    print(f"\n🚀 RUNNING ACTUAL GROUPING FUNCTION...")
    solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)
    
    # Check where Gerard ended up
    gerard_found = False
    print(f"\n🔍 WHERE GERARD ENDED UP:")
    
    # Check solo groups
    for i, group in enumerate(solo_groups):
        for member in group:
            if get_value(member, 'user_id', '') == '2123':
                print(f"  ✅ Gerard found in Solo Group {i+1}")
                gerard_found = True
                break
    
    # Check requested groups
    for i, group in enumerate(requested_groups):
        for member in group:
            if get_value(member, 'user_id', '') == '2123':
                print(f"  ✅ Gerard found in Requested Group {i+1}")
                print(f"    Group members:")
                for j, group_member in enumerate(group):
                    member_id = get_value(group_member, 'user_id', '')
                    member_name = get_value(group_member, 'name', '')
                    member_email = get_value(group_member, 'email', '')
                    print(f"      {j+1}. {member_id} {member_name} ({member_email})")
                gerard_found = True
                break
    
    # Check regular groups
    for group_name, members in grouped.items():
        for member in members:
            if get_value(member, 'user_id', '') == '2123':
                print(f"  ✅ Gerard found in Regular Group: {group_name}")
                gerard_found = True
                break
    
    if not gerard_found:
        print(f"  ❌ Gerard NOT found in any group!")
    
    # Check where Morris ended up
    morris_found = False
    print(f"\n🔍 WHERE MORRIS ENDED UP:")
    
    # Check requested groups
    for i, group in enumerate(requested_groups):
        for member in group:
            if get_value(member, 'user_id', '') == '2360':
                print(f"  ✅ Morris found in Requested Group {i+1}")
                print(f"    Group members:")
                for j, group_member in enumerate(group):
                    member_id = get_value(group_member, 'user_id', '')
                    member_name = get_value(group_member, 'name', '')
                    member_email = get_value(group_member, 'email', '')
                    print(f"      {j+1}. {member_id} {member_name} ({member_email})")
                morris_found = True
                break
    
    if not morris_found:
        print(f"  ❌ Morris NOT found in requested groups!")

if __name__ == "__main__":
    test_gerard_morris_grouping() 