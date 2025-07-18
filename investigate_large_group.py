import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import find_column_mapping, extract_emails_from_accountability_buddies, normalize_email, create_email_mapping

def investigate_large_group():
    """Investigate the large group with 16 members"""
    
    print("🔍 INVESTIGATING LARGE GROUP WITH 16 MEMBERS")
    print("=" * 60)
    
    # Read the input Excel file
    INPUT_FILE = 'merged_users_grouping_preferences_20250719_004359.xlsx'
    
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name='Merged Data')
        print(f"✅ Successfully read input file with {len(df)} records")
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        return
    
    # Find column mapping
    column_mapping = find_column_mapping(df)
    
    # Convert DataFrame to list of dictionaries
    data = df.to_dict('records')
    
    # Helper function to get value safely
    def get_value(row, key, default=''):
        if column_mapping and key in column_mapping:
            if isinstance(row, dict):
                return row.get(column_mapping[key], default)
            else:
                return default
        else:
            return default
    
    # Create email mapping
    email_mapping = create_email_mapping(data, column_mapping)
    
    # Find the users in the first group (based on the output we saw)
    first_group_users = [
        ('265', 'Norie Anne Pitallar'),
        ('856', 'kurly de guzman'),
        ('1178', 'Rachel Jamiro'),
        ('2076', 'Retchielda Pascual'),
        ('132', 'Ma. Virginia Del Rosario'),
        ('2283', 'Leah Marie M. Reyes'),
        ('1869', 'Crystal Eunice Dela Cruz')
    ]
    
    print(f"📋 ANALYZING FIRST GROUP USERS:")
    
    # Find these users in the data and analyze their accountability buddy relationships
    found_users = []
    for user_id, name in first_group_users:
        for row in data:
            if str(get_value(row, 'user_id', '')).strip() == user_id:
                found_users.append(row)
                break
    
    print(f"  Found {len(found_users)} users from the first group")
    
    # Analyze their accountability buddy relationships
    print(f"\n🔍 ACCOUNTABILITY BUDDY RELATIONSHIPS:")
    
    all_referenced_emails = set()
    user_relationships = {}
    
    for row in found_users:
        user_id = get_value(row, 'user_id', '')
        name = get_value(row, 'name', '')
        email = normalize_email(get_value(row, 'email', ''), email_mapping)
        accountability_buddies = get_value(row, 'accountability_buddies', '')
        has_accountability_buddies = get_value(row, 'has_accountability_buddies', '')
        
        print(f"\n  User {user_id} ({name}):")
        print(f"    Email: {email}")
        print(f"    Has Accountability Buddies: {has_accountability_buddies}")
        print(f"    Accountability Buddies: {accountability_buddies}")
        
        if accountability_buddies:
            emails = extract_emails_from_accountability_buddies(accountability_buddies, email_mapping)
            all_referenced_emails.update(emails)
            user_relationships[email] = emails
            print(f"    Extracted emails: {emails}")
    
    print(f"\n📊 SUMMARY OF RELATIONSHIPS:")
    print(f"  Total unique emails referenced: {len(all_referenced_emails)}")
    print(f"  All referenced emails: {sorted(all_referenced_emails)}")
    
    # Check if any of these referenced emails are in our found users
    found_emails = [normalize_email(get_value(user, 'email', ''), email_mapping) for user in found_users]
    print(f"  Emails of found users: {found_emails}")
    
    # Check which referenced emails are in our data
    referenced_in_data = []
    for email in all_referenced_emails:
        for row in data:
            row_email = normalize_email(get_value(row, 'email', ''), email_mapping)
            if row_email == email:
                referenced_in_data.append((email, get_value(row, 'name', ''), get_value(row, 'user_id', '')))
                break
    
    print(f"\n🔍 REFERENCED EMAILS IN DATA:")
    for email, name, user_id in referenced_in_data:
        print(f"  {email}: {name} (ID: {user_id})")
    
    # Check if there are more users that should be in this group
    print(f"\n🔍 POTENTIAL ADDITIONAL GROUP MEMBERS:")
    additional_members = []
    for email, name, user_id in referenced_in_data:
        if email not in found_emails:
            additional_members.append((email, name, user_id))
            print(f"  {email}: {name} (ID: {user_id}) - NOT in found users")
    
    print(f"\n📊 GROUP SIZE ANALYSIS:")
    print(f"  Found users: {len(found_users)}")
    print(f"  Additional members: {len(additional_members)}")
    print(f"  Total potential group size: {len(found_users) + len(additional_members)}")
    
    if len(found_users) + len(additional_members) == 16:
        print(f"  ✅ This matches the expected group size of 16!")
    else:
        print(f"  ❌ This doesn't match the expected group size of 16")

if __name__ == "__main__":
    investigate_large_group() 