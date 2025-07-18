import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import group_participants, find_column_mapping, create_email_mapping, extract_emails_from_accountability_buddies

def investigate_gerard_issue():
    """Investigate the Gerard grouping issue"""
    
    print("🔍 INVESTIGATING GERARD GROUPING ISSUE")
    print("=" * 60)
    
    # Read the new Excel file
    INPUT_FILE = 'merged_users_grouping_preferences_20250719_004359.xlsx'
    
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name='Merged Data')
        print(f"✅ Successfully read input file with {len(df)} records")
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        return
    
    # Find column mapping
    column_mapping = find_column_mapping(df)
    print(f"\n📋 Column mapping found:")
    for key, value in column_mapping.items():
        if value:
            print(f"  ✅ {key}: {value}")
    
    # Convert DataFrame to list of dictionaries
    data = df.to_dict('records')
    
    # Create email mapping
    email_mapping = create_email_mapping(data, column_mapping)
    
    # Helper function to get value safely
    def get_value(row, key, default=''):
        if column_mapping and key in column_mapping:
            if isinstance(row, dict):
                return row.get(column_mapping[key], default)
            else:
                return default
        else:
            return default
    
    # Find Gerard (User ID 2123) with email gerarddy@gmail.com
    gerard_user = None
    gerard_email = None
    
    for row in data:
        user_id = get_value(row, 'user_id', '')
        email = get_value(row, 'email', '')
        name = get_value(row, 'name', '')
        
        if str(user_id).strip() == '2123' or email.lower() == 'gerarddy@gmail.com':
            gerard_user = row
            gerard_email = email
            print(f"\n🔍 FOUND GERARD:")
            print(f"  User ID: {user_id}")
            print(f"  Name: {name}")
            print(f"  Email: {email}")
            print(f"  Has Accountability Buddies: {get_value(row, 'has_accountability_buddies', '')}")
            print(f"  Accountability Buddies: {get_value(row, 'accountability_buddies', '')}")
            print(f"  Temporary Team Name: {get_value(row, 'temporary_team_name', '')}")
            print(f"  Go Solo: {get_value(row, 'go_solo', '')}")
            break
    
    if not gerard_user:
        print(f"\n❌ Gerard (User ID 2123) not found in data")
        return
    
    # Find the other users in the group (Morris Tan, Patricia Pal, John Micha)
    target_users = []
    target_emails = ['gerarddy@gmail.com']  # Add other emails if known
    
    print(f"\n🔍 LOOKING FOR GROUP MEMBERS:")
    
    for row in data:
        user_id = get_value(row, 'user_id', '')
        email = get_value(row, 'email', '')
        name = get_value(row, 'name', '')
        
        # Look for the specific users mentioned
        if (str(user_id).strip() in ['2360', '2539', '2817'] or 
            'morris tan' in name.lower() or 
            'patricia pal' in name.lower() or 
            'john micha' in name.lower()):
            
            target_users.append(row)
            target_emails.append(email)
            print(f"  User ID: {user_id}, Name: {name}, Email: {email}")
            print(f"    Has Accountability Buddies: {get_value(row, 'has_accountability_buddies', '')}")
            print(f"    Accountability Buddies: {get_value(row, 'accountability_buddies', '')}")
            print(f"    Temporary Team Name: {get_value(row, 'temporary_team_name', '')}")
    
    # Check if these users reference each other in accountability buddies
    print(f"\n🔍 CHECKING ACCOUNTABILITY BUDDY RELATIONSHIPS:")
    
    all_target_users = [gerard_user] + target_users
    
    for user in all_target_users:
        user_id = get_value(user, 'user_id', '')
        name = get_value(user, 'name', '')
        accountability_buddies = get_value(user, 'accountability_buddies', '')
        
        print(f"\n  {name} (ID: {user_id}):")
        if accountability_buddies:
            emails = extract_emails_from_accountability_buddies(accountability_buddies, email_mapping)
            print(f"    References: {emails}")
            
            # Check if any of these emails match our target group
            for email in emails:
                for target_user in all_target_users:
                    target_email = get_value(target_user, 'email', '')
                    if email.lower() == target_email.lower():
                        target_name = get_value(target_user, 'name', '')
                        print(f"    ✅ Matches: {target_name} ({target_email})")
        else:
            print(f"    No accountability buddies")
    
    # Run the grouping function to see what happens
    print(f"\n🚀 RUNNING GROUPING FUNCTION...")
    solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)
    
    # Find where Gerard ended up
    print(f"\n🔍 CHECKING WHERE GERARD ENDED UP:")
    gerard_found = False
    
    # Check solo groups
    for i, group in enumerate(solo_groups):
        for member in group:
            if get_value(member, 'user_id', '') == '2123':
                print(f"  ❌ Gerard found in Solo Group {i+1}")
                gerard_found = True
                break
    
    # Check requested groups
    for i, group in enumerate(requested_groups):
        for member in group:
            if get_value(member, 'user_id', '') == '2123':
                print(f"  ✅ Gerard found in Requested Group {i+1}")
                print(f"    Group members:")
                for j, group_member in enumerate(group):
                    member_id = get_value(group_member, 'user_id', '')
                    member_name = get_value(group_member, 'name', '')
                    member_email = get_value(group_member, 'email', '')
                    print(f"      {j+1}. {member_id} {member_name} ({member_email})")
                gerard_found = True
                break
    
    # Check regular groups
    for group_name, members in grouped.items():
        for member in members:
            if get_value(member, 'user_id', '') == '2123':
                print(f"  ❌ Gerard found in Regular Group: {group_name}")
                gerard_found = True
                break
    
    if not gerard_found:
        print(f"  ❌ Gerard not found in any group!")
    
    # Check where the other target users ended up
    print(f"\n🔍 CHECKING WHERE OTHER TARGET USERS ENDED UP:")
    for target_user in target_users:
        target_id = get_value(target_user, 'user_id', '')
        target_name = get_value(target_user, 'name', '')
        target_found = False
        
        # Check requested groups
        for i, group in enumerate(requested_groups):
            for member in group:
                if get_value(member, 'user_id', '') == target_id:
                    print(f"  {target_name} (ID: {target_id}) found in Requested Group {i+1}")
                    target_found = True
                    break
            if target_found:
                break
        
        if not target_found:
            print(f"  {target_name} (ID: {target_id}) not found in requested groups")

if __name__ == "__main__":
    investigate_gerard_issue() 