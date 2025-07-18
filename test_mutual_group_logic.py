import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import find_column_mapping, extract_emails_from_accountability_buddies, normalize_email, create_email_mapping

def test_mutual_group_logic():
    """Test the mutual group logic for Al Baljon"""
    
    print("🔍 TESTING MUTUAL GROUP LOGIC FOR AL BALJON")
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
    
    # Create email mapping
    email_mapping = create_email_mapping(data, column_mapping)
    
    # Find our three users
    al_baljon = None
    mark_lester = None
    mark_anthony = None
    
    for row in data:
        user_id = get_value(row, 'user_id', '')
        if str(user_id).strip() == '1754':
            al_baljon = row
        elif str(user_id).strip() == '1710':
            mark_lester = row
        elif str(user_id).strip() == '2013':
            mark_anthony = row
    
    if not all([al_baljon, mark_lester, mark_anthony]):
        print("❌ Could not find all three users")
        return
    
    # Simulate the accountability participant collection
    print(f"\n🔍 SIMULATING ACCOUNTABILITY PARTICIPANT COLLECTION:")
    accountability_participants = []
    
    for row in data:
        accountability_buddies = get_value(row, 'accountability_buddies', '')
        has_accountability_buddies = get_value(row, 'has_accountability_buddies', '0')
        user_id = get_value(row, 'user_id', 'Unknown')
        
        has_buddies = str(has_accountability_buddies).strip().lower() in ['1', '1.0', 'true', 'yes']
        
        if has_buddies:
            accountability_participants.append(row)
    
    # Add users who are referenced as buddies
    referenced_buddies = set()
    for row in data:
        accountability_buddies = get_value(row, 'accountability_buddies', '')
        if accountability_buddies:
            emails = extract_emails_from_accountability_buddies(accountability_buddies, email_mapping)
            referenced_buddies.update(emails)
    
    for row in data:
        user_email = normalize_email(get_value(row, 'email', ''), email_mapping)
        if user_email in referenced_buddies:
            already_included = any(
                normalize_email(get_value(acc_user, 'email', ''), email_mapping) == user_email 
                for acc_user in accountability_participants
            )
            if not already_included:
                accountability_participants.append(row)
    
    print(f"  Total accountability participants: {len(accountability_participants)}")
    
    # Check if our users are in accountability_participants
    al_baljon_email = normalize_email(get_value(al_baljon, 'email', ''), email_mapping)
    mark_lester_email = normalize_email(get_value(mark_lester, 'email', ''), email_mapping)
    mark_anthony_email = normalize_email(get_value(mark_anthony, 'email', ''), email_mapping)
    
    al_baljon_in_acc = any(
        normalize_email(get_value(acc_user, 'email', ''), email_mapping) == al_baljon_email 
        for acc_user in accountability_participants
    )
    mark_lester_in_acc = any(
        normalize_email(get_value(acc_user, 'email', ''), email_mapping) == mark_lester_email 
        for acc_user in accountability_participants
    )
    mark_anthony_in_acc = any(
        normalize_email(get_value(acc_user, 'email', ''), email_mapping) == mark_anthony_email 
        for acc_user in accountability_participants
    )
    
    print(f"  Al Baljon in accountability_participants: {al_baljon_in_acc}")
    print(f"  Mark Lester in accountability_participants: {mark_lester_in_acc}")
    print(f"  Mark Anthony in accountability_participants: {mark_anthony_in_acc}")
    
    # Create email to user mapping
    email_to_user = {}
    for row in data:
        email = get_value(row, 'email', '')
        if email and '@' in email:
            normalized_email = normalize_email(email, email_mapping)
            email_to_user[normalized_email] = row
    
    # Simulate the mutual buddy group processing
    print(f"\n🔍 SIMULATING MUTUAL BUDDY GROUP PROCESSING:")
    
    # Create a graph of all accountability buddy relationships
    buddy_graph = {}
    for participant in accountability_participants:
        participant_email = normalize_email(get_value(participant, 'email', ''), email_mapping)
        accountability_buddies = get_value(participant, 'accountability_buddies', '')
        requested_emails = extract_emails_from_accountability_buddies(accountability_buddies, email_mapping)
        
        if participant_email not in buddy_graph:
            buddy_graph[participant_email] = set()
        
        # Add direct references
        for email in requested_emails:
            if email in email_to_user:
                buddy_graph[participant_email].add(email)
        
        # Also add reverse references (users who reference this participant)
        for other_participant in accountability_participants:
            other_email = normalize_email(get_value(other_participant, 'email', ''), email_mapping)
            other_buddies = get_value(other_participant, 'accountability_buddies', '')
            other_requested_emails = extract_emails_from_accountability_buddies(other_buddies, email_mapping)
            
            if participant_email in other_requested_emails:
                if other_email not in buddy_graph:
                    buddy_graph[other_email] = set()
                buddy_graph[other_email].add(participant_email)
    
    print(f"  Buddy graph created with {len(buddy_graph)} nodes")
    
    # Check the buddy graph for our users
    print(f"\n🔍 BUDDY GRAPH FOR OUR USERS:")
    for email in [al_baljon_email, mark_lester_email, mark_anthony_email]:
        if email in buddy_graph:
            buddies = buddy_graph[email]
            print(f"  {email}: {buddies}")
        else:
            print(f"  {email}: Not in buddy graph")
    
    # Find all connected components using DFS
    def find_connected_component(start_email, visited):
        """Find all emails connected to start_email through buddy relationships"""
        if start_email in visited:
            return set()
        
        visited.add(start_email)
        component = {start_email}
        
        if start_email in buddy_graph:
            for buddy_email in buddy_graph[start_email]:
                if buddy_email in email_to_user:  # Only include emails that exist in our data
                    component.update(find_connected_component(buddy_email, visited))
        
        return component
    
    # Find all connected components
    visited = set()
    mutual_buddy_groups = []
    processed_users = set()
    
    for participant in accountability_participants:
        participant_email = normalize_email(get_value(participant, 'email', ''), email_mapping)
        
        if participant_email not in visited:
            # Find all users connected to this participant
            connected_emails = find_connected_component(participant_email, visited)
            
            print(f"  Processing {participant_email}: connected to {len(connected_emails)} users")
            
            if len(connected_emails) > 1:
                # Create a group with all connected users
                mutual_group = []
                for email in connected_emails:
                    if email in email_to_user:
                        user = email_to_user[email]
                        mutual_group.append(user)
                        processed_users.add(email)
                
                if len(mutual_group) > 1:
                    mutual_buddy_groups.append(mutual_group)
                    print(f"    Created mutual group with {len(mutual_group)} members")
                    
                    # Check if our users are in this group
                    group_emails = [normalize_email(get_value(member, 'email', ''), email_mapping) for member in mutual_group]
                    if all(email in group_emails for email in [al_baljon_email, mark_lester_email, mark_anthony_email]):
                        print(f"    ✅ All three users are in this group!")
                    elif any(email in group_emails for email in [al_baljon_email, mark_lester_email, mark_anthony_email]):
                        print(f"    ⚠️  Some of our users are in this group")
            else:
                # Single user - mark as processed but don't create a group yet
                processed_users.add(participant_email)
                print(f"    Single user - no group created")
    
    print(f"\n📊 MUTUAL BUDDY GROUPS CREATED:")
    print(f"  Total mutual groups: {len(mutual_buddy_groups)}")
    
    # Check if our users are in the same mutual group
    our_users_in_same_group = False
    for i, group in enumerate(mutual_buddy_groups):
        group_emails = [normalize_email(get_value(member, 'email', ''), email_mapping) for member in group]
        group_names = [get_value(member, 'name', '') for member in group]
        
        if all(email in group_emails for email in [al_baljon_email, mark_lester_email, mark_anthony_email]):
            our_users_in_same_group = True
            print(f"  Group {i+1}: {group_names}")
            print(f"    ✅ All three users are in this group!")
        elif any(email in group_emails for email in [al_baljon_email, mark_lester_email, mark_anthony_email]):
            print(f"  Group {i+1}: {group_names}")
            print(f"    ⚠️  Some of our users are in this group")
    
    if our_users_in_same_group:
        print(f"\n🎉 SUCCESS: All three users should be in the same mutual group!")
    else:
        print(f"\n❌ FAILURE: Users are not in the same mutual group")

if __name__ == "__main__":
    test_mutual_group_logic() 