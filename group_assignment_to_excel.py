import pandas as pd
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font

# File paths - Updated to use merged Excel file
INPUT_FILE = 'sample_merged_data.xlsx'  # Change this to your merged file
OUTPUT_FILE = 'grouped_participants.xlsx'

# Column mapping for merged data (will be dynamically determined)
# These are the expected column names in the merged data
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
    'email': ['email', 'user_email', 'email_address', 'useremail', 'userEmail']
}

# Helper for color coding
GENDER_COLOR = {
    'male': 'ADD8E6',    # Light Blue
    'female': 'FFC0CB',  # Pink
    'lgbtq+': '90EE90',  # Light Green
    'lgbtq': '90EE90',
}

# Define similar country regions for grouping
SIMILAR_COUNTRIES = {
    'southeast_asia': ['Philippines', 'Indonesia', 'Malaysia', 'Thailand', 'Vietnam', 'Singapore', 'Myanmar', 'Cambodia', 'Laos', 'Brunei'],
    'east_asia': ['China', 'Japan', 'South Korea', 'Taiwan', 'Hong Kong', 'Macau'],
    'south_asia': ['India', 'Pakistan', 'Bangladesh', 'Sri Lanka', 'Nepal', 'Bhutan', 'Maldives'],
    'north_america': ['United States', 'Canada', 'Mexico'],
    'europe': ['United Kingdom', 'Germany', 'France', 'Italy', 'Spain', 'Netherlands', 'Belgium', 'Switzerland', 'Austria', 'Sweden', 'Norway', 'Denmark', 'Finland'],
    'middle_east': ['Saudi Arabia', 'UAE', 'Qatar', 'Kuwait', 'Bahrain', 'Oman', 'Jordan', 'Lebanon', 'Israel', 'Turkey'],
    'africa': ['South Africa', 'Nigeria', 'Kenya', 'Egypt', 'Morocco', 'Ghana', 'Ethiopia'],
    'oceania': ['Australia', 'New Zealand', 'Fiji', 'Papua New Guinea']
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
            print(f"Warning: Could not find column for {expected_key}")
            mapping[expected_key] = None
    
    return mapping

def get_country_region(country):
    """Get the region for a given country"""
    country = str(country).strip()
    for region, countries in SIMILAR_COUNTRIES.items():
        if country in countries:
            return region
    return 'other'

def merge_small_groups_with_preference_separation(groups_dict, max_group_size=5, column_mapping=None):
    """Merge groups with less than max_group_size members, keeping preferences separate and grouping by most specific location first."""
    merged_groups = {}
    small_groups = []
    normal_groups = {}
    
    # Separate small groups from normal groups
    for group_name, members in groups_dict.items():
        if len(members) < max_group_size:
            small_groups.append((group_name, members))
        else:
            normal_groups[group_name] = members
    
    if not small_groups:
        return groups_dict
    
    # Step 1: Try to merge by most specific location (province for PH, country/state for international)
    specific_location_groups = defaultdict(list)
    for group_name, members in small_groups:
        if not members:
            continue
        # Determine preference type
        is_same_gender = False
        if 'male' in group_name.lower() or 'female' in group_name.lower() or 'lgbtq' in group_name.lower():
            is_same_gender = True
        # Extract gender key
        gender_key = 'unknown'
        if 'male' in group_name.lower():
            gender_key = 'male'
        elif 'female' in group_name.lower():
            gender_key = 'female'
        elif 'lgbtq' in group_name.lower():
            gender_key = 'lgbtq+'
        elif 'no_preference' in group_name.lower():
            gender_key = 'no_preference'
        # Location keys
        member = members[0]
        if column_mapping:
            residing_ph = str(member.get(column_mapping.get('residing_ph'), '0')) == '1'
            if residing_ph:
                province = member.get(column_mapping.get('province'), 'Unknown Province')
                key = ("same_gender" if is_same_gender else "no_preference", gender_key, "PH", province)
            else:
                country = member.get(column_mapping.get('country'), 'Unknown Country')
                state = member.get(column_mapping.get('state'), 'Unknown State')
                key = ("same_gender" if is_same_gender else "no_preference", gender_key, country, state)
        else:
            # Fallback to old method
            residing_ph = str(member.get('residing_ph', '0')) == '1'
            if residing_ph:
                province = member.get('province', 'Unknown Province')
                key = ("same_gender" if is_same_gender else "no_preference", gender_key, "PH", province)
            else:
                country = member.get('country', 'Unknown Country')
                state = member.get('state', 'Unknown State')
                key = ("same_gender" if is_same_gender else "no_preference", gender_key, country, state)
        specific_location_groups[key].extend(members)
    
    # Merge by specific location
    leftovers = []
    group_counter = len(normal_groups) + 1
    for key, all_members in specific_location_groups.items():
        for i in range(0, len(all_members), max_group_size):
            chunk = all_members[i:i+max_group_size]
            if len(chunk) == max_group_size or (len(chunk) >= 2 and i == 0 and len(all_members) < max_group_size):
                # Only create a group if full or if this is the only group for this location
                pref_type, gender_key, loc1, loc2 = key
                if loc1 == "PH":
                    location_info = f"Province: {loc2}"
                else:
                    location_info = f"Country: {loc1}, State: {loc2}"
                merged_groups[f"Group {group_counter} ({pref_type}, {gender_key}, {location_info})"] = chunk
                group_counter += 1
            else:
                leftovers.extend(chunk)
    
    # Step 2: Merge remaining leftovers by region, keeping Philippines separate
    philippines_groups = defaultdict(list)
    international_groups = defaultdict(list)
    
    for member in leftovers:
        # Determine preference type
        if column_mapping:
            gender_pref = str(member.get(column_mapping.get('gender_preference'), '')).lower()
            if gender_pref == 'same_gender':
                if str(member.get(column_mapping.get('gender_identity'), '')).upper() == 'LGBTQ+':
                    gender_key = f"lgbtq+_{str(member.get(column_mapping.get('sex'), '')).lower()}"
                else:
                    gender_key = str(member.get(column_mapping.get('gender_identity'), '')).lower()
                pref_type = 'same_gender'
            else:
                gender_key = 'no_preference'
                pref_type = 'no_preference'
            
            # Separate Philippines from international
            country = member.get(column_mapping.get('country'), 'Unknown Country')
        else:
            # Fallback to old method
            gender_pref = str(member.get('gender_preference', '')).lower()
            if gender_pref == 'same_gender':
                if str(member.get('gender_identity', '')).upper() == 'LGBTQ+':
                    gender_key = f"lgbtq+_{str(member.get('sex', '')).lower()}"
                else:
                    gender_key = str(member.get('gender_identity', '')).lower()
                pref_type = 'same_gender'
            else:
                gender_key = 'no_preference'
                pref_type = 'no_preference'
            
            # Separate Philippines from international
            country = member.get('country', 'Unknown Country')
        
        if country == 'Philippines':
            # For Philippines, group by preference and gender
            philippines_groups[(pref_type, gender_key)].append(member)
        else:
            # For international, group by region
            region = get_country_region(country)
            international_groups[(pref_type, gender_key, region)].append(member)
    # Merge Philippines groups
    for key, all_members in philippines_groups.items():
        pref_type, gender_key = key
        for i in range(0, len(all_members), max_group_size):
            chunk = all_members[i:i+max_group_size]
            merged_groups[f"Group {group_counter} ({pref_type}, {gender_key}, Philippines)"] = chunk
            group_counter += 1
    
    # Merge international groups by region
    for key, all_members in international_groups.items():
        pref_type, gender_key, region = key
        for i in range(0, len(all_members), max_group_size):
            chunk = all_members[i:i+max_group_size]
            # Region name
            if region == 'southeast_asia':
                location_info = "Southeast Asia"
            elif region == 'east_asia':
                location_info = "East Asia"
            elif region == 'south_asia':
                location_info = "South Asia"
            elif region == 'north_america':
                location_info = "North America"
            elif region == 'europe':
                location_info = "Europe"
            elif region == 'middle_east':
                location_info = "Middle East"
            elif region == 'africa':
                location_info = "Africa"
            elif region == 'oceania':
                location_info = "Oceania"
            else:
                location_info = "International"
            merged_groups[f"Group {group_counter} ({pref_type}, {gender_key}, {location_info})"] = chunk
            group_counter += 1
    # Combine normal groups with merged groups
    final_groups = {**normal_groups, **merged_groups}
    return final_groups

def merge_small_groups(groups_dict, max_group_size=5):
    """Merge groups with less than max_group_size members with similar countries"""
    merged_groups = {}
    small_groups = []
    normal_groups = {}
    
    # Separate small groups from normal groups
    for group_name, members in groups_dict.items():
        if len(members) < max_group_size:
            small_groups.append((group_name, members))
        else:
            normal_groups[group_name] = members
    
    if not small_groups:
        return groups_dict
    
    # Group small groups by gender preference and country region
    small_groups_by_region = defaultdict(list)
    
    for group_name, members in small_groups:
        if not members:
            continue
        
        # Extract gender preference from group name
        gender_key = 'unknown'
        if 'male' in group_name.lower():
            gender_key = 'male'
        elif 'female' in group_name.lower():
            gender_key = 'female'
        elif 'lgbtq' in group_name.lower():
            gender_key = 'lgbtq+'
        elif 'no_preference' in group_name.lower():
            gender_key = 'no_preference'
        
        # Get country region for the first member (assuming all members in a group are from same region)
        # Use the old method since this function doesn't have column_mapping
        country_region = get_country_region(members[0].get('country', 'Unknown Country'))
        
        key = f"{gender_key}_{country_region}"
        small_groups_by_region[key].extend(members)
    
    # Create merged groups
    group_counter = len(normal_groups) + 1
    
    for region_key, all_members in small_groups_by_region.items():
        # Split into chunks of max_group_size
        for i in range(0, len(all_members), max_group_size):
            chunk = all_members[i:i+max_group_size]
            gender_key, country_region = region_key.split('_', 1)
            
            # Create descriptive group name
            if country_region == 'southeast_asia':
                location_info = "Southeast Asia"
            elif country_region == 'east_asia':
                location_info = "East Asia"
            elif country_region == 'south_asia':
                location_info = "South Asia"
            elif country_region == 'north_america':
                location_info = "North America"
            elif country_region == 'europe':
                location_info = "Europe"
            elif country_region == 'middle_east':
                location_info = "Middle East"
            elif country_region == 'africa':
                location_info = "Africa"
            elif country_region == 'oceania':
                location_info = "Oceania"
            else:
                location_info = "International"
            
            merged_groups[f"Group {group_counter} ({gender_key}, {location_info})"] = chunk
            group_counter += 1
    
    # Combine normal groups with merged groups
    final_groups = {**normal_groups, **merged_groups}
    return final_groups

def apply_color_to_cell(cell, gender_identity, same_gender=None, kaizen_client_type=None):
    gender_identity = str(gender_identity).lower()
    if gender_identity in GENDER_COLOR:
        cell.fill = PatternFill(start_color=GENDER_COLOR[gender_identity], end_color=GENDER_COLOR[gender_identity], fill_type="solid")
    
    # Apply font formatting
    font_style = Font()
    if same_gender is not None and str(same_gender).lower() == "same_gender":
        font_style = Font(bold=True)
    
    # Apply dark red color for team members
    if kaizen_client_type is not None and str(kaizen_client_type).lower() == "team_member":
        font_style = Font(color="8B0000")  # Dark red color
        if same_gender is not None and str(same_gender).lower() == "same_gender":
            font_style = Font(bold=True, color="8B0000")  # Bold and dark red
    
    cell.font = font_style

def group_participants(data, column_mapping):
    solo_groups = []
    grouped = defaultdict(list)
    group_counter = 1
    
    print(f"Total participants: {len(data)}")
    
    # Helper function to get value safely
    def get_value(row, key, default=''):
        if column_mapping and key in column_mapping:
            if isinstance(row, dict):
                return row.get(column_mapping[key], default)
            else:
                # For list format, we can't use column mapping
                return default
        else:
            # Fallback to old format (list indices)
            if isinstance(row, list):
                if key == 'go_solo':
                    return row[20] if len(row) > 20 else default
                elif key == 'user_id':
                    return row[0] if len(row) > 0 else default
                elif key == 'gender_preference':
                    return row[10] if len(row) > 10 else default
                elif key == 'gender_identity':
                    return row[3] if len(row) > 3 else default
                elif key == 'sex':
                    return row[7] if len(row) > 7 else default
                elif key == 'residing_ph':
                    return row[8] if len(row) > 8 else default
                elif key == 'country':
                    return row[16] if len(row) > 16 else default
                elif key == 'province':
                    return row[17] if len(row) > 17 else default
                elif key == 'city':
                    return row[18] if len(row) > 18 else default
                elif key == 'state':
                    return row[19] if len(row) > 19 else default
            return default
    
    # Filter out participants where joiningAsStudent is False (but keep NaN/missing values)
    excluded_users = []  # Track excluded users to include them later
    if column_mapping and 'joining_as_student' in column_mapping:
        joining_col = column_mapping['joining_as_student']
        # Keep participants where joiningAsStudent is True or NaN/missing
        filtered_data = []
        excluded_count = 0
        for row in data:
            joining_value = get_value(row, 'joining_as_student', 'True')
            # Convert to string and check if it's explicitly False
            joining_str = str(joining_value).strip().lower()
            if joining_str in ['false', '0', '0.0', 'no']:
                excluded_count += 1
                excluded_users.append(row)  # Add to excluded list
                user_id = get_value(row, 'user_id', 'Unknown')
                print(f"Excluded User {user_id}: joiningAsStudent = '{joining_value}'")
            else:
                # Keep if True, NaN, or any other value (including missing)
                filtered_data.append(row)
        
        data = filtered_data
        print(f"Excluded {excluded_count} participants with joiningAsStudent=False")
        print(f"Remaining participants: {len(data)}")
    
    # 1. Handle Accountability Buddies (Requested Groups) - Process first
    requested_groups = []
    accountability_count = 0
    
    # First pass: collect all participants with non-empty accountabilityBuddies
    accountability_participants = []
    for row in data:
        accountability_buddies = get_value(row, 'accountability_buddies', '')
        has_accountability_buddies = get_value(row, 'has_accountability_buddies', '0')
        user_id = get_value(row, 'user_id', 'Unknown')
        
        # Check if has_accountability_buddies is True/1
        has_buddies = str(has_accountability_buddies).strip().lower() in ['1', '1.0', 'true', 'yes']
        
        # Check if accountability_buddies field has valid data
        has_buddy_data = accountability_buddies and str(accountability_buddies).strip() not in ['', 'None', 'nan', '[None]', '[None, None]', "{'1': None}"]
        
        if has_buddies and has_buddy_data:
            accountability_participants.append(row)
            print(f"User {user_id}: has_accountability_buddies={has_accountability_buddies}, accountability_buddies='{accountability_buddies}'")
        elif has_buddies and not has_buddy_data:
            print(f"User {user_id}: has_accountability_buddies={has_accountability_buddies} but no buddy data: '{accountability_buddies}'")
        elif not has_buddies and has_buddy_data:
            print(f"User {user_id}: has_accountability_buddies={has_accountability_buddies} but has buddy data: '{accountability_buddies}'")
    
    print(f"Found {len(accountability_participants)} participants with accountability buddies")
    
    # Create a mapping of email to user data for quick lookup
    email_to_user = {}
    for row in data:
        # Use the column mapping to find email
        email = get_value(row, 'email', '')
        
        if email and '@' in email:
            email_to_user[email.lower().strip()] = row
            user_id = get_value(row, 'user_id', 'Unknown')
            print(f"User {user_id}: email = {email}")
    
    print(f"Created email mapping for {len(email_to_user)} users")
    
    # Process each participant with accountability buddies
    processed_requests = set()  # Track processed requests to avoid duplicates
    assigned_users = set()  # Track users already assigned to requested groups
    
    for participant in accountability_participants:
        accountability_buddies = get_value(participant, 'accountability_buddies', '')
        user_id = get_value(participant, 'user_id', 'Unknown')
        participant_email = get_value(participant, 'email', '').lower().strip()
        
        # Skip if this participant is already assigned to a requested group
        if participant_email in assigned_users:
            print(f"Skipping User {user_id} ({participant_email}): already assigned to a requested group")
            continue
        
        # Clean and extract emails from accountabilityBuddies
        if isinstance(accountability_buddies, str):
            # Remove brackets and quotes, split by comma
            cleaned = accountability_buddies.strip('[]').replace('"', '').replace("'", '')
            requested_emails = [email.strip().lower() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
            
            if requested_emails:
                # Create a unique key for this request to avoid duplicates
                request_key = ','.join(sorted(requested_emails))
                
                if request_key not in processed_requests:
                    processed_requests.add(request_key)
                    
                    # Build the group: requester + all requested buddies
                    group_members = [participant]  # Start with the requester
                    assigned_users.add(participant_email)  # Mark requester as assigned
                    
                    # Add all requested buddies (only if not already assigned)
                    found_buddies = []
                    missing_buddies = []
                    already_assigned_buddies = []
                    
                    for email in requested_emails:
                        if email in email_to_user:
                            buddy_user = email_to_user[email]
                            buddy_email = get_value(buddy_user, 'email', '').lower().strip()
                            
                            # Check if this buddy is already assigned to a requested group
                            if buddy_email in assigned_users:
                                already_assigned_buddies.append(email)
                                buddy_user_id = get_value(buddy_user, 'user_id', 'Unknown')
                                print(f"  Skipping buddy {email} -> User {buddy_user_id}: already assigned to another requested group")
                            else:
                                group_members.append(buddy_user)
                                assigned_users.add(buddy_email)  # Mark buddy as assigned
                                found_buddies.append(email)
                                buddy_user_id = get_value(buddy_user, 'user_id', 'Unknown')
                                print(f"  Found buddy {email} -> User {buddy_user_id}")
                        else:
                            missing_buddies.append(email)
                            print(f"  Missing buddy: {email}")
                    
                    if group_members:
                        requested_groups.append(group_members)
                        accountability_count += len(group_members)
                        print(f"Created Requested Group with {len(group_members)} members:")
                        print(f"  Requester: User {user_id}")
                        print(f"  Requested emails: {requested_emails}")
                        print(f"  Found buddies: {found_buddies}")
                        if missing_buddies:
                            print(f"  Missing buddies: {missing_buddies}")
                        if already_assigned_buddies:
                            print(f"  Already assigned buddies: {already_assigned_buddies}")
    
    print(f"Created {len(requested_groups)} requested groups with {accountability_count} participants")
    print(f"Total users assigned to requested groups: {len(assigned_users)}")
    
    # 2. Handle Solo participants (from remaining data)
    solo_count = 0
    # Remove accountability participants and already assigned users from data for solo processing
    remaining_data = []
    for row in data:
        user_email = get_value(row, 'email', '').lower().strip()
        # Skip if user is in accountability participants or already assigned to requested groups
        if row not in accountability_participants and user_email not in assigned_users:
            remaining_data.append(row)
    
    print(f"Remaining participants for solo/regular grouping: {len(remaining_data)}")
    
    for row in remaining_data:
        go_solo_value = str(get_value(row, 'go_solo', '0')).strip()
        user_id = get_value(row, 'user_id', 'Unknown')
        print(f"User {user_id}: go_solo = '{go_solo_value}'")
        # Handle various formats: '1', '1.0', 'True', 'true'
        if go_solo_value.lower() in ['1', '1.0', 'true']:
            solo_groups.append([row])
            solo_count += 1
            print(f"Added to solo: User {user_id}")
    
    print(f"Found {solo_count} solo participants")
    
    # 3. Handle non-solo participants (from remaining data)
    non_solo = [row for row in remaining_data if str(get_value(row, 'go_solo', '0')).strip().lower() not in ['1', '1.0', 'true']]
    print(f"Non-solo participants: {len(non_solo)}")
    
    # Group by gender preference
    gender_pref_groups = defaultdict(list)
    print(f"Processing {len(non_solo)} non-solo participants for grouping...")
    
    for row in non_solo:
        gender_pref = str(get_value(row, 'gender_preference', '')).lower()
        user_id = get_value(row, 'user_id', 'Unknown')
        print(f"User {user_id}: gender_preference = '{gender_pref}'")
        
        if gender_pref == 'same_gender':
            # Special handling for LGBTQ+
            if str(get_value(row, 'gender_identity', '')).upper() == 'LGBTQ+':
                gender_key = f"lgbtq+_{str(get_value(row, 'sex', '')).lower()}"
            else:
                gender_key = str(get_value(row, 'gender_identity', '')).lower()
        elif gender_pref == 'no_preference':
            gender_key = 'no_preference'
        else:
            gender_key = 'other'
        
        gender_pref_groups[gender_key].append(row)
        print(f"  -> Assigned to group: {gender_key}")
    
    print(f"Gender preference groups created:")
    for key, members in gender_pref_groups.items():
        print(f"  {key}: {len(members)} participants")
    
    # Now, within each gender group, group by location with hierarchical approach
    for gender_key, rows in gender_pref_groups.items():
        print(f"\nProcessing gender group: {gender_key} ({len(rows)} participants)")
        
        # Split by PH or not
        ph_rows = []
        non_ph_rows = []
        
        # Debug: Check what values are in the residing_ph column
        ph_values = []
        for r in rows[:5]:  # Check first 5 participants
            ph_val = get_value(r, 'residing_ph', '0')
            ph_values.append(ph_val)
            user_id = get_value(r, 'user_id', 'Unknown')
            print(f"    User {user_id}: residing_ph = '{ph_val}' (type: {type(ph_val)})")
        
        print(f"    Sample residing_ph values: {ph_values}")
        
        for r in rows:
            ph_val = str(get_value(r, 'residing_ph', '0')).strip().lower()
            if ph_val in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
                ph_rows.append(r)
            elif ph_val in ['0', '0.0', 'false', 'no']:
                non_ph_rows.append(r)
            else:
                # For unknown values, treat as international
                non_ph_rows.append(r)
                user_id = get_value(r, 'user_id', 'Unknown')
                print(f"    User {user_id}: unknown residing_ph value '{ph_val}', treating as international")
        
        print(f"  Philippines residents: {len(ph_rows)}")
        print(f"  International residents: {len(non_ph_rows)}")
        
        # Group Philippines participants by Province -> City hierarchy
        province_groups = defaultdict(list)
        for r in ph_rows:
            province = get_value(r, 'province', 'Unknown Province')
            province_groups[province].append(r)
        
        print(f"  Philippines provinces found: {list(province_groups.keys())}")
        
        for province, province_members in province_groups.items():
            print(f"    Province '{province}': {len(province_members)} participants")
            # Further group by city within each province
            city_groups = defaultdict(list)
            for r in province_members:
                city = get_value(r, 'city', 'Unknown City')
                city_groups[city].append(r)
            
            print(f"      Cities in {province}: {list(city_groups.keys())}")
            
            for city, members in city_groups.items():
                print(f"        City '{city}': {len(members)} participants")
                # Split into chunks of 5
                for i in range(0, len(members), 5):
                    location_info = f"Province: {province}, City: {city}"
                    grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = members[i:i+5]
                    print(f"          Created Group {group_counter} with {len(members[i:i+5])} members")
                    group_counter += 1
        
        # Group International participants by Country -> State hierarchy
        country_groups = defaultdict(list)
        for r in non_ph_rows:
            country = get_value(r, 'country', 'Unknown Country')
            country_groups[country].append(r)
        
        print(f"  International countries found: {list(country_groups.keys())}")
        
        for country, country_members in country_groups.items():
            print(f"    Country '{country}': {len(country_members)} participants")
            # Further group by state within each country
            state_groups = defaultdict(list)
            for r in country_members:
                state = get_value(r, 'state', 'Unknown State')
                state_groups[state].append(r)
            
            print(f"      States in {country}: {list(state_groups.keys())}")
            
            for state, members in state_groups.items():
                print(f"        State '{state}': {len(members)} participants")
                for i in range(0, len(members), 5):
                    location_info = f"Country: {country}, State: {state}"
                    grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = members[i:i+5]
                    print(f"          Created Group {group_counter} with {len(members[i:i+5])} members")
                    group_counter += 1
    
    # Merge small groups with similar countries, but keep same_gender and no_preference separate
    print(f"Before merging: {len(grouped)} groups")
    grouped = merge_small_groups_with_preference_separation(grouped, max_group_size=5, column_mapping=column_mapping)
    print(f"After merging: {len(grouped)} groups")
    
    print(f"Created {len(requested_groups)} requested groups, {len(solo_groups)} solo groups and {len(grouped)} regular groups")
    print(f"Excluded {len(excluded_users)} users with joiningAsStudent=False")
    return solo_groups, grouped, excluded_users, requested_groups

def save_to_excel(solo_groups, grouped, filename_or_buffer, column_mapping, excluded_users=None, requested_groups=None):
    wb = Workbook()
    ws = wb.active
    ws.title = "Grouped Members"
    ws.append([
        "Group Name",
        "User ID 1", "Name 1", "City 1",
        "User ID 2", "Name 2", "City 2",
        "User ID 3", "Name 3", "City 3",
        "User ID 4", "Name 4", "City 4",
        "User ID 5", "Name 5", "City 5",
        "Gender Identity", "Sex", "Residing in PH", "Gender Preference", "Country", "Province", "City", "State"
    ])
    
    # Write requested groups (accountability buddies)
    if requested_groups:
        print(f"Writing {len(requested_groups)} requested groups to Excel...")
        for idx, group in enumerate(requested_groups, 1):
            row = [f"Requested Group {idx}"]
            
            # Add user data for each member
            for i in range(5):
                if i < len(group):
                    member = group[i]
                    # Determine location display based on residing_ph
                    residing_ph = str(member.get(column_mapping.get('residing_ph'), '0')).strip().lower()
                    if residing_ph in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
                        # Philippines resident - show city
                        location_display = member.get(column_mapping.get('city'), '')
                    else:
                        # International resident - show "State, Country"
                        state = member.get(column_mapping.get('state'), '')
                        country = member.get(column_mapping.get('country'), '')
                        if state and country:
                            location_display = f"{state}, {country}"
                        elif country:
                            location_display = country
                        else:
                            location_display = member.get(column_mapping.get('city'), '')
                    
                    row.extend([
                        member.get(column_mapping.get('user_id'), ''),
                        member.get(column_mapping.get('name'), ''),
                        location_display
                    ])
                else:
                    row.extend(["", "", ""])
            
            # Add extra info for the first member
            member = group[0]
            row.extend([
                member.get(column_mapping.get('gender_identity'), ''),
                member.get(column_mapping.get('sex'), ''),
                member.get(column_mapping.get('residing_ph'), ''),
                member.get(column_mapping.get('gender_preference'), ''),
                member.get(column_mapping.get('country'), ''),
                member.get(column_mapping.get('province'), ''),
                member.get(column_mapping.get('city'), ''),
                member.get(column_mapping.get('state'), '')
            ])
            
            ws.append(row)
            print(f"Added requested group {idx} with {len(group)} members")
            
            # Apply formatting
            for i in range(5):
                if i < len(group):
                    member = group[i]
                    gender_pref = member.get(column_mapping.get('gender_preference'), '')
                    kaizen_client_type = member.get(column_mapping.get('kaizen_client_type'), '')
                    apply_color_to_cell(ws.cell(row=ws.max_row, column=2 + i*3), member.get(column_mapping.get('gender_identity'), ''))
                    apply_color_to_cell(ws.cell(row=ws.max_row, column=3 + i*3), member.get(column_mapping.get('gender_identity'), ''), gender_pref, kaizen_client_type)
    
    # Write solo groups
    print(f"Writing {len(solo_groups)} solo groups to Excel...")
    for idx, group in enumerate(solo_groups, 1):
        row = [f"Solo {idx}"]
        for i in range(5):
            if i < len(group):
                member = group[i]
                # Determine location display based on residing_ph
                residing_ph = str(member.get(column_mapping.get('residing_ph'), '0')).strip().lower()
                if residing_ph in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
                    # Philippines resident - show city
                    location_display = member.get(column_mapping.get('city'), '')
                else:
                    # International resident - show "State, Country"
                    state = member.get(column_mapping.get('state'), '')
                    country = member.get(column_mapping.get('country'), '')
                    if state and country:
                        location_display = f"{state}, {country}"
                    elif country:
                        location_display = country
                    else:
                        location_display = member.get(column_mapping.get('city'), '')
                
                row.extend([
                    member.get(column_mapping.get('user_id'), ''),
                    member.get(column_mapping.get('name'), ''),
                    location_display
                ])
            else:
                row.extend(["", "", ""])
        # Add extra info for the first member
        member = group[0]
        row.extend([
            member.get(column_mapping.get('gender_identity'), ''),
            member.get(column_mapping.get('sex'), ''),
            member.get(column_mapping.get('residing_ph'), ''),
            member.get(column_mapping.get('gender_preference'), ''),
            member.get(column_mapping.get('country'), ''),
            member.get(column_mapping.get('province'), ''),
            member.get(column_mapping.get('city'), ''),
            member.get(column_mapping.get('state'), '')
        ])
        ws.append(row)
        print(f"Added solo group {idx} with user {member.get(column_mapping.get('user_id'), 'Unknown')}")
        # Color code user_id and name cells for each member
        for i in range(5):
            if i < len(group):
                member = group[i]
                gender_pref = member.get(column_mapping.get('gender_preference'), '')
                kaizen_client_type = member.get(column_mapping.get('kaizen_client_type'), '')
                # User ID cell: col 2, 5, 8, 11, 14
                apply_color_to_cell(ws.cell(row=ws.max_row, column=2 + i*3), member.get(column_mapping.get('gender_identity'), ''))
                # Name cell: col 3, 6, 9, 12, 15 - apply bold if same_gender preference, dark red if team_member
                apply_color_to_cell(ws.cell(row=ws.max_row, column=3 + i*3), member.get(column_mapping.get('gender_identity'), ''), gender_pref, kaizen_client_type)
    
    # Write grouped participants
    print(f"Writing {len(grouped)} regular groups to Excel...")
    for group_name, members in grouped.items():
        row = [group_name]
        for i in range(5):
            if i < len(members):
                member = members[i]
                # Determine location display based on residing_ph
                residing_ph = str(member.get(column_mapping.get('residing_ph'), '0')).strip().lower()
                if residing_ph in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
                    # Philippines resident - show city
                    location_display = member.get(column_mapping.get('city'), '')
                else:
                    # International resident - show "State, Country"
                    state = member.get(column_mapping.get('state'), '')
                    country = member.get(column_mapping.get('country'), '')
                    if state and country:
                        location_display = f"{state}, {country}"
                    elif country:
                        location_display = country
                    else:
                        location_display = member.get(column_mapping.get('city'), '')
                
                row.extend([
                    member.get(column_mapping.get('user_id'), ''),
                    member.get(column_mapping.get('name'), ''),
                    location_display
                ])
            else:
                row.extend(["", "", ""])
        # Add extra info for the first member
        member = members[0]
        row.extend([
            member.get(column_mapping.get('gender_identity'), ''),
            member.get(column_mapping.get('sex'), ''),
            member.get(column_mapping.get('residing_ph'), ''),
            member.get(column_mapping.get('gender_preference'), ''),
            member.get(column_mapping.get('country'), ''),
            member.get(column_mapping.get('province'), ''),
            member.get(column_mapping.get('city'), ''),
            member.get(column_mapping.get('state'), '')
        ])
        ws.append(row)
        # Color code user_id and name cells for each member
        for i in range(5):
            if i < len(members):
                member = members[i]
                gender_pref = member.get(column_mapping.get('gender_preference'), '')
                kaizen_client_type = member.get(column_mapping.get('kaizen_client_type'), '')
                apply_color_to_cell(ws.cell(row=ws.max_row, column=2 + i*3), member.get(column_mapping.get('gender_identity'), ''))
                # Apply bold to name if same_gender preference, dark red if team_member
                apply_color_to_cell(ws.cell(row=ws.max_row, column=3 + i*3), member.get(column_mapping.get('gender_identity'), ''), gender_pref, kaizen_client_type)
    
    # Write excluded users (joiningAsStudent=False)
    if excluded_users:
        print(f"Writing {len(excluded_users)} excluded users to Excel...")
        for idx, user in enumerate(excluded_users, 1):
            row = [f"Excluded {idx}"]
            
            # Add user data
            # Determine location display based on residing_ph
            residing_ph = str(user.get(column_mapping.get('residing_ph'), '0')).strip().lower()
            if residing_ph in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
                # Philippines resident - show city
                location_display = user.get(column_mapping.get('city'), '')
            else:
                # International resident - show "State, Country"
                state = user.get(column_mapping.get('state'), '')
                country = user.get(column_mapping.get('country'), '')
                if state and country:
                    location_display = f"{state}, {country}"
                elif country:
                    location_display = country
                else:
                    location_display = user.get(column_mapping.get('city'), '')
            
            row.extend([
                user.get(column_mapping.get('user_id'), ''),
                user.get(column_mapping.get('name'), ''),
                location_display
            ])
            
            # Add empty cells for remaining slots
            for i in range(4):  # 4 more slots (total 5)
                row.extend(["", "", ""])
            
            # Add extra info
            row.extend([
                user.get(column_mapping.get('gender_identity'), ''),
                user.get(column_mapping.get('sex'), ''),
                user.get(column_mapping.get('residing_ph'), ''),
                user.get(column_mapping.get('gender_preference'), ''),
                user.get(column_mapping.get('country'), ''),
                user.get(column_mapping.get('province'), ''),
                user.get(column_mapping.get('city'), ''),
                user.get(column_mapping.get('state'), '')
            ])
            
            ws.append(row)
            print(f"Added excluded user {idx} with user {user.get(column_mapping.get('user_id'), 'Unknown')}")
            
            # Apply formatting (treat as solo)
            gender_pref = user.get(column_mapping.get('gender_preference'), '')
            kaizen_client_type = user.get(column_mapping.get('kaizen_client_type'), '')
            apply_color_to_cell(ws.cell(row=ws.max_row, column=2), user.get(column_mapping.get('gender_identity'), ''))
            apply_color_to_cell(ws.cell(row=ws.max_row, column=3), user.get(column_mapping.get('gender_identity'), ''), gender_pref, kaizen_client_type)
    
    # Check if filename_or_buffer is a string (file path) or BytesIO buffer
    if isinstance(filename_or_buffer, str):
        wb.save(filename_or_buffer)
        print(f"Groups have been saved to '{filename_or_buffer}'.")
    else:
        # It's a BytesIO buffer
        wb.save(filename_or_buffer)
        print("Groups have been saved to buffer.")

def main():
    # Read the merged Excel file
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name='Merged Data')
        print(f"Successfully read merged data with {len(df)} records")
        print(f"Available columns: {list(df.columns)}")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        print("Trying to read as CSV file instead...")
        try:
            df = pd.read_csv(INPUT_FILE)
            print(f"Successfully read CSV file with {len(df)} records")
        except Exception as e2:
            print(f"Error reading CSV file: {e2}")
            return
    
    # Find column mapping
    column_mapping = find_column_mapping(df)
    print(f"Column mapping: {column_mapping}")
    
    # Debug: Check specific columns we're looking for
    print("\nDebug: Checking specific columns:")
    for key in ['accountability_buddies', 'has_accountability_buddies', 'email']:
        if key in column_mapping and column_mapping[key]:
            print(f"  {key}: Found as '{column_mapping[key]}'")
        else:
            print(f"  {key}: NOT FOUND")
    
    # Convert DataFrame to list of dictionaries
    data = df.to_dict('records')
    
    # Debug: Show first few rows to see actual data
    print("\nDebug: First 3 rows of data:")
    for i, row in enumerate(data[:3]):
        print(f"  Row {i}:")
        for key in ['user_id', 'accountability_buddies', 'has_accountability_buddies', 'email']:
            if key in column_mapping and column_mapping[key]:
                value = row.get(column_mapping[key], 'NOT_FOUND')
                print(f"    {key} ({column_mapping[key]}): {value}")
            else:
                print(f"    {key}: Column not mapped")
    
    # Group participants
    solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)
    
    # Save to Excel
    save_to_excel(solo_groups, grouped, OUTPUT_FILE, column_mapping, excluded_users, requested_groups)

if __name__ == "__main__":
    main() 