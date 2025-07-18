import pandas as pd
from group_assignment_to_excel import find_column_mapping

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx')

# Find column mapping
column_mapping = find_column_mapping(df)

# Target emails to debug
target_emails = ['lilyroseanne.gutierrez@gmail.com', 'carolineongco0392@yahoo.com.au', 'karenpicache@gmail.com']

print('Detailed debugging of missing users:')
print('=' * 60)

# Helper function to get value safely
def get_value(row, key, default=''):
    if column_mapping and key in column_mapping:
        if isinstance(row, dict):
            return row.get(column_mapping[key], default)
    return default

# Check each target user
for email in target_emails:
    matches = df[df['email'] == email]
    print(f'\n{email}:')
    
    if len(matches) > 0:
        user = matches.iloc[0]
        user_dict = user.to_dict()
        
        print(f'  User ID: {get_value(user_dict, "user_id")}')
        print(f'  Name: {get_value(user_dict, "name")}')
        
        # Check joiningAsStudent
        joining_value = get_value(user_dict, 'joining_as_student', 'True')
        joining_str = str(joining_value).strip().lower()
        print(f'  joiningAsStudent: {joining_value} -> {joining_str}')
        
        # Check goSolo
        go_solo_value = str(get_value(user_dict, 'go_solo', '0')).strip()
        print(f'  goSolo: {go_solo_value}')
        
        # Check accountability buddies
        has_buddies = str(get_value(user_dict, 'has_accountability_buddies', '0')).strip().lower() in ['1', '1.0', 'true', 'yes']
        accountability_buddies = get_value(user_dict, 'accountability_buddies', '')
        print(f'  hasAccountabilityBuddies: {get_value(user_dict, "has_accountability_buddies")} -> {has_buddies}')
        print(f'  accountabilityBuddies: {accountability_buddies}')
        print(f'  accountabilityBuddies type: {type(accountability_buddies)}')
        
        # Test the has_buddy_data logic
        has_buddy_data = False
        if accountability_buddies:
            accountability_str = str(accountability_buddies).strip()
            print(f'  accountability_str: "{accountability_str}"')
            
            if accountability_str not in ['', 'None', 'nan', '[None]', '[None, None]', "{'1': None}"]:
                if isinstance(accountability_buddies, str):
                    cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
                    print(f'  cleaned: "{cleaned}"')
                    emails = [email.strip().lower() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
                    print(f'  extracted emails: {emails}')
                    has_buddy_data = len(emails) > 0
                else:
                    has_buddy_data = True
        
        print(f'  has_buddy_data: {has_buddy_data}')
        
        # Check if they should be in accountability buddies
        if has_buddies and has_buddy_data:
            print(f'  ✅ Should be in accountability buddies group')
        else:
            print(f'  ❌ Should NOT be in accountability buddies group')
            
    else:
        print(f'  ❌ User not found in data')

print(f'\nTotal records in file: {len(df)}') 