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

def format_location_display(member, column_mapping):
    """Format location display based on residing_ph status"""
    residing_ph = str(member.get(column_mapping.get('residing_ph'), '0')).strip().lower()
    
    if residing_ph in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
        # Philippines resident - show "city, province" format
        city = member.get(column_mapping.get('city'), '')
        province = member.get(column_mapping.get('province'), '')
        
        # Use "MM" as acronym for Metro Manila
        if province and province.lower() == 'metro manila':
            province = 'MM'
        
        if city and province:
            return f"{city}, {province}"
        elif city:
            return city
        elif province:
            return province
        else:
            return ''
    else:
        # International resident - show "State, Country"
        state = member.get(column_mapping.get('state'), '')
        country = member.get(column_mapping.get('country'), '')
        if state and country:
            return f"{state}, {country}"
        elif country:
            return country
        else:
            return member.get(column_mapping.get('city'), '')

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
            # For same_gender preference, use biological sex to ensure male/female separation
            sex = str(get_value(row, 'sex', '')).lower()
            gender_identity = str(get_value(row, 'gender_identity', '')).upper()
            
            if gender_identity == 'LGBTQ+':
                # LGBTQ+ participants are grouped by their biological sex for same_gender preference
                gender_key = f"lgbtq+_{sex}"
            else:
                # Use biological sex for strict male/female separation
                gender_key = sex
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
            # Normalize province name
            province_norm = province.strip().lower() if isinstance(province, str) else str(province).strip().lower()
            province_groups[province_norm].append(r)
        
        print(f"  Philippines provinces found: {list(province_groups.keys())}")
        
        for province_norm, province_members in province_groups.items():
            # Use the original province name from the first member for display
            province = get_value(province_members[0], 'province', 'Unknown Province')
            print(f"    Province '{province}': {len(province_members)} participants")
            # Further group by city within each province
            city_groups = defaultdict(list)
            for r in province_members:
                city = get_value(r, 'city', 'Unknown City')
                # Normalize city name
                city_norm = city.strip().lower() if isinstance(city, str) else str(city).strip().lower()
                city_groups[city_norm].append(r)
            
            print(f"      Cities in {province}: {[get_value(city_groups[city][0], 'city', 'Unknown City') for city in city_groups.keys()]}")
            
            # --- SORT CITIES ALPHABETICALLY ---
            sorted_city_names = sorted(city_groups.keys())
            print(f"      Cities sorted alphabetically: {sorted_city_names}")
            
            # --- NEW LOGIC: Prioritize same-city groups from entire province pool ---
            # Collect all participants from this province
            all_province_members = []
            for city_norm in sorted_city_names:  # Use sorted city names
                members = city_groups[city_norm]
                all_province_members.extend(members)
                print(f"        City '{city_norm}' (normalized): {len(members)} participants")
            
            print(f"        Total participants in {province}: {len(all_province_members)}")
            
            # Group by city within the province
            city_members = defaultdict(list)
            for member in all_province_members:
                city = get_value(member, 'city', 'Unknown City')
                city_norm = city.strip().lower() if isinstance(city, str) else str(city).strip().lower()
                city_members[city_norm].append(member)
            
            # First, create complete groups (5 members) from each city
            remaining_by_city = {}
            for city_norm, members in city_members.items():
                print(f"          Processing {city_norm}: {len(members)} participants")
                
                # Create complete groups of 5 from this city
                i = 0
                while i + 5 <= len(members):
                    group_members = members[i:i+5]
                    location_info = f"Province: {province}, City: {city_norm}"
                    grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                    print(f"            Created Group {group_counter} with {len(group_members)} members (same city)")
                    group_counter += 1
                    i += 5
                
                # Keep remaining members from this city
                if i < len(members):
                    remaining_by_city[city_norm] = members[i:]
                    print(f"            Remaining from {city_norm}: {len(members[i:])} members")
            
            # Now handle remaining members - prioritize same-city groups
            if remaining_by_city:
                print(f"        Processing remaining members from {province}")
                
                # First, try to form same-city groups from remaining members
                for city_norm, members in list(remaining_by_city.items()):
                    if len(members) >= 5:
                        # Can form a complete group from this city
                        group_members = members[:5]
                        location_info = f"Province: {province}, City: {city_norm}"
                        grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                        print(f"            Created Group {group_counter} with {len(group_members)} members (same city, from remaining)")
                        group_counter += 1
                        remaining_by_city[city_norm] = members[5:]
                    elif len(members) == 0:
                        del remaining_by_city[city_norm]
                
                # Collect all final remaining members (less than 5 per city)
                final_remaining = []
                for members in remaining_by_city.values():
                    final_remaining.extend(members)
                
                # Create mixed-city groups from final remaining - keep city-units together
                if final_remaining:
                    print(f"        Creating mixed-city groups from {len(final_remaining)} final remaining members (city-units kept together)")
                    # Group final remaining by city - use remaining_by_city directly
                    final_by_city = []
                    for city, members in remaining_by_city.items():
                        if members:  # Only add non-empty city units
                            final_by_city.append(members)
                    
                    print(f"        City units to combine: {[len(unit) for unit in final_by_city]}")
                    
                    # Greedily combine city-units into groups of up to 5, never splitting a city-unit
                    i = 0
                    while i < len(final_by_city):
                        group = []
                        while i < len(final_by_city) and len(group) + len(final_by_city[i]) <= 5:
                            group.extend(final_by_city[i])
                            i += 1
                        if group:
                            # Check if all from same city
                            cities_in_group = set()
                            for member in group:
                                city = get_value(member, 'city', 'Unknown City')
                                cities_in_group.add(city.strip().lower() if isinstance(city, str) else str(city).strip().lower())
                            if len(cities_in_group) == 1:
                                city_name = get_value(group[0], 'city', 'Unknown City')
                                location_info = f"Province: {province}, City: {city_name}"
                                print(f"            Created Group {group_counter} with {len(group)} members (same city, city-unit)")
                            else:
                                location_info = f"Province: {province} (mixed cities)"
                                print(f"            Created Group {group_counter} with {len(group)} members (mixed cities, city-units)")
                            grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group
                            group_counter += 1
            # --- END NEW LOGIC ---
        
        # Group International participants by Country -> State hierarchy (unchanged)
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
    
    # No merging of small groups - keep all groups as created
    print(f"Created {len(grouped)} regular groups (no merging)")
    
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
            # --- SORT small group members ---
            if len(group) < 5:
                group = sorted(group, key=lambda m: (
                    m.get(column_mapping.get('user_id'), ''),
                    m.get(column_mapping.get('name'), ''),
                    m.get(column_mapping.get('city'), '')
                ))
            row = [f"Requested Group {idx}"]
            
            # Add user data for each member
            for i in range(5):
                if i < len(group):
                    member = group[i]
                    location_display = format_location_display(member, column_mapping)
                    
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
        # --- SORT small group members ---
        if len(group) < 5:
            group = sorted(group, key=lambda m: (
                m.get(column_mapping.get('user_id'), ''),
                m.get(column_mapping.get('name'), ''),
                m.get(column_mapping.get('city'), '')
            ))
        row = [f"Solo {idx}"]
        for i in range(5):
            if i < len(group):
                member = group[i]
                location_display = format_location_display(member, column_mapping)
                
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
        # --- SORT small group members ---
        if len(members) < 5:
            members = sorted(members, key=lambda m: (
                m.get(column_mapping.get('user_id'), ''),
                m.get(column_mapping.get('name'), ''),
                m.get(column_mapping.get('city'), '')
            ))
        row = [group_name]
        for i in range(5):
            if i < len(members):
                member = members[i]
                location_display = format_location_display(member, column_mapping)
                
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
            location_display = format_location_display(user, column_mapping)
            
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
    # --- SORTING STEP: Sort by province, city, gender_preference, gender_identity, user_id if columns exist ---
    sort_columns = []
    for col_key in ['province', 'city', 'gender_preference', 'gender_identity', 'user_id']:
        col_name = column_mapping.get(col_key)
        if col_name and col_name in df.columns:
            sort_columns.append(col_name)
    if sort_columns:
        df = df.sort_values(by=sort_columns)
        print(f"Sorted data by: {sort_columns}")
    else:
        print("No sort columns found; skipping sorting step.")
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