import pandas as pd
from group_assignment_to_excel import group_participants, find_column_mapping

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx')

# Find column mapping
column_mapping = find_column_mapping(df)

# Convert to list of dictionaries
data = df.to_dict('records')

print('Checking if missing users are in requested_groups:')
print('=' * 60)

# Run the group assignment
solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)

# Target emails to check
target_emails = ['lilyroseanne.gutierrez@gmail.com', 'carolineongco0392@yahoo.com.au', 'karenpicache@gmail.com']

print(f'\nTotal requested groups: {len(requested_groups)}')

# Helper function to get value safely
def get_value(row, key, default=''):
    if column_mapping and key in column_mapping:
        if isinstance(row, dict):
            return row.get(column_mapping[key], default)
    return default

# Check each target user
for email in target_emails:
    print(f'\n{email}:')
    found = False
    
    for i, group in enumerate(requested_groups):
        group_emails = [get_value(member, 'email', '').lower().strip() for member in group]
        if email in group_emails:
            print(f'  ✅ Found in requested group {i+1}')
            print(f'  Group members: {group_emails}')
            found = True
            break
    
    if not found:
        print(f'  ❌ NOT FOUND in any requested group')

print(f'\nTotal requested groups: {len(requested_groups)}')
print(f'Total users in requested groups: {sum(len(group) for group in requested_groups)}') 