import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import group_participants, find_column_mapping

# Read the merged Excel file
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx', sheet_name='Merged Data')

# Find column mapping
column_mapping = find_column_mapping(df)

# Convert DataFrame to list of dictionaries
data = df.to_dict('records')

# Group participants
solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)

print("Checking current grouping for Jaw Ybañez and Agnes Rosero:")
print("=" * 60)

# Find Jaw Ybañez and Agnes Rosero in the data
jaw_user = None
agnes_user = None

for user in data:
    email = user.get(column_mapping.get('email'), '')
    name = user.get(column_mapping.get('name'), '')
    
    if email == 'yo21st@gmail.com' or name == 'Jaw Ybañez':
        jaw_user = user
    elif email == 'agnes.rosero@gmail.com' or name == 'Agnes Rosero':
        agnes_user = user

print(f"\nJaw Ybañez:")
if jaw_user:
    print(f"  Name: {jaw_user.get(column_mapping.get('name'), 'N/A')}")
    print(f"  Email: {jaw_user.get(column_mapping.get('email'), 'N/A')}")
    print(f"  User ID: {jaw_user.get(column_mapping.get('user_id'), 'N/A')}")
    print(f"  Accountability Buddies: {jaw_user.get(column_mapping.get('accountability_buddies'), 'N/A')}")
    print(f"  Has Accountability Buddies: {jaw_user.get(column_mapping.get('has_accountability_buddies'), 'N/A')}")
    print(f"  Temporary Team Name: {jaw_user.get(column_mapping.get('temporary_team_name'), 'N/A')}")
else:
    print("  ❌ Not found in data")

print(f"\nAgnes Rosero:")
if agnes_user:
    print(f"  Name: {agnes_user.get(column_mapping.get('name'), 'N/A')}")
    print(f"  Email: {agnes_user.get(column_mapping.get('email'), 'N/A')}")
    print(f"  User ID: {agnes_user.get(column_mapping.get('user_id'), 'N/A')}")
    print(f"  Accountability Buddies: {agnes_user.get(column_mapping.get('accountability_buddies'), 'N/A')}")
    print(f"  Has Accountability Buddies: {agnes_user.get(column_mapping.get('has_accountability_buddies'), 'N/A')}")
    print(f"  Temporary Team Name: {agnes_user.get(column_mapping.get('temporary_team_name'), 'N/A')}")
else:
    print("  ❌ Not found in data")

# Check where they are currently grouped
print(f"\n" + "="*60)
print("CURRENT GROUPING STATUS:")
print("="*60)

# Check in requested groups
jaw_found = False
agnes_found = False

for i, group in enumerate(requested_groups):
    group_emails = []
    group_names = []
    for member in group:
        member_email = member.get(column_mapping.get('email'), '')
        member_name = member.get(column_mapping.get('name'), '')
        if member_email:
            group_emails.append(member_email.lower().strip())
        if member_name:
            group_names.append(member_name)
    
    jaw_in_group = 'yo21st@gmail.com' in group_emails or 'Jaw Ybañez' in group_names
    agnes_in_group = 'agnes.rosero@gmail.com' in group_emails or 'Agnes Rosero' in group_names
    
    if jaw_in_group or agnes_in_group:
        print(f"\nRequested Group {i+1}:")
        print(f"  Members: {group_names}")
        print(f"  Emails: {group_emails}")
        if jaw_in_group:
            print(f"  ✅ Jaw Ybañez is in this group")
            jaw_found = True
        if agnes_in_group:
            print(f"  ✅ Agnes Rosero is in this group")
            agnes_found = True

# Check in regular groups
for group_name, members in grouped.items():
    group_emails = []
    group_names = []
    for member in members:
        member_email = member.get(column_mapping.get('email'), '')
        member_name = member.get(column_mapping.get('name'), '')
        if member_email:
            group_emails.append(member_email.lower().strip())
        if member_name:
            group_names.append(member_name)
    
    jaw_in_group = 'yo21st@gmail.com' in group_emails or 'Jaw Ybañez' in group_names
    agnes_in_group = 'agnes.rosero@gmail.com' in group_emails or 'Agnes Rosero' in group_names
    
    if jaw_in_group or agnes_in_group:
        print(f"\nRegular Group: {group_name}")
        print(f"  Members: {group_names}")
        print(f"  Emails: {group_emails}")
        if jaw_in_group:
            print(f"  ✅ Jaw Ybañez is in this group")
            jaw_found = True
        if agnes_in_group:
            print(f"  ✅ Agnes Rosero is in this group")
            agnes_found = True

# Check in solo groups
for i, group in enumerate(solo_groups):
    group_emails = []
    group_names = []
    for member in group:
        member_email = member.get(column_mapping.get('email'), '')
        member_name = member.get(column_mapping.get('name'), '')
        if member_email:
            group_emails.append(member_email.lower().strip())
        if member_name:
            group_names.append(member_name)
    
    jaw_in_group = 'yo21st@gmail.com' in group_emails or 'Jaw Ybañez' in group_names
    agnes_in_group = 'agnes.rosero@gmail.com' in group_emails or 'Agnes Rosero' in group_names
    
    if jaw_in_group or agnes_in_group:
        print(f"\nSolo Group {i+1}:")
        print(f"  Members: {group_names}")
        print(f"  Emails: {group_emails}")
        if jaw_in_group:
            print(f"  ✅ Jaw Ybañez is in this group")
            jaw_found = True
        if agnes_in_group:
            print(f"  ✅ Agnes Rosero is in this group")
            agnes_found = True

if not jaw_found:
    print(f"\n❌ Jaw Ybañez not found in any group")
if not agnes_found:
    print(f"\n❌ Agnes Rosero not found in any group")

print(f"\n" + "="*60)
print("EMAIL MISMATCH ANALYSIS:")
print("="*60)
print("Jaw Ybañez's email: yo21st@gmail.com")
print("Agnes Rosero's accountability buddies contains: jaw.ybanez@yahoo.com")
print("This email mismatch is preventing them from being grouped together!") 