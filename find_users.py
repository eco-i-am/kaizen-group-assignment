import pandas as pd

# Read the merged Excel file
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx', sheet_name='Merged Data')

print("Finding Jaw Ybañez and Agnes Rosero:")
print("=" * 50)

# Search for Jaw Ybañez
jaw_users = df[df['name'].str.contains('Jaw', case=False, na=False)]
print(f"\nJaw Ybañez search results ({len(jaw_users)} found):")
for _, user in jaw_users.iterrows():
    print(f"  Name: {user['name']}")
    print(f"  Email: {user['email']}")
    print(f"  User ID: {user['id_y']}")
    print(f"  Accountability Buddies: {user['accountabilityBuddies']}")
    print(f"  Has Accountability Buddies: {user['hasAccountabilityBuddies']}")
    print(f"  Temporary Team Name: {user['temporaryTeamName']}")
    print()

# Search for Agnes Rosero
agnes_users = df[df['name'].str.contains('Agnes', case=False, na=False)]
print(f"\nAgnes Rosero search results ({len(agnes_users)} found):")
for _, user in agnes_users.iterrows():
    print(f"  Name: {user['name']}")
    print(f"  Email: {user['email']}")
    print(f"  User ID: {user['id_y']}")
    print(f"  Accountability Buddies: {user['accountabilityBuddies']}")
    print(f"  Has Accountability Buddies: {user['hasAccountabilityBuddies']}")
    print(f"  Temporary Team Name: {user['temporaryTeamName']}")
    print()

# Also search for "Rosero" to catch variations
rosero_users = df[df['name'].str.contains('Rosero', case=False, na=False)]
if len(rosero_users) > 0:
    print(f"\nRosero search results ({len(rosero_users)} found):")
    for _, user in rosero_users.iterrows():
        print(f"  Name: {user['name']}")
        print(f"  Email: {user['email']}")
        print(f"  User ID: {user['id_y']}")
        print(f"  Accountability Buddies: {user['accountabilityBuddies']}")
        print(f"  Has Accountability Buddies: {user['hasAccountabilityBuddies']}")
        print(f"  Temporary Team Name: {user['temporaryTeamName']}")
        print()

# Search for "Ybañez" to catch variations
ybanez_users = df[df['name'].str.contains('Ybañez', case=False, na=False)]
if len(ybanez_users) > 0:
    print(f"\nYbañez search results ({len(ybanez_users)} found):")
    for _, user in ybanez_users.iterrows():
        print(f"  Name: {user['name']}")
        print(f"  Email: {user['email']}")
        print(f"  User ID: {user['id_y']}")
        print(f"  Accountability Buddies: {user['accountabilityBuddies']}")
        print(f"  Has Accountability Buddies: {user['hasAccountabilityBuddies']}")
        print(f"  Temporary Team Name: {user['temporaryTeamName']}")
        print() 