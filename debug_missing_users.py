import pandas as pd
from collections import defaultdict

# File paths
INPUT_FILE = 'sample_merged_data.xlsx'
OUTPUT_FILE = 'grouped_participants.xlsx'

# Column mapping for merged data (will be dynamically determined)
EXPECTED_COLUMNS = {
    'user_id': ['user_id', 'id', 'userid', 'user id', 'id_y', 'id_x'],
    'name': ['name', 'full_name', 'fullname', 'first_name', 'last_name', 'firstName', 'lastName'],
    'gender_identity': ['gender_identity', 'gender', 'genderidentity', 'genderIdentity'],
    'sex': ['sex', 'biological_sex', 'biologicalsex'],
    'residing_ph': ['residing_ph', 'residing_in_philippines', 'philippines_resident', 'lingInPhilippineExperience', 'residingInPhilippines'],
    'gender_preference': ['gender_preference', 'grouping_preference', 'preference', 'genderPref', 'groupGenderPreference'],
    'country': ['country', 'nationality'],
    'province': ['province', 'state_province'],
    'city': ['city', 'municipality'],
    'state': ['state', 'region', 'stat'],
    'go_solo': ['go_solo', 'solo', 'prefer_solo', 'goSolo'],
    'joining_as_student': ['joining_as_student', 'joiningAsStudent', 'student', 'is_student'],
    'kaizen_client_type': ['kaizen_client_type', 'kaizenClientType', 'client_type', 'clientType'],
    'accountability_buddies': ['accountability_buddies', 'accountabilityBuddies', 'accountability_buddies', 'buddies'],
    'has_accountability_buddies': ['has_accountability_buddies', 'hasAccountabilityBuddies', 'has_buddies'],
    'email': ['email', 'user_email', 'email_address', 'useremail', 'userEmail'],
    'temporary_team_name': ['temporaryTeamName', 'temporary_team_name', 'temp_team_name', 'team_name'],
    'previous_coach_name': ['previousCoachName', 'previous_coach_name', 'prev_coach_name', 'coach_name']
}

def find_column_mapping(df):
    """Dynamically find column mapping based on available columns"""
    mapping = {}
    available_columns = [col.lower() for col in df.columns]
    
    for expected_key, possible_names in EXPECTED_COLUMNS.items():
        found = False
        for possible_name in possible_names:
            if possible_name.lower() in available_columns:
                # Find the exact column name (case-insensitive match)
                for col in df.columns:
                    if col.lower() == possible_name.lower():
                        mapping[expected_key] = col
                        found = True
                        break
                if found:
                    break
        
        if not found:
            mapping[expected_key] = None
    
    return mapping

def get_value(row, key, default=''):
    """Helper function to get value safely"""
    if key in row:
        return row[key]
    return default

def analyze_missing_users():
    """Analyze why users might be missing from the grouping process"""
    
    # Read the input file
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name='Merged Data')
        print(f"✅ Successfully read input file with {len(df)} records")
    except Exception as e:
        try:
            df = pd.read_csv(INPUT_FILE)
            print(f"✅ Successfully read CSV file with {len(df)} records")
        except Exception as e2:
            print(f"❌ Error reading input file: {e2}")
            return
    
    # Find column mapping
    column_mapping = find_column_mapping(df)
    print(f"\n📋 Column mapping found:")
    for key, value in column_mapping.items():
        if value:
            print(f"  ✅ {key}: {value}")
        else:
            print(f"  ❌ {key}: NOT FOUND")
    
    # Convert to list of dictionaries
    data = df.to_dict('records')
    original_count = len(data)
    print(f"\n📊 Original data count: {original_count}")
    
    # Track users through each filtering step
    user_tracking = {}
    
    # Initialize tracking for all users
    for i, row in enumerate(data):
        user_id = get_value(row, column_mapping.get('user_id', ''), f'Row_{i}')
        email = get_value(row, column_mapping.get('email', ''), '')
        user_tracking[user_id] = {
            'email': email,
            'status': 'original',
            'reason': 'Initial data',
            'row_data': row
        }
    
    # Step 1: Check joining_as_student filtering
    if column_mapping.get('joining_as_student'):
        joining_col = column_mapping['joining_as_student']
        excluded_count = 0
        for row in data:
            user_id = get_value(row, column_mapping.get('user_id', ''), 'Unknown')
            joining_value = get_value(row, joining_col, 'True')
            joining_str = str(joining_value).strip().lower()
            
            if joining_str in ['false', '0', '0.0', 'no']:
                if user_id in user_tracking:
                    user_tracking[user_id]['status'] = 'excluded'
                    user_tracking[user_id]['reason'] = f'joiningAsStudent = {joining_value}'
                excluded_count += 1
        
        print(f"\n🔍 Step 1 - joiningAsStudent filtering:")
        print(f"  Excluded users: {excluded_count}")
        print(f"  Remaining users: {original_count - excluded_count}")
    
    # Step 2: Check accountability buddies processing
    accountability_users = set()
    team_name_users = set()
    
    if column_mapping.get('has_accountability_buddies') and column_mapping.get('accountability_buddies'):
        for row in data:
            user_id = get_value(row, column_mapping.get('user_id', ''), 'Unknown')
            has_buddies = get_value(row, column_mapping.get('has_accountability_buddies', ''), '0')
            buddies_data = get_value(row, column_mapping.get('accountability_buddies', ''), '')
            
            # Check if has_accountability_buddies is True/1
            has_buddies_bool = str(has_buddies).strip().lower() in ['1', '1.0', 'true', 'yes']
            
            # Check if accountability_buddies field has valid data
            has_buddy_data = buddies_data and str(buddies_data).strip() not in ['', 'None', 'nan', '[None]', '[None, None]', "{'1': None}"]
            
            if has_buddies_bool and has_buddy_data:
                accountability_users.add(user_id)
                if user_id in user_tracking:
                    user_tracking[user_id]['status'] = 'accountability_buddies'
                    user_tracking[user_id]['reason'] = 'Has accountability buddies'
    
    # Check team names
    if column_mapping.get('temporary_team_name'):
        for row in data:
            user_id = get_value(row, column_mapping.get('user_id', ''), 'Unknown')
            team_name = get_value(row, column_mapping.get('temporary_team_name', ''), '')
            
            has_team_name = team_name and str(team_name).strip() not in ['', 'None', 'nan']
            
            if has_team_name and user_id not in accountability_users:
                team_name_users.add(user_id)
                if user_id in user_tracking:
                    user_tracking[user_id]['status'] = 'team_name'
                    user_tracking[user_id]['reason'] = f'Has team name: {team_name}'
    
    print(f"\n🔍 Step 2 - Special grouping:")
    print(f"  Accountability buddies users: {len(accountability_users)}")
    print(f"  Team name users: {len(team_name_users)}")
    
    # Step 3: Check solo participants
    solo_users = set()
    if column_mapping.get('go_solo'):
        for row in data:
            user_id = get_value(row, column_mapping.get('user_id', ''), 'Unknown')
            go_solo_value = str(get_value(row, column_mapping.get('go_solo', ''), '0')).strip()
            
            if go_solo_value.lower() in ['1', '1.0', 'true']:
                solo_users.add(user_id)
                if user_id in user_tracking:
                    user_tracking[user_id]['status'] = 'solo'
                    user_tracking[user_id]['reason'] = 'go_solo = True'
    
    print(f"\n🔍 Step 3 - Solo participants:")
    print(f"  Solo users: {len(solo_users)}")
    
    # Step 4: Check regular grouping
    regular_users = set()
    for user_id, info in user_tracking.items():
        if info['status'] == 'original':
            regular_users.add(user_id)
            info['status'] = 'regular_grouping'
            info['reason'] = 'Regular grouping (non-solo, no special requests)'
    
    print(f"\n🔍 Step 4 - Regular grouping:")
    print(f"  Regular grouping users: {len(regular_users)}")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"  Total original users: {original_count}")
    print(f"  Excluded (joiningAsStudent=False): {len([u for u in user_tracking.values() if u['status'] == 'excluded'])}")
    print(f"  Accountability buddies: {len([u for u in user_tracking.values() if u['status'] == 'accountability_buddies'])}")
    print(f"  Team name groups: {len([u for u in user_tracking.values() if u['status'] == 'team_name'])}")
    print(f"  Solo participants: {len([u for u in user_tracking.values() if u['status'] == 'solo'])}")
    print(f"  Regular grouping: {len([u for u in user_tracking.values() if u['status'] == 'regular_grouping'])}")
    
    # Check for any unaccounted users
    total_accounted = (
        len([u for u in user_tracking.values() if u['status'] == 'excluded']) +
        len([u for u in user_tracking.values() if u['status'] == 'accountability_buddies']) +
        len([u for u in user_tracking.values() if u['status'] == 'team_name']) +
        len([u for u in user_tracking.values() if u['status'] == 'solo']) +
        len([u for u in user_tracking.values() if u['status'] == 'regular_grouping'])
    )
    
    print(f"  Total accounted for: {total_accounted}")
    print(f"  Missing/Unaccounted: {original_count - total_accounted}")
    
    # Show details for each category
    print(f"\n📋 DETAILED BREAKDOWN:")
    
    for status in ['excluded', 'accountability_buddies', 'team_name', 'solo', 'regular_grouping']:
        users_in_status = [u for u in user_tracking.values() if u['status'] == status]
        if users_in_status:
            print(f"\n  {status.upper()} ({len(users_in_status)} users):")
            for user in users_in_status[:5]:  # Show first 5
                user_id = next(k for k, v in user_tracking.items() if v == user)
                print(f"    - {user_id}: {user['reason']}")
            if len(users_in_status) > 5:
                print(f"    ... and {len(users_in_status) - 5} more")
    
    # Check for potential issues
    print(f"\n🔍 POTENTIAL ISSUES:")
    
    # Check for users without emails
    users_without_email = [u for u in user_tracking.values() if not u['email'] or '@' not in u['email']]
    if users_without_email:
        print(f"  ⚠️  Users without valid emails: {len(users_without_email)}")
        for user in users_without_email[:3]:
            user_id = next(k for k, v in user_tracking.items() if v == user)
            print(f"    - {user_id}: email = '{user['email']}'")
    
    # Check for users with missing critical data
    critical_columns = ['gender_identity', 'gender_preference', 'residing_ph']
    for col in critical_columns:
        if column_mapping.get(col):
            missing_data = []
            for row in data:
                user_id = get_value(row, column_mapping.get('user_id', ''), 'Unknown')
                value = get_value(row, column_mapping.get(col, ''), '')
                if not value or str(value).strip() in ['', 'None', 'nan']:
                    missing_data.append(user_id)
            
            if missing_data:
                print(f"  ⚠️  Users with missing {col}: {len(missing_data)}")
                print(f"    Examples: {missing_data[:3]}")

if __name__ == "__main__":
    analyze_missing_users() 