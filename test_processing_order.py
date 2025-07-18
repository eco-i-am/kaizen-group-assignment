import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import find_column_mapping, extract_emails_from_accountability_buddies, normalize_email

def test_processing_order():
    """Test to check the order of processing in mutual buddy groups"""
    
    print("🧪 TESTING PROCESSING ORDER")
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
    
    # Find the key users
    morris_user = None
    gerard_user = None
    john_user = None
    
    for row in data:
        user_id = get_value(row, 'user_id', '')
        if str(user_id).strip() == '2360':
            morris_user = row
        elif str(user_id).strip() == '2123':
            gerard_user = row
        elif str(user_id).strip() == '2817':
            john_user = row
    
    if not morris_user or not gerard_user or not john_user:
        print(f"❌ Could not find all three users")
        return
    
    print(f"\n📋 USER DATA:")
    print(f"  Morris (ID 2360): {get_value(morris_user, 'name', '')}")
    print(f"    Has Accountability Buddies: {get_value(morris_user, 'has_accountability_buddies', '')}")
    print(f"    Accountability Buddies: {get_value(morris_user, 'accountability_buddies', '')}")
    
    print(f"  Gerard (ID 2123): {get_value(gerard_user, 'name', '')}")
    print(f"    Has Accountability Buddies: {get_value(gerard_user, 'has_accountability_buddies', '')}")
    print(f"    Accountability Buddies: {get_value(gerard_user, 'accountability_buddies', '')}")
    
    print(f"  John (ID 2817): {get_value(john_user, 'name', '')}")
    print(f"    Has Accountability Buddies: {get_value(john_user, 'has_accountability_buddies', '')}")
    print(f"    Accountability Buddies: {get_value(john_user, 'accountability_buddies', '')}")
    
    # Create email mapping
    email_mapping = {}
    
    # Extract emails
    morris_email = normalize_email(get_value(morris_user, 'email', ''), email_mapping)
    gerard_email = normalize_email(get_value(gerard_user, 'email', ''), email_mapping)
    john_email = normalize_email(get_value(john_user, 'email', ''), email_mapping)
    
    print(f"\n📧 EMAILS:")
    print(f"  Morris: {morris_email}")
    print(f"  Gerard: {gerard_email}")
    print(f"  John: {john_email}")
    
    # Check who references whom
    print(f"\n🔍 REFERENCE ANALYSIS:")
    
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
    
    # Check mutual relationships
    print(f"\n🤝 MUTUAL RELATIONSHIPS:")
    
    # Morris -> Gerard (one-way)
    if gerard_email in morris_extracted:
        print(f"  ✅ Morris -> Gerard")
    else:
        print(f"  ❌ Morris -X-> Gerard")
    
    # John -> Morris (one-way)
    if morris_email in john_extracted:
        print(f"  ✅ John -> Morris")
    else:
        print(f"  ❌ John -X-> Morris")
    
    # Gerard -> Morris (should be false)
    if morris_email in gerard_extracted:
        print(f"  ✅ Gerard -> Morris")
    else:
        print(f"  ❌ Gerard -X-> Morris")
    
    # John -> Gerard (should be false)
    if gerard_email in john_extracted:
        print(f"  ✅ John -> Gerard")
    else:
        print(f"  ❌ John -X-> Gerard")
    
    # Check who has has_accountability_buddies=True
    print(f"\n📋 ACCOUNTABILITY BUDDIES FLAGS:")
    morris_has_buddies = str(get_value(morris_user, 'has_accountability_buddies', '')).strip().lower() in ['1', '1.0', 'true', 'yes']
    john_has_buddies = str(get_value(john_user, 'has_accountability_buddies', '')).strip().lower() in ['1', '1.0', 'true', 'yes']
    gerard_has_buddies = str(get_value(gerard_user, 'has_accountability_buddies', '')).strip().lower() in ['1', '1.0', 'true', 'yes']
    
    print(f"  Morris has_accountability_buddies: {morris_has_buddies}")
    print(f"  John has_accountability_buddies: {john_has_buddies}")
    print(f"  Gerard has_accountability_buddies: {gerard_has_buddies}")
    
    # Simulate the processing order
    print(f"\n🔄 SIMULATING PROCESSING ORDER:")
    
    # First pass: collect users with has_accountability_buddies=True
    accountability_participants = []
    if morris_has_buddies:
        accountability_participants.append(('Morris', morris_user))
        print(f"  ✅ Morris added (has_accountability_buddies=True)")
    if john_has_buddies:
        accountability_participants.append(('John', john_user))
        print(f"  ✅ John added (has_accountability_buddies=True)")
    if gerard_has_buddies:
        accountability_participants.append(('Gerard', gerard_user))
        print(f"  ✅ Gerard added (has_accountability_buddies=True)")
    
    # Second pass: collect referenced buddies
    referenced_buddies = set()
    for name, user in [('Morris', morris_user), ('John', john_user), ('Gerard', gerard_user)]:
        buddies = get_value(user, 'accountability_buddies', '')
        if buddies:
            emails = extract_emails_from_accountability_buddies(buddies, email_mapping)
            referenced_buddies.update(emails)
            print(f"  {name} references: {emails}")
    
    print(f"  All referenced emails: {referenced_buddies}")
    
    # Add users who are referenced but not already included
    for name, user in [('Morris', morris_user), ('John', john_user), ('Gerard', gerard_user)]:
        user_email = normalize_email(get_value(user, 'email', ''), email_mapping)
        if user_email in referenced_buddies:
            # Check if already included
            already_included = any(
                normalize_email(get_value(acc_user, 'email', ''), email_mapping) == user_email 
                for _, acc_user in accountability_participants
            )
            
            if not already_included:
                accountability_participants.append((name, user))
                print(f"  ✅ {name} added (referenced by others)")
    
    print(f"\n📋 FINAL ACCOUNTABILITY PARTICIPANTS:")
    for name, user in accountability_participants:
        user_email = normalize_email(get_value(user, 'email', ''), email_mapping)
        print(f"  {name}: {user_email}")
    
    # Simulate mutual buddy group creation
    print(f"\n👥 SIMULATING MUTUAL BUDDY GROUP CREATION:")
    
    email_to_user = {
        morris_email: morris_user,
        gerard_email: gerard_user,
        john_email: john_user
    }
    
    mutual_buddy_groups = []
    processed_users = set()
    
    for name, participant in accountability_participants:
        participant_email = normalize_email(get_value(participant, 'email', ''), email_mapping)
        
        if participant_email in processed_users:
            continue
        
        print(f"\n  Processing {name} ({participant_email}):")
        
        # Find all users who want to be grouped together
        mutual_group = [participant]
        processed_users.add(participant_email)
        
        # Get this user's buddies
        accountability_buddies = get_value(participant, 'accountability_buddies', '')
        requested_emails = extract_emails_from_accountability_buddies(accountability_buddies, email_mapping)
        
        print(f"    {name} references: {requested_emails}")
        
        # Include all buddies that this user references (both mutual and one-way relationships)
        for email in requested_emails:
            if email in email_to_user:
                buddy_user = email_to_user[email]
                buddy_email = normalize_email(get_value(buddy_user, 'email', ''), email_mapping)
                
                if buddy_email not in processed_users:
                    mutual_group.append(buddy_user)
                    processed_users.add(buddy_email)
                    print(f"    ✅ Added {buddy_email} to group")
                else:
                    print(f"    ❌ {buddy_email} already processed")
        
        if len(mutual_group) > 1:
            mutual_buddy_groups.append(mutual_group)
            print(f"    📦 Created mutual group with {len(mutual_group)} members")
            
            # Show group members
            for member in mutual_group:
                member_email = normalize_email(get_value(member, 'email', ''), email_mapping)
                member_name = get_value(member, 'name', '')
                print(f"      - {member_name} ({member_email})")
        else:
            print(f"    📦 Single user group for {name}")
    
    print(f"\n📊 FINAL MUTUAL BUDDY GROUPS:")
    for i, group in enumerate(mutual_buddy_groups):
        print(f"  Group {i+1}:")
        for member in group:
            member_email = normalize_email(get_value(member, 'email', ''), email_mapping)
            member_name = get_value(member, 'name', '')
            print(f"    - {member_name} ({member_email})")

if __name__ == "__main__":
    test_processing_order() 