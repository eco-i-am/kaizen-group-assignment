import pandas as pd
from group_assignment_to_excel import find_column_mapping

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx')

# Find column mapping
column_mapping = find_column_mapping(df)

# Target emails to trace
target_emails = ['lilyroseanne.gutierrez@gmail.com', 'carolineongco0392@yahoo.com.au', 'karenpicache@gmail.com']

print('Tracing group assignment for missing users:')
print('=' * 60)

# Helper function to get value safely
def get_value(row, key, default=''):
    if column_mapping and key in column_mapping:
        if isinstance(row, dict):
            return row.get(column_mapping[key], default)
    return default

# Convert to list of dictionaries
data = df.to_dict('records')

# Create email to user mapping
email_to_user = {}
for row in data:
    email = get_value(row, 'email', '')
    if email and '@' in email:
        email_to_user[email.lower().strip()] = row

print(f'Total users in email mapping: {len(email_to_user)}')

# Check each target user
for email in target_emails:
    print(f'\n{email}:')
    
    # Check if user is in email mapping
    if email.lower().strip() in email_to_user:
        user = email_to_user[email.lower().strip()]
        print(f'  ✅ Found in email mapping')
        
        # Get user details
        user_id = get_value(user, 'user_id', 'Unknown')
        accountability_buddies = get_value(user, 'accountability_buddies', '')
        
        print(f'  User ID: {user_id}')
        print(f'  accountabilityBuddies: {accountability_buddies}')
        
        # Extract emails from accountability buddies
        if isinstance(accountability_buddies, str):
            cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
            requested_emails = [email.strip().lower() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
            print(f'  Extracted emails: {requested_emails}')
            
            # Check if buddies exist in data
            for buddy_email in requested_emails:
                if buddy_email in email_to_user:
                    buddy_user = email_to_user[buddy_email]
                    buddy_id = get_value(buddy_user, 'user_id', 'Unknown')
                    print(f'    ✅ {buddy_email}: Found (User ID: {buddy_id})')
                else:
                    print(f'    ❌ {buddy_email}: NOT FOUND in data')
        else:
            print(f'  accountabilityBuddies is not a string: {type(accountability_buddies)}')
    else:
        print(f'  ❌ NOT FOUND in email mapping')

print(f'\nTotal records in file: {len(df)}') 