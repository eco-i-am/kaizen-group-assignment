import pandas as pd

# Read the Excel output
df = pd.read_excel('grouped_participants.xlsx')

# Read the original data to get email-to-name mapping
original_df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx', sheet_name='Merged Data')

print('Checking if missing users are in Excel output:')
print('=' * 50)

# Target emails to check
target_emails = ['lilyroseanne.gutierrez@gmail.com', 'carolineongco0392@yahoo.com.au', 'karenpicache@gmail.com']

# Create email to name mapping
email_to_name = {}
for _, row in original_df.iterrows():
    email = row.get('email', '')
    name = row.get('name', '')
    if email and name:
        email_to_name[email.lower().strip()] = name

for email in target_emails:
    found = False
    print(f'\n{email}:')
    
    # Get the name for this email
    name = email_to_name.get(email.lower().strip())
    if not name:
        print(f'  ❌ Name not found for email in original data')
        continue
    
    print(f'  Looking for name: {name}')
    
    # Check all name columns
    for col in ['Name 1', 'Name 2', 'Name 3', 'Name 4', 'Name 5', 'Name 6', 'Name 7']:
        if col in df.columns:
            matches = df[df[col] == name]
            if len(matches) > 0:
                found = True
                group_name = matches.iloc[0]['Group Name']
                print(f'  ✅ Found in {col}')
                print(f'  Group: {group_name}')
                break
    
    if not found:
        print(f'  ❌ NOT FOUND in Excel output')

print(f'\nTotal rows in Excel: {len(df)}')
print(f'Columns: {df.columns.tolist()}') 