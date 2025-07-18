import pandas as pd

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx')

# Target emails to look for
target_emails = ['lilyroseanne.gutierrez@gmail.com', 'carolineongco0392@yahoo.com.au', 'karenpicache@gmail.com']

print('Looking for specific users:')
print('=' * 50)

for email in target_emails:
    matches = df[df['email'] == email]
    print(f'\n{email}: {len(matches)} matches')
    
    if len(matches) > 0:
        user = matches.iloc[0]
        print(f'  User ID: {user.get("id_x", "N/A")}')
        print(f'  Name: {user.get("name", "N/A")}')
        print(f'  joiningAsStudent: {user.get("joiningAsStudent", "N/A")}')
        print(f'  goSolo: {user.get("goSolo", "N/A")}')
        print(f'  hasAccountabilityBuddies: {user.get("hasAccountabilityBuddies", "N/A")}')
        print(f'  accountabilityBuddies: {user.get("accountabilityBuddies", "N/A")}')
        print(f'  temporaryTeamName: {user.get("temporaryTeamName", "N/A")}')
    else:
        print(f'  ❌ User not found in data')

print(f'\nTotal records in file: {len(df)}')
print(f'Unique emails: {df["email"].nunique()}') 