import pandas as pd
from collections import defaultdict
import sys
sys.path.append('.')

from group_assignment_to_excel import find_column_mapping, normalize_email, create_email_mapping, get_philippines_region

def group_participants_fixed(data, column_mapping):
    """Fixed version of group_participants that ensures no duplicate users"""
    
    solo_groups = []
    grouped = defaultdict(list)
    group_counter = 1
    
    # Create dynamic email mapping
    email_mapping = create_email_mapping(data, column_mapping)
    
    # User tracking for diagnostics
    user_tracking = {}
    original_count = len(data)
    
    # Helper function to get value safely
    def get_value(row, key, default=''):
        if column_mapping and key in column_mapping:
            if isinstance(row, dict):
                return row.get(column_mapping[key], default)
            else:
                return default
        else:
            return default
    
    # Initialize tracking for all users
    for i, row in enumerate(data):
        user_id = get_value(row, 'user_id', f'Row_{i}')
        user_id_str = str(user_id).strip() if user_id else f'Row_{i}'
        email = get_value(row, 'email', '')
        user_tracking[user_id_str] = {
            'email': email,
            'status': 'original',
            'reason': 'Initial data',
            'row_data': row
        }
    
    # Filter out participants where joiningAsStudent is False
    excluded_users = []
    if column_mapping and 'joining_as_student' in column_mapping:
        joining_col = column_mapping['joining_as_student']
        filtered_data = []
        excluded_count = 0
        for row in data:
            user_id = get_value(row, 'user_id', 'Unknown')
            joining_value = get_value(row, 'joining_as_student', 'True')
            joining_str = str(joining_value).strip().lower()
            if joining_str in ['false', '0', '0.0', 'no']:
                excluded_count += 1
                excluded_users.append(row)
                user_id_str = str(user_id).strip() if user_id else 'Unknown'
                if user_id_str in user_tracking:
                    user_tracking[user_id_str]['status'] = 'excluded'
                    user_tracking[user_id_str]['reason'] = f'joiningAsStudent = {joining_value}'
            else:
                filtered_data.append(row)
        data = filtered_data
    
    # Create email to user mapping
    email_to_user = {}
    for row in data:
        email = get_value(row, 'email', '')
        if email and '@' in email:
            normalized_email = normalize_email(email, email_mapping)
            email_to_user[normalized_email] = row
    
    # Track all assigned users to prevent duplicates
    assigned_users = set()
    requested_groups = []
    accountability_count = 0
    
    # Step 1: Process mutual buddy groups first
    mutual_buddy_groups = []
    processed_users = set()
    
    for row in data:
        participant_email = normalize_email(get_value(row, 'email', ''), email_mapping)
        
        if participant_email in processed_users or participant_email in assigned_users:
            continue
        
        # Find all users who want to be grouped together
        mutual_group = [row]
        processed_users.add(participant_email)
        
        # Get this user's buddies
        accountability_buddies = get_value(row, 'accountability_buddies', '')
        if isinstance(accountability_buddies, str):
            cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
            requested_emails = [normalize_email(email.strip(), email_mapping) for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
        else:
            requested_emails = []
        
        # Find buddies who also reference this user
        for email in requested_emails:
            if email in email_to_user:
                buddy_user = email_to_user[email]
                buddy_email = normalize_email(get_value(buddy_user, 'email', ''), email_mapping)
                
                if buddy_email not in processed_users and buddy_email not in assigned_users:
                    # Check if this buddy also references the original user
                    buddy_buddies = get_value(buddy_user, 'accountability_buddies', '')
                    if isinstance(buddy_buddies, str):
                        cleaned = buddy_buddies.strip('[]').replace('"', '').replace("'", '')
                        buddy_requested = [normalize_email(email.strip(), email_mapping) for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
                        if participant_email in buddy_requested:
                            mutual_group.append(buddy_user)
                            processed_users.add(buddy_email)
        
        if len(mutual_group) > 1:
            mutual_buddy_groups.append(mutual_group)
    
    # Process mutual buddy groups
    for mutual_group in mutual_buddy_groups:
        if len(mutual_group) > 1:
            requested_groups.append(mutual_group)
            accountability_count += len(mutual_group)
            
            # Mark all members as assigned
            for member in mutual_group:
                member_email = normalize_email(get_value(member, 'email', ''), email_mapping)
                assigned_users.add(member_email)
    
    # Step 2: Process remaining accountability participants
    remaining_accountability = []
    for row in data:
        participant_email = normalize_email(get_value(row, 'email', ''), email_mapping)
        
        if participant_email in assigned_users:
            continue
        
        # Check if user has accountability buddies
        has_accountability_buddies = get_value(row, 'has_accountability_buddies', '0')
        accountability_buddies = get_value(row, 'accountability_buddies', '')
        
        has_buddies = str(has_accountability_buddies).strip().lower() in ['1', '1.0', 'true', 'yes']
        has_buddy_data = False
        
        if accountability_buddies:
            accountability_str = str(accountability_buddies).strip()
            if accountability_str not in ['', 'None', 'nan', '[None]', '[None, None]', "{'1': None}"]:
                if isinstance(accountability_buddies, str):
                    cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
                    emails = [email.strip().lower() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
                    has_buddy_data = len(emails) > 0
                else:
                    has_buddy_data = True
        
        if has_buddies or has_buddy_data:
            remaining_accountability.append(row)
    
    # Process remaining accountability participants
    processed_requests = set()
    
    for participant in remaining_accountability:
        participant_email = normalize_email(get_value(participant, 'email', ''), email_mapping)
        
        if participant_email in assigned_users:
            continue
        
        accountability_buddies = get_value(participant, 'accountability_buddies', '')
        
        if isinstance(accountability_buddies, str):
            cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
            requested_emails = [normalize_email(email.strip(), email_mapping) for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
            
            if requested_emails:
                request_key = ','.join(sorted(requested_emails))
                
                if request_key not in processed_requests:
                    processed_requests.add(request_key)
                    
                    # Create group with available buddies
                    group_members = [participant]
                    assigned_users.add(participant_email)
                    
                    for email in requested_emails:
                        if email in email_to_user:
                            buddy_user = email_to_user[email]
                            buddy_email = normalize_email(get_value(buddy_user, 'email', ''), email_mapping)
                            
                            if buddy_email not in assigned_users:
                                group_members.append(buddy_user)
                                assigned_users.add(buddy_email)
                    
                    if group_members:
                        requested_groups.append(group_members)
                        accountability_count += len(group_members)
    
    # Step 3: Process team name participants
    team_name_participants = []
    for row in data:
        participant_email = normalize_email(get_value(row, 'email', ''), email_mapping)
        
        if participant_email in assigned_users:
            continue
        
        temporary_team_name = get_value(row, 'temporary_team_name', '')
        has_team_name = temporary_team_name and str(temporary_team_name).strip() not in ['', 'None', 'nan']
        
        if has_team_name:
            team_name_participants.append(row)
    
    # Group team name participants by team name
    if team_name_participants:
        team_groups = defaultdict(list)
        for participant in team_name_participants:
            participant_email = normalize_email(get_value(participant, 'email', ''), email_mapping)
            
            if participant_email in assigned_users:
                continue
            
            team_name = get_value(participant, 'temporary_team_name', '').strip()
            team_groups[team_name].append(participant)
        
        # Create requested groups for each team
        for team_name, team_members in team_groups.items():
            if team_members:
                # Create groups of up to 5 members from this team
                i = 0
                while i < len(team_members):
                    group_members = team_members[i:i+5]
                    
                    # Mark all members as assigned
                    for member in group_members:
                        member_email = normalize_email(get_value(member, 'email', ''), email_mapping)
                        assigned_users.add(member_email)
                    
                    requested_groups.append(group_members)
                    accountability_count += len(group_members)
                    i += 5
    
    # Step 4: Handle solo participants
    solo_count = 0
    for row in data:
        user_email = normalize_email(get_value(row, 'email', ''), email_mapping)
        
        if user_email in assigned_users:
            continue
        
        go_solo_value = str(get_value(row, 'go_solo', '0')).strip()
        user_id = get_value(row, 'user_id', 'Unknown')
        
        if go_solo_value.lower() in ['1', '1.0', 'true']:
            solo_groups.append([row])
            solo_count += 1
            assigned_users.add(user_email)
            
            user_id_str = str(user_id).strip() if user_id else 'Unknown'
            if user_id_str in user_tracking:
                user_tracking[user_id_str]['status'] = 'solo'
                user_tracking[user_id_str]['reason'] = 'go_solo = True'
    
    # Step 5: Handle remaining participants (regular grouping)
    remaining_data = []
    for row in data:
        user_email = normalize_email(get_value(row, 'email', ''), email_mapping)
        if user_email not in assigned_users:
            remaining_data.append(row)
    
    # Group by gender preference
    gender_pref_groups = defaultdict(list)
    
    for row in remaining_data:
        gender_pref = str(get_value(row, 'gender_preference', '')).lower()
        user_id = get_value(row, 'user_id', 'Unknown')
        
        if gender_pref == 'same_gender':
            sex = str(get_value(row, 'sex', '')).lower()
            gender_identity = str(get_value(row, 'gender_identity', '')).upper()
            
            if gender_identity == 'LGBTQ+':
                gender_key = f"lgbtq+_{sex}"
            else:
                gender_key = sex
        elif gender_pref == 'no_preference':
            gender_key = 'no_preference'
        else:
            gender_key = 'other'
        
        gender_pref_groups[gender_key].append(row)
    
    # Process each gender group
    for gender_key, rows in gender_pref_groups.items():
        # Split by PH or not
        ph_rows = []
        non_ph_rows = []
        
        for r in rows:
            ph_val = str(get_value(r, 'residing_ph', '0')).strip().lower()
            if ph_val in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
                ph_rows.append(r)
            else:
                non_ph_rows.append(r)
        
        # Group Philippines participants by Province -> City
        province_groups = defaultdict(list)
        for r in ph_rows:
            province = get_value(r, 'province', 'Unknown Province')
            province_norm = province.strip().lower() if isinstance(province, str) else str(province).strip().lower()
            province_groups[province_norm].append(r)
        
        # Sort provinces by region
        sorted_provinces = []
        for province_norm, province_members in province_groups.items():
            original_province = get_value(province_members[0], 'province', 'Unknown Province')
            region = get_philippines_region(original_province)
            sorted_provinces.append((original_province, province_norm, province_members, region))
        
        region_order = {'luzon': 1, 'visayas': 2, 'mindanao': 3, 'unknown': 4}
        sorted_provinces.sort(key=lambda x: (region_order.get(x[3], 5), str(x[0]).lower() if x[0] else ''))
        
        for original_province, province_norm, province_members, region in sorted_provinces:
            province = original_province
            
            # Group by city within province
            city_groups = defaultdict(list)
            for r in province_members:
                city = get_value(r, 'city', 'Unknown City')
                city_norm = city.strip().lower() if isinstance(city, str) else str(city).strip().lower()
                city_groups[city_norm].append(r)
            
            sorted_city_names = sorted(city_groups.keys())
            
            # Create groups from each city
            for city_norm in sorted_city_names:
                members = city_groups[city_norm]
                
                # Create complete groups of 5
                i = 0
                while i + 5 <= len(members):
                    group_members = members[i:i+5]
                    location_info = f"Province: {province}, City: {city_norm}"
                    grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                    group_counter += 1
                    i += 5
                
                # Handle remaining members
                if i < len(members):
                    remaining_members = members[i:]
                    
                    # Try to form a complete group
                    if len(remaining_members) >= 5:
                        group_members = remaining_members[:5]
                        location_info = f"Province: {province}, City: {city_norm}"
                        grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                        group_counter += 1
                        remaining_members = remaining_members[5:]
                    
                    # Add remaining to mixed groups
                    if remaining_members:
                        # Find other remaining members from same province
                        all_remaining = []
                        for other_city in sorted_city_names:
                            if other_city != city_norm:
                                other_members = city_groups[other_city]
                                other_i = 0
                                while other_i + 5 <= len(other_members):
                                    other_i += 5
                                if other_i < len(other_members):
                                    all_remaining.extend(other_members[other_i:])
                        
                        all_remaining.extend(remaining_members)
                        
                        # Create mixed groups
                        i = 0
                        while i < len(all_remaining):
                            group_members = all_remaining[i:i+5]
                            location_info = f"Province: {province} (mixed cities)"
                            grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                            group_counter += 1
                            i += 5
        
        # Group International participants by Country -> State
        country_groups = defaultdict(list)
        for r in non_ph_rows:
            country = get_value(r, 'country', 'Unknown Country')
            country_groups[country].append(r)
        
        for country, country_members in country_groups.items():
            state_groups = defaultdict(list)
            for r in country_members:
                state = get_value(r, 'state', 'Unknown State')
                state_groups[state].append(r)
            
            for state, members in state_groups.items():
                # Create complete groups of 5
                i = 0
                while i + 5 <= len(members):
                    group_members = members[i:i+5]
                    location_info = f"Country: {country}, State: {state}"
                    grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                    group_counter += 1
                    i += 5
                
                # Handle remaining members
                if i < len(members):
                    remaining_members = members[i:]
                    
                    # Try to form a complete group
                    if len(remaining_members) >= 5:
                        group_members = remaining_members[:5]
                        location_info = f"Country: {country}, State: {state}"
                        grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                        group_counter += 1
                        remaining_members = remaining_members[5:]
                    
                    # Add remaining to mixed groups
                    if remaining_members:
                        # Find other remaining members from same country
                        all_remaining = []
                        for other_state in state_groups:
                            if other_state != state:
                                other_members = state_groups[other_state]
                                other_i = 0
                                while other_i + 5 <= len(other_members):
                                    other_i += 5
                                if other_i < len(other_members):
                                    all_remaining.extend(other_members[other_i:])
                        
                        all_remaining.extend(remaining_members)
                        
                        # Create mixed groups
                        i = 0
                        while i < len(all_remaining):
                            group_members = all_remaining[i:i+5]
                            location_info = f"Country: {country} (mixed states)"
                            grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                            group_counter += 1
                            i += 5
    
    # Update remaining users as regular grouping
    for user_id, info in user_tracking.items():
        if info['status'] == 'original':
            info['status'] = 'regular_grouping'
            info['reason'] = 'Regular grouping (non-solo, no special requests)'
    
    return solo_groups, grouped, excluded_users, requested_groups

def test_fixed_grouping():
    """Test the fixed grouping function"""
    
    print("🧪 TESTING FIXED GROUPING FUNCTION")
    print("=" * 60)
    
    # Read the merged Excel file
    INPUT_FILE = 'merged_users_grouping_preferences_20250718_221747.xlsx'
    
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
    
    # Test the fixed grouping function
    print(f"\n🚀 Testing fixed group assignment...")
    solo_groups, grouped, excluded_users, requested_groups = group_participants_fixed(data, column_mapping)
    
    # Check for duplicates
    all_users = set()
    duplicate_users = set()
    
    def get_value(row, key, default=''):
        if column_mapping and key in column_mapping:
            if isinstance(row, dict):
                return row.get(column_mapping[key], default)
            else:
                return default
        else:
            return default
    
    # Collect all users
    for group in solo_groups:
        for member in group:
            user_id = get_value(member, 'user_id', 'Unknown')
            if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
                user_key = str(user_id).strip()
                if user_key in all_users:
                    duplicate_users.add(user_key)
                else:
                    all_users.add(user_key)
    
    for group_name, members in grouped.items():
        for member in members:
            user_id = get_value(member, 'user_id', 'Unknown')
            if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
                user_key = str(user_id).strip()
                if user_key in all_users:
                    duplicate_users.add(user_key)
                else:
                    all_users.add(user_key)
    
    for group in requested_groups:
        for member in group:
            user_id = get_value(member, 'user_id', 'Unknown')
            if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
                user_key = str(user_id).strip()
                if user_key in all_users:
                    duplicate_users.add(user_key)
                else:
                    all_users.add(user_key)
    
    for user in excluded_users:
        user_id = get_value(user, 'user_id', 'Unknown')
        if user_id and str(user_id).strip() not in ['', 'nan', 'None']:
            user_key = str(user_id).strip()
            if user_key in all_users:
                duplicate_users.add(user_key)
            else:
                all_users.add(user_key)
    
    print(f"\n📊 RESULTS:")
    print(f"Total unique users in output: {len(all_users)}")
    print(f"Duplicate users: {len(duplicate_users)}")
    
    if duplicate_users:
        print(f"\n❌ DUPLICATE USERS FOUND:")
        for user_id in sorted(duplicate_users):
            print(f"  - User ID: {user_id}")
    else:
        print(f"\n✅ NO DUPLICATE USERS FOUND!")
    
    # Check specific users
    print(f"\n🔍 CHECKING SPECIFIC USERS:")
    
    # Look for Jericho Nangyo
    jericho_found = False
    for user_id in all_users:
        # Find user data
        for row in data:
            if str(get_value(row, 'user_id', '')).strip() == user_id:
                name = get_value(row, 'name', '')
                if 'jericho' in str(name).lower() or 'nangyo' in str(name).lower():
                    jericho_found = True
                    print(f"✅ Found Jericho Nangyo: User ID {user_id}, Name: {name}")
                    break
        if jericho_found:
            break
    
    if not jericho_found:
        print(f"❌ Jericho Nangyo not found in output")
    
    # Look for Eco and Gico
    eco_found = False
    gico_found = False
    
    for user_id in all_users:
        for row in data:
            if str(get_value(row, 'user_id', '')).strip() == user_id:
                name = get_value(row, 'name', '')
                if 'eco' in str(name).lower() and 'filoteo' in str(name).lower():
                    eco_found = True
                    print(f"✅ Found Eco: User ID {user_id}, Name: {name}")
                elif 'gico' in str(name).lower() and 'regacho' in str(name).lower():
                    gico_found = True
                    print(f"✅ Found Gico: User ID {user_id}, Name: {name}")
                break
    
    if not eco_found:
        print(f"❌ Eco not found in output")
    if not gico_found:
        print(f"❌ Gico not found in output")
    
    print(f"\n📋 GROUP SUMMARY:")
    print(f"Solo groups: {len(solo_groups)}")
    print(f"Regular groups: {len(grouped)}")
    print(f"Requested groups: {len(requested_groups)}")
    print(f"Excluded users: {len(excluded_users)}")
    
    return solo_groups, grouped, excluded_users, requested_groups

if __name__ == "__main__":
    test_fixed_grouping() 