import pandas as pd

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx')

# Target emails to investigate
target_emails = ['lilyroseanne.gutierrez@gmail.com', 'carolineongco0392@yahoo.com.au', 'karenpicache@gmail.com']

print('Investigating missing users:')
print('=' * 60)

for email in target_emails:
    matches = df[df['email'] == email]
    print(f'\n{email}:')
    
    if len(matches) > 0:
        user = matches.iloc[0]
        print(f'  User ID: {user.get("id_y", "N/A")}')
        print(f'  Name: {user.get("name", "N/A")}')
        print(f'  joiningAsStudent: {user.get("joiningAsStudent", "N/A")}')
        print(f'  goSolo: {user.get("goSolo", "N/A")}')
        print(f'  hasAccountabilityBuddies: {user.get("hasAccountabilityBuddies", "N/A")}')
        print(f'  accountabilityBuddies: {user.get("accountabilityBuddies", "N/A")}')
        print(f'  temporaryTeamName: {user.get("temporaryTeamName", "N/A")}')
        
        # Check if their buddies exist in the data
        accountability_buddies = user.get("accountabilityBuddies", [])
        if accountability_buddies and isinstance(accountability_buddies, list):
            print(f'  Checking buddies:')
            for buddy_email in accountability_buddies:
                if buddy_email and buddy_email != 'None':
                    buddy_matches = df[df['email'] == buddy_email]
                    if len(buddy_matches) > 0:
                        print(f'    ✅ {buddy_email}: Found in data (User ID: {buddy_matches.iloc[0].get("id_y", "N/A")})')
                    else:
                        print(f'    ❌ {buddy_email}: NOT FOUND in data')
                else:
                    print(f'    ⚠️  {buddy_email}: Invalid email')
    else:
        print(f'  ❌ User not found in data')

print(f'\nTotal records in file: {len(df)}')
print(f'Unique emails: {df["email"].nunique()}') 