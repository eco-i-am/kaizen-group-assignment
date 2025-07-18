import pandas as pd

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx')

# Buddy emails to check
buddy_emails = ['royal.narne@gmail.com', 'jane.alojamiento@yahoo.com', 'mavis.rosete@gmail.com']

print('Checking if buddies exist in data:')
print('=' * 50)

for email in buddy_emails:
    matches = df[df['email'] == email]
    print(f'\n{email}: {len(matches)} matches')
    
    if len(matches) > 0:
        user = matches.iloc[0]
        print(f'  User ID: {user.get("id_y", "N/A")}')
        print(f'  Name: {user.get("name", "N/A")}')
        print(f'  hasAccountabilityBuddies: {user.get("hasAccountabilityBuddies", "N/A")}')
        print(f'  accountabilityBuddies: {user.get("accountabilityBuddies", "N/A")}')
    else:
        print(f'  ❌ Buddy not found in data')

print(f'\nTotal records in file: {len(df)}') 