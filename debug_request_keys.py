import pandas as pd
from group_assignment_to_excel import find_column_mapping

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx')

# Find column mapping
column_mapping = find_column_mapping(df)

# Target emails to debug
target_emails = ['lilyroseanne.gutierrez@gmail.com', 'carolineongco0392@yahoo.com.au', 'karenpicache@gmail.com']

print('Debugging request keys for missing users:')
print('=' * 60)

# Helper function to get value safely
def get_value(row, key, default=''):
    if column_mapping and key in column_mapping:
        if isinstance(row, dict):
            return row.get(column_mapping[key], default)
    return default

# Convert to list of dictionaries
data = df.to_dict('records')

# Find target users
target_users = []
for row in data:
    user_email = get_value(row, 'email', '').lower().strip()
    if user_email in target_emails:
        target_users.append(row)

print(f'Found {len(target_users)} target users')

# Process each target user
processed_requests = set()

for user in target_users:
    user_email = get_value(user, 'email', '').lower().strip()
    accountability_buddies = get_value(user, 'accountability_buddies', '')
    
    print(f'\n{user_email}:')
    print(f'  accountabilityBuddies: {accountability_buddies}')
    
    # Clean and extract emails from accountabilityBuddies
    if isinstance(accountability_buddies, str):
        cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
        requested_emails = [email.strip().lower() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
        
        print(f'  Extracted emails: {requested_emails}')
        
        if requested_emails:
            request_key = ','.join(sorted(requested_emails))
            print(f'  Request key: "{request_key}"')
            
            if request_key in processed_requests:
                print(f'  ❌ Request key already processed')
            else:
                print(f'  ✅ Request key not processed yet')
                processed_requests.add(request_key)
        else:
            print(f'  ❌ No valid emails extracted')
    else:
        print(f'  ❌ accountabilityBuddies is not a string')

print(f'\nTotal processed requests: {len(processed_requests)}')
print(f'Processed request keys: {sorted(processed_requests)}') 