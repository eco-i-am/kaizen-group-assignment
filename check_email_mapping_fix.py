import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import group_participants, find_column_mapping, create_email_mapping

# Read the original Excel file (without modifications)
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx', sheet_name='Merged Data')

# Find column mapping
column_mapping = find_column_mapping(df)

# Convert DataFrame to list of dictionaries
data = df.to_dict('records')

# Create dynamic email mapping
email_mapping = create_email_mapping(data, column_mapping)

# Group participants
solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)

print("Checking if dynamic email mapping fix worked for Jaw Ybañez and Agnes Rosero:")
print("=" * 70)

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
    print(f"  Normalized Email: {email_mapping.get(jaw_user.get(column_mapping.get('email'), '').lower(), jaw_user.get(column_mapping.get('email'), '').lower())}")
    print(f"  Accountability Buddies: {jaw_user.get(column_mapping.get('accountability_buddies'), 'N/A')}")
else:
    print("  ❌ Not found in data")

print(f"\nAgnes Rosero:")
if agnes_user:
    print(f"  Name: {agnes_user.get(column_mapping.get('name'), 'N/A')}")
    print(f"  Email: {agnes_user.get(column_mapping.get('email'), 'N/A')}")
    print(f"  Normalized Email: {email_mapping.get(agnes_user.get(column_mapping.get('email'), '').lower(), agnes_user.get(column_mapping.get('email'), '').lower())}")
    print(f"  Accountability Buddies: {agnes_user.get(column_mapping.get('accountability_buddies'), 'N/A')}")
else:
    print("  ❌ Not found in data")

# Show the dynamic email mapping
print(f"\n" + "="*70)
print("DYNAMIC EMAIL MAPPING CREATED:")
print("="*70)
if email_mapping:
    print("Email mappings found:")
    for old_email, new_email in email_mapping.items():
        print(f"  {old_email} -> {new_email}")
else:
    print("No email mappings needed (no users with multiple emails found)")

# Check where they are currently grouped
print(f"\n" + "="*70)
print("CURRENT GROUPING STATUS WITH DYNAMIC EMAIL MAPPING:")
print("="*70)

# Check in requested groups
jaw_found = False
agnes_found = False
jaw_group = None
agnes_group = None

for i, group in enumerate(requested_groups):
    group_emails = []
    group_names = []
    for member in group:
        member_email = member.get(column_mapping.get('email'), '')
        member_name = member.get(column_mapping.get('name'), '')
        if member_email:
            normalized_email = email_mapping.get(member_email.lower(), member_email.lower())
            group_emails.append(normalized_email)
        if member_name:
            group_names.append(member_name)
    
    jaw_normalized = email_mapping.get('yo21st@gmail.com', 'yo21st@gmail.com')
    agnes_normalized = email_mapping.get('agnes.rosero@gmail.com', 'agnes.rosero@gmail.com')
    
    jaw_in_group = jaw_normalized in group_emails or 'Jaw Ybañez' in group_names
    agnes_in_group = agnes_normalized in group_emails or 'Agnes Rosero' in group_names
    
    if jaw_in_group or agnes_in_group:
        print(f"\nRequested Group {i+1}:")
        print(f"  Members: {group_names}")
        print(f"  Normalized Emails: {group_emails}")
        if jaw_in_group:
            print(f"  ✅ Jaw Ybañez is in this group")
            jaw_found = True
            jaw_group = i
        if agnes_in_group:
            print(f"  ✅ Agnes Rosero is in this group")
            agnes_found = True
            agnes_group = i

# Check if they are in the same group
if jaw_found and agnes_found and jaw_group == agnes_group:
    print(f"\n🎉 SUCCESS! Jaw Ybañez and Agnes Rosero are now in the same group!")
    print(f"   They are both in Requested Group {jaw_group + 1}")
    print(f"   The dynamic email mapping fix worked without hard-coding emails!")
else:
    print(f"\n❌ Jaw Ybañez and Agnes Rosero are still in different groups")
    if jaw_found and agnes_found:
        print(f"   Jaw Ybañez is in Requested Group {jaw_group + 1}")
        print(f"   Agnes Rosero is in Requested Group {agnes_group + 1}")

if not jaw_found:
    print(f"\n❌ Jaw Ybañez not found in any requested group")
if not agnes_found:
    print(f"\n❌ Agnes Rosero not found in any requested group")

# Also check the Excel output
print(f"\n" + "="*70)
print("CHECKING EXCEL OUTPUT:")
print("="*70)

try:
    excel_df = pd.read_excel('grouped_participants.xlsx')
    print(f"✅ Successfully read Excel output with {len(excel_df)} rows")
    
    # Look for both users in the Excel
    jaw_found_excel = False
    agnes_found_excel = False
    
    for idx, row in excel_df.iterrows():
        group_name = row['Group Name']
        
        # Check all name columns
        for i in range(1, 8):
            name_col = f'Name {i}'
            if name_col in excel_df.columns:
                name = row[name_col]
                if name == 'Jaw Ybañez':
                    print(f"  ✅ Jaw Ybañez found in row {idx+1}, {name_col}")
                    print(f"     Group: {group_name}")
                    jaw_found_excel = True
                elif name == 'Agnes Rosero':
                    print(f"  ✅ Agnes Rosero found in row {idx+1}, {name_col}")
                    print(f"     Group: {group_name}")
                    agnes_found_excel = True
    
    if jaw_found_excel and agnes_found_excel:
        print(f"\n✅ Both users found in Excel output")
    else:
        print(f"\n❌ One or both users missing from Excel output")
        
except Exception as e:
    print(f"❌ Error reading Excel output: {e}")

print(f"\n" + "="*70)
print("DYNAMIC EMAIL MAPPING SUMMARY:")
print("="*70)
print("The script now dynamically creates email mappings by:")
print("1. Scanning all users to find those with multiple email addresses")
print("2. Creating mappings from alternative emails to canonical emails")
print("3. Applying these mappings automatically during grouping")
print("4. No hard-coded email addresses required!")
print("5. Works for any user with multiple email variations") 