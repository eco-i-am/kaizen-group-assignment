import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import create_email_mapping, find_column_mapping, check_name_similarity

# Read the data
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx', sheet_name='Merged Data')
column_mapping = find_column_mapping(df)
data = df.to_dict('records')

print("Testing email mapping logic:")
print("=" * 50)

# Test name similarity
jaw_name = "Jaw Ybañez"
agnes_name = "Agnes Rosero"

similarity = check_name_similarity(jaw_name, agnes_name)
print(f"Name similarity between '{jaw_name}' and '{agnes_name}': {similarity}")

# Test with different variations
test_names = [
    "Jaw Ybañez",
    "Jaw Ybanez", 
    "Jaw Ybañez",
    "Jaw",
    "Ybañez",
    "Agnes Rosero",
    "Agnes",
    "Rosero"
]

print(f"\nTesting name similarity with various combinations:")
for i, name1 in enumerate(test_names):
    for j, name2 in enumerate(test_names):
        if i != j:
            similarity = check_name_similarity(name1, name2)
            if similarity > 0.3:  # Show only meaningful similarities
                print(f"'{name1}' vs '{name2}': {similarity:.2f}")

# Test the email mapping creation
print(f"\n" + "="*50)
print("Testing email mapping creation:")
print("="*50)

email_mapping = create_email_mapping(data, column_mapping)

print(f"Email mapping created: {len(email_mapping)} mappings")
if email_mapping:
    for old_email, new_email in email_mapping.items():
        print(f"  {old_email} -> {new_email}")
else:
    print("No email mappings created")

# Check specific case
print(f"\n" + "="*50)
print("Checking specific case:")
print("="*50)

# Find Jaw and Agnes
jaw_user = None
agnes_user = None

for user in data:
    name = user.get(column_mapping.get('name'), '')
    email = user.get(column_mapping.get('email'), '')
    
    if name == 'Jaw Ybañez':
        jaw_user = user
    elif name == 'Agnes Rosero':
        agnes_user = user

if jaw_user:
    print(f"Jaw Ybañez:")
    print(f"  Email: {jaw_user.get(column_mapping.get('email'), 'N/A')}")
    print(f"  Accountability Buddies: {jaw_user.get(column_mapping.get('accountability_buddies'), 'N/A')}")

if agnes_user:
    print(f"\nAgnes Rosero:")
    print(f"  Email: {agnes_user.get(column_mapping.get('email'), 'N/A')}")
    print(f"  Accountability Buddies: {agnes_user.get(column_mapping.get('accountability_buddies'), 'N/A')}")

# Check if jaw.ybanez@yahoo.com exists in the data
print(f"\n" + "="*50)
print("Checking if jaw.ybanez@yahoo.com exists in data:")
print("="*50)

jaw_yahoo_found = False
for user in data:
    email = user.get(column_mapping.get('email'), '')
    if email and 'jaw.ybanez@yahoo.com' in email.lower():
        jaw_yahoo_found = True
        print(f"Found user with jaw.ybanez@yahoo.com:")
        print(f"  Name: {user.get(column_mapping.get('name'), 'N/A')}")
        print(f"  Email: {email}")

if not jaw_yahoo_found:
    print("jaw.ybanez@yahoo.com NOT found in data")

# Check all emails in accountability buddies
print(f"\n" + "="*50)
print("Checking all emails in accountability buddies:")
print("="*50)

all_buddy_emails = set()
for user in data:
    accountability_buddies = user.get(column_mapping.get('accountability_buddies'), '')
    if accountability_buddies:
        if isinstance(accountability_buddies, str):
            cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
            buddy_emails = [email.strip().lower() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
            all_buddy_emails.update(buddy_emails)

print(f"All emails in accountability buddies: {sorted(all_buddy_emails)}")

# Check which buddy emails don't exist in the main email column
print(f"\n" + "="*50)
print("Checking missing emails:")
print("="*50)

all_main_emails = set()
for user in data:
    email = user.get(column_mapping.get('email'), '')
    if email and '@' in email:
        all_main_emails.add(email.lower())

missing_emails = all_buddy_emails - all_main_emails
print(f"Emails in accountability buddies but not in main email column: {sorted(missing_emails)}") 