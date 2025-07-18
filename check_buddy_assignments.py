import pandas as pd
from group_assignment_to_excel import find_column_mapping

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx')

# Find column mapping
column_mapping = find_column_mapping(df)

# Target emails and their buddies
target_buddies = {
    'lilyroseanne.gutierrez@gmail.com': 'royal.narne@gmail.com',
    'carolineongco0392@yahoo.com.au': 'jane.alojamiento@yahoo.com',
    'karenpicache@gmail.com': 'mavis.rosete@gmail.com'
}

print('Checking buddy assignments:')
print('=' * 50)

# Helper function to get value safely
def get_value(row, key, default=''):
    if column_mapping and key in column_mapping:
        if isinstance(row, dict):
            return row.get(column_mapping[key], default)
    return default

# Convert to list of dictionaries
data = df.to_dict('records')

# Check each target user and their buddy
for target_email, buddy_email in target_buddies.items():
    print(f'\n{target_email}:')
    
    # Find target user
    target_user = None
    for row in data:
        user_email = get_value(row, 'email', '').lower().strip()
        if user_email == target_email:
            target_user = row
            break
    
    if target_user:
        print(f'  ✅ Target user found')
        target_id = get_value(target_user, 'user_id', 'Unknown')
        print(f'  Target User ID: {target_id}')
        
        # Find buddy user
        buddy_user = None
        for row in data:
            user_email = get_value(row, 'email', '').lower().strip()
            if user_email == buddy_email:
                buddy_user = row
                break
        
        if buddy_user:
            print(f'  ✅ Buddy user found')
            buddy_id = get_value(buddy_user, 'user_id', 'Unknown')
            print(f'  Buddy User ID: {buddy_id}')
            
            # Check if buddy has accountability buddies
            buddy_has_buddies = get_value(buddy_user, 'has_accountability_buddies', '0')
            buddy_accountability_buddies = get_value(buddy_user, 'accountability_buddies', '')
            
            print(f'  Buddy hasAccountabilityBuddies: {buddy_has_buddies}')
            print(f'  Buddy accountabilityBuddies: {buddy_accountability_buddies}')
            
            # Check if buddy's accountability buddies include the target user
            if isinstance(buddy_accountability_buddies, str):
                cleaned = buddy_accountability_buddies.strip('[]').replace('"', '').replace("'", '')
                buddy_requested_emails = [email.strip().lower() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
                
                if target_email in buddy_requested_emails:
                    print(f'  ✅ Buddy includes target user in their accountability buddies')
                else:
                    print(f'  ❌ Buddy does NOT include target user in their accountability buddies')
                    print(f'  Buddy requested emails: {buddy_requested_emails}')
        else:
            print(f'  ❌ Buddy user not found')
    else:
        print(f'  ❌ Target user not found')

print(f'\nTotal records in file: {len(df)}') 