import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import group_participants, find_column_mapping, create_email_mapping

# Read the new Excel file
print("🔍 INVESTIGATING MISSING USERS IN NEW DATA FILE")
print("=" * 60)

df = pd.read_excel('merged_users_grouping_preferences_20250718_221747.xlsx', sheet_name='Merged Data')
print(f"✅ Successfully read input file with {len(df)} records")

# Find column mapping
column_mapping = find_column_mapping(df)
print(f"\n📋 Column mapping found:")
for key, value in column_mapping.items():
    if value:
        print(f"  ✅ {key}: {value}")
    else:
        print(f"  ❌ {key}: NOT FOUND")

# Convert DataFrame to list of dictionaries
data = df.to_dict('records')

# Create email mapping
email_mapping = create_email_mapping(data, column_mapping)
print(f"\n🔗 Email mappings created: {len(email_mapping)}")

# Group participants
print(f"\n🚀 Starting group assignment process...")
solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)

# Collect all users from different sources
print(f"\n📊 ANALYZING USER DISTRIBUTION")
print("=" * 60)

# Count users in each category
solo_count = sum(len(group) for group in solo_groups)
regular_count = sum(len(members) for members in grouped.values())
requested_count = sum(len(group) for group in requested_groups)
excluded_count = len(excluded_users)

print(f"Input users: {len(data)}")
print(f"Solo users: {solo_count}")
print(f"Regular group users: {regular_count}")
print(f"Requested group users: {requested_count}")
print(f"Excluded users: {excluded_count}")

total_output = solo_count + regular_count + requested_count + excluded_count
missing_count = len(data) - total_output

print(f"Total output users: {total_output}")
print(f"Missing users: {missing_count}")

if missing_count > 0:
    print(f"\n❌ MISSING USERS DETECTED: {missing_count}")
    print("=" * 60)
    
    # Find which users are missing
    all_output_user_ids = set()
    
    # Collect from solo groups
    for group in solo_groups:
        for member in group:
            user_id = member.get(column_mapping.get('user_id'), 'Unknown')
            if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
                all_output_user_ids.add(str(user_id).strip())
    
    # Collect from regular groups
    for group_name, members in grouped.items():
        for member in members:
            user_id = member.get(column_mapping.get('user_id'), 'Unknown')
            if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
                all_output_user_ids.add(str(user_id).strip())
    
    # Collect from requested groups
    for group in requested_groups:
        for member in group:
            user_id = member.get(column_mapping.get('user_id'), 'Unknown')
            if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
                all_output_user_ids.add(str(user_id).strip())
    
    # Collect from excluded users
    for user in excluded_users:
        user_id = user.get(column_mapping.get('user_id'), 'Unknown')
        if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
            all_output_user_ids.add(str(user_id).strip())
    
    # Find missing users
    all_input_user_ids = set()
    for user in data:
        user_id = user.get(column_mapping.get('user_id'), 'Unknown')
        if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
            all_input_user_ids.add(str(user_id).strip())
    
    missing_user_ids = all_input_user_ids - all_output_user_ids
    
    print(f"\n🔍 MISSING USER ANALYSIS:")
    print(f"Input user IDs: {len(all_input_user_ids)}")
    print(f"Output user IDs: {len(all_output_user_ids)}")
    print(f"Missing user IDs: {len(missing_user_ids)}")
    
    if missing_user_ids:
        print(f"\n📋 FIRST 20 MISSING USERS:")
        missing_list = sorted(list(missing_user_ids), key=lambda x: int(x) if str(x).isdigit() else 999)
        for i, user_id in enumerate(missing_list[:20], 1):
            # Find the user data
            user_data = None
            for user in data:
                if str(user.get(column_mapping.get('user_id'), '')).strip() == user_id:
                    user_data = user
                    break
            
            if user_data:
                name = user_data.get(column_mapping.get('name'), 'Unknown')
                email = user_data.get(column_mapping.get('email'), 'No email')
                go_solo = user_data.get(column_mapping.get('go_solo'), 'Unknown')
                has_buddies = user_data.get(column_mapping.get('has_accountability_buddies'), 'Unknown')
                joining_student = user_data.get(column_mapping.get('joining_as_student'), 'Unknown')
                
                print(f"{i:2d}. User ID: {user_id}")
                print(f"    Name: {name}")
                print(f"    Email: {email}")
                print(f"    Go Solo: {go_solo}")
                print(f"    Has Buddies: {has_buddies}")
                print(f"    Joining as Student: {joining_student}")
                print()
        
        if len(missing_list) > 20:
            print(f"    ... and {len(missing_list) - 20} more missing users")
    
    # Check for potential issues
    print(f"\n🔍 POTENTIAL ISSUES:")
    
    # Check for users with missing critical data
    critical_columns = ['user_id', 'name', 'email']
    missing_critical_data = []
    
    for user in data:
        user_id = user.get(column_mapping.get('user_id'), '')
        if not user_id or str(user_id).strip() in ['', 'nan', 'None']:
            missing_critical_data.append(f"Missing user_id: {user}")
    
    if missing_critical_data:
        print(f"  ⚠️  Users with missing critical data: {len(missing_critical_data)}")
        print(f"    First few: {missing_critical_data[:3]}")
    
    # Check for duplicate user IDs
    user_ids = []
    for user in data:
        user_id = user.get(column_mapping.get('user_id'), '')
        if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
            user_ids.append(str(user_id).strip())
    
    duplicate_ids = [x for x in set(user_ids) if user_ids.count(x) > 1]
    if duplicate_ids:
        print(f"  ⚠️  Duplicate user IDs found: {len(duplicate_ids)}")
        print(f"    Examples: {duplicate_ids[:5]}")

else:
    print(f"\n✅ NO MISSING USERS - ALL ACCOUNTED FOR!")

print(f"\n" + "="*60)
print(f"🔍 END OF MISSING USERS INVESTIGATION")
print(f"="*60) 