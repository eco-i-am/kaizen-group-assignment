import pandas as pd
from collections import defaultdict

def test_requested_groups_logic():
    """Test the requested groups logic with sample data"""
    
    # Create sample data
    sample_data = [
        {
            'user_id': '1',
            'name': 'Alice',
            'email': 'alice@example.com',
            'has_accountability_buddies': '1',
            'accountability_buddies': "['bob@example.com', 'charlie@example.com']"
        },
        {
            'user_id': '2',
            'name': 'Bob',
            'email': 'bob@example.com',
            'has_accountability_buddies': '0',
            'accountability_buddies': ''
        },
        {
            'user_id': '3',
            'name': 'Charlie',
            'email': 'charlie@example.com',
            'has_accountability_buddies': '0',
            'accountability_buddies': ''
        },
        {
            'user_id': '4',
            'name': 'David',
            'email': 'david@example.com',
            'has_accountability_buddies': '1',
            'accountability_buddies': "['eve@example.com', 'frank@example.com']"
        },
        {
            'user_id': '5',
            'name': 'Eve',
            'email': 'eve@example.com',
            'has_accountability_buddies': '0',
            'accountability_buddies': ''
        },
        {
            'user_id': '6',
            'name': 'Frank',
            'email': 'frank@example.com',
            'has_accountability_buddies': '0',
            'accountability_buddies': ''
        }
    ]
    
    # Column mapping for the sample data
    column_mapping = {
        'user_id': 'user_id',
        'name': 'name',
        'email': 'email',
        'has_accountability_buddies': 'has_accountability_buddies',
        'accountability_buddies': 'accountability_buddies'
    }
    
    def get_value(row, key, default=''):
        if key in column_mapping:
            return row.get(column_mapping[key], default)
        return default
    
    # Test the logic
    print("Testing requested groups logic with sample data:")
    print("=" * 50)
    
    # 1. Find participants with accountability buddies
    accountability_participants = []
    for row in sample_data:
        accountability_buddies = get_value(row, 'accountability_buddies', '')
        has_accountability_buddies = get_value(row, 'has_accountability_buddies', '0')
        user_id = get_value(row, 'user_id', 'Unknown')
        
        has_buddies = str(has_accountability_buddies).strip().lower() in ['1', '1.0', 'true', 'yes']
        has_buddy_data = accountability_buddies and str(accountability_buddies).strip() not in ['', 'None', 'nan', '[None]', '[None, None]', "{'1': None}"]
        
        if has_buddies and has_buddy_data:
            accountability_participants.append(row)
            print(f"User {user_id}: has_accountability_buddies={has_accountability_buddies}, accountability_buddies='{accountability_buddies}'")
    
    print(f"\nFound {len(accountability_participants)} participants with accountability buddies")
    
    # 2. Create email mapping
    email_to_user = {}
    for row in sample_data:
        email = get_value(row, 'email', '')
        if email and '@' in email:
            email_to_user[email.lower().strip()] = row
            user_id = get_value(row, 'user_id', 'Unknown')
            print(f"User {user_id}: email = {email}")
    
    print(f"Created email mapping for {len(email_to_user)} users")
    
    # 3. Process requested groups
    requested_groups = []
    processed_requests = set()
    
    for participant in accountability_participants:
        accountability_buddies = get_value(participant, 'accountability_buddies', '')
        user_id = get_value(participant, 'user_id', 'Unknown')
        
        if isinstance(accountability_buddies, str):
            cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
            requested_emails = [email.strip().lower() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
            
            if requested_emails:
                request_key = ','.join(sorted(requested_emails))
                
                if request_key not in processed_requests:
                    processed_requests.add(request_key)
                    
                    group_members = [participant]
                    found_buddies = []
                    missing_buddies = []
                    
                    for email in requested_emails:
                        if email in email_to_user:
                            buddy_user = email_to_user[email]
                            group_members.append(buddy_user)
                            found_buddies.append(email)
                            buddy_user_id = get_value(buddy_user, 'user_id', 'Unknown')
                            print(f"  Found buddy {email} -> User {buddy_user_id}")
                        else:
                            missing_buddies.append(email)
                            print(f"  Missing buddy: {email}")
                    
                    if group_members:
                        requested_groups.append(group_members)
                        print(f"\nCreated Requested Group with {len(group_members)} members:")
                        print(f"  Requester: User {user_id}")
                        print(f"  Requested emails: {requested_emails}")
                        print(f"  Found buddies: {found_buddies}")
                        if missing_buddies:
                            print(f"  Missing buddies: {missing_buddies}")
                        
                        # Show group members
                        print("  Group members:")
                        for member in group_members:
                            member_id = get_value(member, 'user_id', 'Unknown')
                            member_name = get_value(member, 'name', 'Unknown')
                            member_email = get_value(member, 'email', 'Unknown')
                            print(f"    - User {member_id}: {member_name} ({member_email})")
    
    print(f"\nFinal result: Created {len(requested_groups)} requested groups")
    
    return requested_groups

if __name__ == "__main__":
    test_requested_groups_logic() 