import pandas as pd
from group_assignment_to_excel import group_participants, find_column_mapping, save_to_excel

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx')

# Find column mapping
column_mapping = find_column_mapping(df)

# Convert to list of dictionaries
data = df.to_dict('records')

print('Checking main script logic:')
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

# Now let's save to Excel and check if the users are in the output
print(f'\nSaving to Excel...')
save_to_excel(solo_groups, grouped, 'test_output.xlsx', column_mapping, excluded_users, requested_groups)

# Check the Excel output
df_output = pd.read_excel('test_output.xlsx')
print(f'\nChecking Excel output:')
for email in target_emails:
    found = False
    print(f'\n{email}:')
    
    # Check all user ID columns
    for col in ['User ID 1', 'User ID 2', 'User ID 3', 'User ID 4', 'User ID 5', 'User ID 6', 'User ID 7']:
        if col in df_output.columns:
            matches = df_output[df_output[col] == email]
            if len(matches) > 0:
                found = True
                group_name = matches.iloc[0]['Group Name']
                print(f'  ✅ Found in {col}')
                print(f'  Group: {group_name}')
                break
    
    if not found:
        print(f'  ❌ NOT FOUND in Excel output') 