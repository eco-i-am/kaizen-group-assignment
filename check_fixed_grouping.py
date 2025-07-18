import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import group_participants, find_column_mapping

# Read the fixed Excel file
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414_fixed.xlsx', sheet_name='Merged Data')

# Find column mapping
column_mapping = find_column_mapping(df)

# Convert DataFrame to list of dictionaries
data = df.to_dict('records')

# Group participants
solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)

print("Checking if Jaw Ybañez is now grouped with Agnes Rosero:")
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
else:
    print("  ❌ Not found in data")

print(f"\nAgnes Rosero:")
if agnes_user:
    print(f"  Name: {agnes_user.get(column_mapping.get('name'), 'N/A')}")
    print(f"  Email: {agnes_user.get(column_mapping.get('email'), 'N/A')}")
    print(f"  User ID: {agnes_user.get(column_mapping.get('user_id'), 'N/A')}")
    print(f"  Accountability Buddies: {agnes_user.get(column_mapping.get('accountability_buddies'), 'N/A')}")
else:
    print("  ❌ Not found in data")

# Check where they are currently grouped
print(f"\n" + "="*60)
print("CURRENT GROUPING STATUS AFTER FIX:")
print("="*60)

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
            jaw_group = i
        if agnes_in_group:
            print(f"  ✅ Agnes Rosero is in this group")
            agnes_found = True
            agnes_group = i

# Check if they are in the same group
if jaw_found and agnes_found and jaw_group == agnes_group:
    print(f"\n🎉 SUCCESS! Jaw Ybañez and Agnes Rosero are now in the same group!")
    print(f"   They are both in Requested Group {jaw_group + 1}")
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
print(f"\n" + "="*60)
print("CHECKING EXCEL OUTPUT:")
print("="*60)

try:
    excel_df = pd.read_excel('grouped_participants_fixed.xlsx')
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