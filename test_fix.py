import pandas as pd
from group_assignment_to_excel import find_column_mapping

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx')

# Find column mapping
column_mapping = find_column_mapping(df)

# Target emails to debug
target_emails = ['lilyroseanne.gutierrez@gmail.com', 'carolineongco0392@yahoo.com.au', 'karenpicache@gmail.com']

print('Testing the fix for missing users:')
print('=' * 60)

# Helper function to get value safely
def get_value(row, key, default=''):
    if column_mapping and key in column_mapping:
        if isinstance(row, dict):
            return row.get(column_mapping[key], default)
    return default

# Convert to list of dictionaries
data = df.to_dict('records')

# Step 1: Find all accountability participants
accountability_participants = []
for row in data:
    accountability_buddies = get_value(row, 'accountability_buddies', '')
    has_accountability_buddies = get_value(row, 'has_accountability_buddies', '0')
    user_id = get_value(row, 'user_id', 'Unknown')
    user_email = get_value(row, 'email', '').lower().strip()
    
    # Check if has_accountability_buddies is True/1
    has_buddies = str(has_accountability_buddies).strip().lower() in ['1', '1.0', 'true', 'yes']
    
    # Check if accountability_buddies field has valid data
    has_buddy_data = False
    if accountability_buddies:
        accountability_str = str(accountability_buddies).strip()
        if accountability_str not in ['', 'None', 'nan', '[None]', '[None, None]', "{'1': None}"]:
            if isinstance(accountability_buddies, str):
                cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
                emails = [email.strip().lower() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
                has_buddy_data = len(emails) > 0
            else:
                has_buddy_data = True
    
    if has_buddies and has_buddy_data:
        accountability_participants.append(row)
        if user_email in target_emails:
            print(f'✅ {user_email}: Added to accountability_participants')

print(f'\nTotal accountability_participants: {len(accountability_participants)}')

# Step 2: Create email to user mapping
email_to_user = {}
for row in data:
    email = get_value(row, 'email', '')
    if email and '@' in email:
        email_to_user[email.lower().strip()] = row

print(f'Total users in email mapping: {len(email_to_user)}')

# Step 3: Process accountability participants with the new logic
processed_requests = set()
assigned_users = set()
requested_groups = []

print(f'\nProcessing accountability participants with new logic...')

for i, participant in enumerate(accountability_participants):
    accountability_buddies = get_value(participant, 'accountability_buddies', '')
    user_id = get_value(participant, 'user_id', 'Unknown')
    participant_email = get_value(participant, 'email', '').lower().strip()
    
    if participant_email in target_emails:
        print(f'\n🔍 Processing {participant_email} (iteration {i+1}):')
        print(f'  User ID: {user_id}')
        print(f'  accountabilityBuddies: {accountability_buddies}')
        print(f'  Already assigned: {participant_email in assigned_users}')
    
    # Skip if this participant is already assigned to a requested group
    if participant_email in assigned_users:
        if participant_email in target_emails:
            print(f'  ❌ Already assigned to a group')
        continue
    
    # Clean and extract emails from accountabilityBuddies
    if isinstance(accountability_buddies, str):
        cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
        requested_emails = [email.strip().lower() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
        
        if participant_email in target_emails:
            print(f'  Extracted emails: {requested_emails}')
        
        if requested_emails:
            request_key = ','.join(sorted(requested_emails))
            
            if participant_email in target_emails:
                print(f'  Request key: "{request_key}"')
                print(f'  Already processed: {request_key in processed_requests}')
            
            if request_key not in processed_requests:
                processed_requests.add(request_key)
                
                if participant_email in target_emails:
                    print(f'  ✅ Processing this request (new)')
                
                # Create a new group with available buddies (if any)
                available_buddies = []
                for email in requested_emails:
                    if email in email_to_user:
                        buddy_user = email_to_user[email]
                        buddy_email = get_value(buddy_user, 'email', '').lower().strip()
                        if buddy_email not in assigned_users:
                            available_buddies.append(email)
                
                if available_buddies:
                    group_members = [participant]
                    assigned_users.add(participant_email)
                    
                    for email in available_buddies:
                        buddy_user = email_to_user[email]
                        buddy_email = get_value(buddy_user, 'email', '').lower().strip()
                        group_members.append(buddy_user)
                        assigned_users.add(buddy_email)
                    
                    requested_groups.append(group_members)
                    if participant_email in target_emails:
                        print(f'  ✅ Created group with available buddies: {len(group_members)} members')
                else:
                    group_members = [participant]
                    assigned_users.add(participant_email)
                    requested_groups.append(group_members)
                    if participant_email in target_emails:
                        print(f'  ✅ Created solo group (no buddies available)')
            else:
                # Request key already processed - check if user should be added to existing group
                if participant_email in target_emails:
                    print(f'  Request key already processed, checking if should be added to existing group')
                
                # Find existing group that contains any of the requested buddies
                existing_group_with_buddies = None
                for email in requested_emails:
                    if email in email_to_user:
                        buddy_user = email_to_user[email]
                        buddy_email = get_value(buddy_user, 'email', '').lower().strip()
                        
                        if buddy_email in assigned_users:
                            # Find which existing group contains this buddy
                            for i, existing_group in enumerate(requested_groups):
                                existing_emails = [get_value(member, 'email', '').lower().strip() for member in existing_group]
                                if buddy_email in existing_emails:
                                    existing_group_with_buddies = i
                                    break
                            if existing_group_with_buddies is not None:
                                break
                
                if existing_group_with_buddies is not None:
                    existing_group = requested_groups[existing_group_with_buddies]
                    
                    # Check if the group has space (max 5 members)
                    if len(existing_group) < 5:
                        existing_group.append(participant)
                        assigned_users.add(participant_email)
                        if participant_email in target_emails:
                            print(f'  ✅ Added to existing group {existing_group_with_buddies}')
                    else:
                        # Create a new group for this user since existing group is full
                        group_members = [participant]
                        assigned_users.add(participant_email)
                        
                        if group_members:
                            requested_groups.append(group_members)
                            if participant_email in target_emails:
                                print(f'  ✅ Created new group (existing group full): {len(group_members)} members')
                else:
                    # No existing group found - create a solo group
                    group_members = [participant]
                    assigned_users.add(participant_email)
                    
                    if group_members:
                        requested_groups.append(group_members)
                        if participant_email in target_emails:
                            print(f'  ✅ Created solo group (no existing group found): {len(group_members)} members')
        else:
            if participant_email in target_emails:
                print(f'  ❌ No valid emails extracted')
    else:
        if participant_email in target_emails:
            print(f'  ❌ accountabilityBuddies is not a string')

print(f'\nFinal results:')
print(f'Total requested groups: {len(requested_groups)}')
print(f'Total assigned users: {len(assigned_users)}')

# Check if target users are assigned
for email in target_emails:
    if email in assigned_users:
        print(f'✅ {email}: Assigned to a group')
    else:
        print(f'❌ {email}: NOT assigned to any group') 