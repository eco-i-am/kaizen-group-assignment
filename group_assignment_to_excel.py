import pandas as pd
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
import re

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
    'email': ['email', 'user_email', 'email_address', 'useremail', 'userEmail'],
    'temporary_team_name': ['temporaryTeamName', 'temporary_team_name', 'temp_team_name', 'team_name'],
    'previous_coach_name': ['previousCoachName', 'previous_coach_name', 'prev_coach_name', 'coach_name']
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
    'middle_east': ['Saudi Arabia', 'United Arab Emirates', 'Qatar', 'Kuwait', 'Bahrain', 'Oman', 'Jordan', 'Lebanon', 'Israel', 'Turkey'],
    'africa': ['South Africa', 'Nigeria', 'Kenya', 'Egypt', 'Morocco', 'Ghana', 'Ethiopia'],
    'oceania': ['Australia', 'New Zealand', 'Fiji', 'Papua New Guinea']
}

# Define timezone regions for international grouping
TIMEZONE_REGIONS = {
    'pst_pdt': ['United States', 'Canada'],  # Pacific Time
    'mst_mdt': ['United States', 'Canada'],  # Mountain Time
    'cst_cdt': ['United States', 'Canada'],  # Central Time
    'est_edt': ['United States', 'Canada'],  # Eastern Time
    'gmt_bst': ['United Kingdom', 'Ireland', 'Portugal','Isle of Man'],  # GMT/BST
    'cet_cest': ['Germany', 'France', 'Italy', 'Spain', 'Netherlands', 'Belgium', 'Switzerland', 'Austria', 'Sweden', 'Norway', 'Denmark', 'Finland', 'Poland', 'Czech Republic', 'Hungary', 'Slovakia', 'Slovenia', 'Croatia', 'Serbia', 'Bosnia', 'Montenegro', 'North Macedonia', 'Albania', 'Kosovo', 'Bulgaria', 'Romania', 'Moldova', 'Ukraine', 'Belarus', 'Lithuania', 'Latvia', 'Estonia'],
    'eet_eest': ['Greece', 'Cyprus', 'Bulgaria', 'Romania', 'Moldova', 'Ukraine', 'Belarus', 'Lithuania', 'Latvia', 'Estonia', 'Finland'],
    'msk': ['Russia'],  # Moscow Time
    'ist': ['India', 'Sri Lanka'],  # India Standard Time
    'pkt': ['Pakistan'],  # Pakistan Time
    'bst': ['Bangladesh'],  # Bangladesh Time
    'jst': ['Japan', 'South Korea'],  # Japan Standard Time
    'cst': ['China', 'Taiwan', 'Hong Kong', 'Macau'],  # China Standard Time
    'sgt': ['Singapore', 'Malaysia', 'Brunei'],  # Singapore Time
    'ict': ['Thailand', 'Vietnam', 'Cambodia', 'Laos'],  # Indochina Time
    'wib': ['Indonesia'],  # Western Indonesian Time
    'aest_aedt': ['Australia'],  # Australian Eastern Time
    'nzst_nzdt': ['New Zealand'],  # New Zealand Time
    'gst': ['United Arab Emirates', 'Oman'],  # Gulf Standard Time
    'ast': ['Saudi Arabia', 'Kuwait', 'Bahrain', 'Qatar'],  # Arabia Standard Time
    'eat': ['Kenya', 'Ethiopia', 'Tanzania', 'Uganda', 'Rwanda', 'Burundi', 'Somalia', 'Djibouti', 'Eritrea'],  # East Africa Time
    'wast_wat': ['Nigeria', 'Ghana', 'Cameroon', 'Chad', 'Central African Republic', 'Gabon', 'Congo', 'DR Congo', 'Angola'],  # West Africa Time
    'sast': ['South Africa', 'Namibia', 'Botswana', 'Zimbabwe', 'Zambia', 'Malawi', 'Mozambique', 'Lesotho', 'Eswatini'],  # South Africa Time
    'est': ['Egypt', 'Libya', 'Sudan', 'South Sudan'],  # Egypt Standard Time
    'pst': ['Mexico'],  # Pacific Standard Time (Mexico)
    'cst': ['Mexico'],  # Central Standard Time (Mexico)
    'est': ['Mexico'],  # Eastern Standard Time (Mexico)
    'cayman_est': ['Cayman Islands'],
    'bermuda_ast': ['Bermuda'],
    # Geographic regions
    'southeast_asia': 'GMT+7',
    'east_asia': 'GMT+8',
    'south_asia': 'GMT+5',   
    'north_america': 'GMT-5', 
    'europe': 'GMT+1',
    'middle_east': 'GMT+3', 
    'africa': 'GMT+2',
    'oceania': 'GMT+10'
}

# GMT offset mapping for timezone labels
GMT_OFFSETS = {
    'pst_pdt': 'GMT-8',
    'mst_mdt': 'GMT-7', 
    'cst_cdt': 'GMT-6',
    'est_edt': 'GMT-5',
    'gmt_bst': 'GMT+0',
    'cet_cest': 'GMT+1',
    'eet_eest': 'GMT+2',
    'msk': 'GMT+3',
    'ist': 'GMT+5:30',
    'pkt': 'GMT+5',
    'bst': 'GMT+6',
    'jst': 'GMT+9',
    'cst': 'GMT+8',
    'sgt': 'GMT+8',
    'ict': 'GMT+7',
    'wib': 'GMT+7',
    'aest_aedt': 'GMT+10',
    'nzst_nzdt': 'GMT+12',
    'gst': 'GMT+4',
    'ast': 'GMT+3',
    'eat': 'GMT+3',
    'wast_wat': 'GMT+1',
    'sast': 'GMT+2',
    'est': 'GMT+2',
    'pst': 'GMT-8',
    'cst': 'GMT-6',
    'est': 'GMT-5',
    'cayman_est': 'GMT-5',
    'bermuda_ast': 'GMT-4',
    # Geographic regions
    'southeast_asia': 'GMT+7',
    'east_asia': 'GMT+8',
    'south_asia': 'GMT+5',   
    'north_america': 'GMT-5', 
    'europe': 'GMT+1',
    'middle_east': 'GMT+3', 
    'africa': 'GMT+2',
    'oceania': 'GMT+10'
}

def get_gmt_offset_value(timezone_region):
    """Get GMT offset as a numeric value for sorting (negative for behind GMT, positive for ahead)"""
    if timezone_region in GMT_OFFSETS:
        offset_str = GMT_OFFSETS[timezone_region]
        # Extract numeric value from GMT+X or GMT-X or GMT+X:Y
        if 'GMT+' in offset_str:
            # Handle half-hour offsets like GMT+5:30
            parts = offset_str.replace('GMT+', '').split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            return hours + (minutes / 60.0)
        else:
            # Handle whole hour offsets
            return int(offset_str.replace('GMT+', '').replace('GMT-', '-'))
    return 0  # Default for unknown timezones

def normalize_country_name(country):
    if not country:
        return ''
    country = str(country).strip().lower().replace('.', '')
    country = re.sub(r'\s+', ' ', country)  # collapse multiple spaces
    return country

def extract_country_from_field(field_value):
    if not field_value:
        return field_value
    field_str = str(field_value).strip()
    if field_str.lower() in ['nan', 'none', '[]']:
        return field_str
    if ',' in field_str:
        parts = [part.strip() for part in field_str.split(',')]
        return parts[-1]
    # Handle abbreviations and variations
    country_mappings = {
        'uae': 'united arab emirates',
        'u a e': 'united arab emirates',
        'u.a.e.': 'united arab emirates',
        'united arab emirates': 'united arab emirates',
        'usa': 'united states',
        'us': 'united states',
        'u s a': 'united states',
        'u.s.a.': 'united states',
        'uk': 'united kingdom',
        'u k': 'united kingdom',
        'u.k.': 'united kingdom',
        'north ame': 'united states',
        'north america': 'united states',
        'bermuda': 'bermuda',
        'cayman islands': 'cayman islands',
    }
    norm = normalize_country_name(field_str)
    if norm in country_mappings:
        return country_mappings[norm]
    return field_str

def get_timezone_region(country, state=None):
    original_country = country
    country = extract_country_from_field(country)
    norm_country = normalize_country_name(country)
    print(f"DEBUG: get_timezone_region - Original: {original_country} -> Extracted: '{country}' -> Normalized: '{norm_country}'")
    # Special handling for US states with different timezones
    if norm_country == 'united states' and state:
        state = str(state).strip().lower()
        if state in ['california', 'washington', 'oregon', 'nevada', 'alaska']:
            return 'pst_pdt'
        elif state in ['colorado', 'utah', 'wyoming', 'montana', 'idaho', 'new mexico', 'arizona']:
            return 'mst_mdt'
        elif state in ['texas', 'oklahoma', 'kansas', 'nebraska', 'south dakota', 'north dakota', 'minnesota', 'iowa', 'missouri', 'arkansas', 'louisiana', 'mississippi', 'alabama', 'illinois', 'wisconsin', 'michigan', 'indiana', 'kentucky', 'tennessee']:
            return 'cst_cdt'
        elif state in ['new york', 'new jersey', 'pennsylvania', 'ohio', 'indiana', 'michigan', 'illinois', 'wisconsin', 'minnesota', 'iowa', 'missouri', 'arkansas', 'louisiana', 'mississippi', 'alabama', 'georgia', 'florida', 'south carolina', 'north carolina', 'virginia', 'west virginia', 'maryland', 'delaware', 'new hampshire', 'vermont', 'maine', 'massachusetts', 'rhode island', 'connecticut']:
            return 'est_edt'
    # Check timezone regions with case-insensitive matching
    for timezone, countries in TIMEZONE_REGIONS.items():
        for mapped_country in countries:
            if norm_country == normalize_country_name(mapped_country):
                print(f"DEBUG: Found timezone match - {norm_country} -> {timezone}")
                return timezone
    # Fallback to geographic regions with case-insensitive matching
    for region, countries in SIMILAR_COUNTRIES.items():
        for mapped_country in countries:
            if norm_country == normalize_country_name(mapped_country):
                print(f"DEBUG: Found geographic match - {norm_country} -> {region}")
                return region
    print(f"DEBUG: No match found for country '{norm_country}' - returning 'other'")
    return 'other'

def get_timezone_label(timezone_region):
    """Get timezone label with GMT offset first"""
    if timezone_region in GMT_OFFSETS:
        return f"{GMT_OFFSETS[timezone_region]} => {timezone_region.upper()}"
    elif timezone_region in SIMILAR_COUNTRIES:
        return f"{timezone_region.replace('_', ' ').title()}"
    else:
        return timezone_region

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
    
    # Second pass: collect participants with temporary team names (even without accountability buddies)
    team_name_participants = []
    for row in data:
        temporary_team_name = get_value(row, 'temporary_team_name', '')
        user_id = get_value(row, 'user_id', 'Unknown')
        
        # Check if user has a valid temporary team name
        has_team_name = temporary_team_name and str(temporary_team_name).strip() not in ['', 'None', 'nan']
        
        if has_team_name:
            # Check if this user is not already in accountability_participants
            user_email = get_value(row, 'email', '').lower().strip()
            is_in_accountability = any(
                get_value(acc_user, 'email', '').lower().strip() == user_email 
                for acc_user in accountability_participants
            )
            
            if not is_in_accountability:
                team_name_participants.append(row)
                print(f"User {user_id}: temporary_team_name='{temporary_team_name}' (no accountability buddies)")
    
    print(f"Found {len(team_name_participants)} participants with team names but no accountability buddies")
    
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
                    
                    # Check if any requested buddies are already in existing groups
                    buddies_in_existing_groups = []
                    available_buddies = []
                    existing_group_with_buddies = None
                    
                    for email in requested_emails:
                        if email in email_to_user:
                            buddy_user = email_to_user[email]
                            buddy_email = get_value(buddy_user, 'email', '').lower().strip()
                            
                            # Check if this buddy is already assigned to a requested group
                            if buddy_email in assigned_users:
                                buddies_in_existing_groups.append(email)
                                buddy_user_id = get_value(buddy_user, 'user_id', 'Unknown')
                                print(f"  Buddy {email} -> User {buddy_user_id}: already assigned to another requested group")
                                
                                # Find which existing group contains this buddy
                                for i, existing_group in enumerate(requested_groups):
                                    existing_emails = [get_value(member, 'email', '').lower().strip() for member in existing_group]
                                    if buddy_email in existing_emails:
                                        existing_group_with_buddies = i
                                        break
                            else:
                                available_buddies.append(email)
                        else:
                            print(f"  Missing buddy: {email}")
                    
                    # If buddies are in existing groups, add user to that group
                    if buddies_in_existing_groups and existing_group_with_buddies is not None:
                        existing_group = requested_groups[existing_group_with_buddies]
                        
                        # Check if the group has space (max 5 members)
                        if len(existing_group) < 5:
                            existing_group.append(participant)
                            assigned_users.add(participant_email)
                            accountability_count += 1
                            
                            existing_group_emails = [get_value(member, 'email', '').lower().strip() for member in existing_group]
                            print(f"Added User {user_id} to existing Requested Group {existing_group_with_buddies + 1}:")
                            print(f"  Existing group members: {existing_group_emails}")
                            print(f"  Group size: {len(existing_group)} members")
                            print(f"  Requested emails: {requested_emails}")
                            print(f"  Buddies in existing group: {buddies_in_existing_groups}")
                        else:
                            print(f"Cannot add User {user_id} to existing group: group is full (5 members)")
                            print(f"  Requested emails: {requested_emails}")
                            print(f"  Buddies in existing groups: {buddies_in_existing_groups}")
                    
                    # Only create a new group if there are available buddies and no existing group to join
                    elif available_buddies:
                        # Build the group: requester + all available buddies
                        group_members = [participant]  # Start with the requester
                        assigned_users.add(participant_email)  # Mark requester as assigned
                        
                        found_buddies = []
                        missing_buddies = []
                        
                        for email in available_buddies:
                            buddy_user = email_to_user[email]
                            buddy_email = get_value(buddy_user, 'email', '').lower().strip()
                            
                            group_members.append(buddy_user)
                            assigned_users.add(buddy_email)  # Mark buddy as assigned
                            found_buddies.append(email)
                            buddy_user_id = get_value(buddy_user, 'user_id', 'Unknown')
                            print(f"  Found buddy {email} -> User {buddy_user_id}")
                        
                        # Add missing buddies to the list
                        for email in requested_emails:
                            if email not in email_to_user:
                                missing_buddies.append(email)
                                print(f"  Missing buddy: {email}")
                        
                        if group_members:
                            requested_groups.append(group_members)
                            accountability_count += len(group_members)
                            print(f"Created new Requested Group with {len(group_members)} members:")
                            print(f"  Requester: User {user_id}")
                            print(f"  Requested emails: {requested_emails}")
                            print(f"  Available buddies: {available_buddies}")
                            print(f"  Found buddies: {found_buddies}")
                            if missing_buddies:
                                print(f"  Missing buddies: {missing_buddies}")
                            if buddies_in_existing_groups:
                                print(f"  Buddies already in existing groups: {buddies_in_existing_groups}")
                    else:
                        print(f"Skipping User {user_id}: no available buddies and no existing group to join")
                        print(f"  Requested emails: {requested_emails}")
                        print(f"  Buddies in existing groups: {buddies_in_existing_groups}")
    
    print(f"Created {len(requested_groups)} requested groups with {accountability_count} participants")
    print(f"Total users assigned to requested groups: {len(assigned_users)}")
    
    # Process team name participants and group them by team name
    if team_name_participants:
        print(f"\nProcessing {len(team_name_participants)} participants with team names...")
        
        # Group team name participants by their team name
        team_groups = defaultdict(list)
        for participant in team_name_participants:
            team_name = get_value(participant, 'temporary_team_name', '').strip()
            user_id = get_value(participant, 'user_id', 'Unknown')
            user_email = get_value(participant, 'email', '').lower().strip()
            
            # Skip if already assigned to a requested group
            if user_email in assigned_users:
                print(f"Skipping User {user_id} ({user_email}): already assigned to a requested group")
                continue
            
            team_groups[team_name].append(participant)
            print(f"User {user_id}: assigned to team '{team_name}'")
        
        # Create requested groups for each team
        for team_name, team_members in team_groups.items():
            if team_members:
                print(f"\nProcessing team '{team_name}' with {len(team_members)} members")
                
                # Create groups of up to 5 members from this team
                i = 0
                team_group_counter = 1
                while i < len(team_members):
                    group_members = team_members[i:i+5]
                    
                    # Mark all members as assigned
                    for member in group_members:
                        member_email = get_value(member, 'email', '').lower().strip()
                        assigned_users.add(member_email)
                    
                    requested_groups.append(group_members)
                    accountability_count += len(group_members)
                    
                    print(f"Created Team Group '{team_name} {team_group_counter}' with {len(group_members)} members")
                    for member in group_members:
                        member_id = get_value(member, 'user_id', 'Unknown')
                        member_name = get_value(member, 'name', 'Unknown')
                        print(f"  - User {member_id}: {member_name}")
                    
                    i += 5
                    team_group_counter += 1
    
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
        
        # Group International participants by Country -> State hierarchy with timezone-based small group merging
        country_groups = defaultdict(list)
        for r in non_ph_rows:
            country = get_value(r, 'country', 'Unknown Country')
            country_groups[country].append(r)
        
        print(f"  International countries found: {list(country_groups.keys())}")
        
        # First pass: create complete groups (5 members) from each country/state
        remaining_international = []
        
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
                
                # Create complete groups of 5 from this state
                i = 0
                while i + 5 <= len(members):
                    group_members = members[i:i+5]
                    location_info = f"Country: {country}, State: {state}"
                    grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                    print(f"          Created Group {group_counter} with {len(group_members)} members (complete group)")
                    group_counter += 1
                    i += 5
                
                # Keep remaining members for timezone-based grouping
                if i < len(members):
                    remaining_members = members[i:]
                    remaining_international.extend(remaining_members)
                    print(f"          Remaining from {state}: {len(remaining_members)} members")
        
        # Second pass: combine remaining members by timezone regions
        if remaining_international:
            print(f"        Processing {len(remaining_international)} remaining international members by timezone")
            
            # Sort remaining international members by GMT offset
            remaining_international.sort(key=lambda m: get_gmt_offset_value(get_timezone_region(get_value(m, 'country', 'Unknown Country'), get_value(m, 'state', 'Unknown State'))))
            
            # Group remaining members by timezone region
            timezone_groups = defaultdict(list)
            for member in remaining_international:
                country = get_value(member, 'country', 'Unknown Country')
                state = get_value(member, 'state', 'Unknown State')
                timezone_region = get_timezone_region(country, state)
                timezone_groups[timezone_region].append(member)
            
            print(f"        Timezone regions found: {list(timezone_groups.keys())}")
            
            # Sort timezone regions by GMT offset before processing
            sorted_timezone_regions = sorted(timezone_groups.keys(), key=get_gmt_offset_value)
            print(f"        Timezone regions sorted by GMT: {sorted_timezone_regions}")
            
            # Process each timezone region
            for timezone_region in sorted_timezone_regions:
                members = timezone_groups[timezone_region]
                print(f"          Timezone {timezone_region}': {len(members)} participants")
                
                # Create groups of up to 5 from this timezone region
                i = 0
                while i < len(members):
                    group_members = members[i:i+5]
                    timezone_label = get_timezone_label(timezone_region)
                    location_info = f"Timezone: {timezone_label}"
                    grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                    print(f"            Created Group {group_counter} with {len(group_members)} members (timezone-based)")
                    group_counter += 1
                    i += 5
    
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
        "User ID 6", "Name 6", "City 6",
        "User ID 7", "Name 7", "City 7",
        "Gender Identity", "Sex", "Residing in PH", "Gender Preference", "Country", "Province", "City", "State",
        "Temporary Team Name", "Previous Coach Name"
    ])
    
    # Write requested groups (accountability buddies)
    if requested_groups:
        print(f"Writing {len(requested_groups)} requested groups to Excel...")
        # Sort requested groups by descending order of number of users
        sorted_requested_groups = sorted(requested_groups, key=lambda g: len(g), reverse=True)
        green_fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
        group_row_indices = []
        for idx, group in enumerate(sorted_requested_groups, 1):
            # --- SORT small group members ---
            if len(group) < 7:
                group = sorted(group, key=lambda m: (
                    m.get(column_mapping.get('user_id'), ''),
                    m.get(column_mapping.get('name'), ''),
                    m.get(column_mapping.get('city'), '')
                ))
            
            # Determine if this is a team group or accountability buddy group
            first_member = group[0]
            team_name = first_member.get(column_mapping.get('temporary_team_name'), '')
            has_accountability_buddies = first_member.get(column_mapping.get('has_accountability_buddies'), '0')
            
            # Check if all members have the same team name and no accountability buddies
            all_same_team = all(
                member.get(column_mapping.get('temporary_team_name'), '') == team_name 
                for member in group
            )
            all_no_accountability = all(
                str(member.get(column_mapping.get('has_accountability_buddies'), '0')).strip().lower() not in ['1', '1.0', 'true', 'yes']
                for member in group
            )
            
            if all_same_team and all_no_accountability and team_name:
                # This is a team group
                row = [f"Team Group {idx} - {team_name} ({len(group)} members)"]
            else:
                # This is an accountability buddy group
                row = [f"Requested Group {idx} ({len(group)} members)"]
            
            # Add user data for each member (up to 7)
            for i in range(7):
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
            
            # Collect all team names from group members
            team_names = []
            for group_member in group:
                team_name = group_member.get(column_mapping.get('temporary_team_name'), '')
                if team_name and str(team_name).strip() not in ['', 'None', 'nan']:
                    team_names.append(str(team_name).strip())
            
            # Combine team names with "/" separator if they're different
            combined_team_names = ' / '.join(sorted(set(team_names))) if team_names else ''
            
            # Collect all coach names from group members
            coach_names = []
            for group_member in group:
                coach_name = group_member.get(column_mapping.get('previous_coach_name'), '')
                if coach_name and str(coach_name).strip() not in ['', 'None', 'nan']:
                    coach_names.append(str(coach_name).strip())
            
            # Combine coach names with "/" separator if they're different
            combined_coach_names = ' / '.join(sorted(set(coach_names))) if coach_names else ''
            
            row.extend([
                member.get(column_mapping.get('gender_identity'), ''),
                member.get(column_mapping.get('sex'), ''),
                member.get(column_mapping.get('residing_ph'), ''),
                member.get(column_mapping.get('gender_preference'), ''),
                member.get(column_mapping.get('country'), ''),
                member.get(column_mapping.get('province'), ''),
                member.get(column_mapping.get('city'), ''),
                member.get(column_mapping.get('state'), ''),
                combined_team_names,
                combined_coach_names
            ])
            
            ws.append(row)
            group_row_indices.append((ws.max_row, len(group)))
            print(f"Added requested group {idx} with {len(group)} members")
            
            # Apply formatting
            for i in range(7):
                if i < len(group):
                    member = group[i]
                    gender_pref = member.get(column_mapping.get('gender_preference'), '')
                    kaizen_client_type = member.get(column_mapping.get('kaizen_client_type'), '')
                    apply_color_to_cell(ws.cell(row=ws.max_row, column=2 + i*3), member.get(column_mapping.get('gender_identity'), ''))
                    apply_color_to_cell(ws.cell(row=ws.max_row, column=3 + i*3), member.get(column_mapping.get('gender_identity'), ''), gender_pref, kaizen_client_type)
        
        # After all requested groups are written, apply green highlight to group name cell if group has 5 or more members
        for row_idx, group_size in group_row_indices:
            if group_size >= 5:
                ws.cell(row=row_idx, column=1).fill = green_fill
    
    # Write solo groups
    print(f"Writing {len(solo_groups)} solo groups to Excel...")
    for idx, group in enumerate(solo_groups, 1):
        # --- SORT small group members ---
        if len(group) < 7:
            group = sorted(group, key=lambda m: (
                m.get(column_mapping.get('user_id'), ''),
                m.get(column_mapping.get('name'), ''),
                m.get(column_mapping.get('city'), '')
            ))
        row = [f"Solo {idx}"]
        for i in range(7):
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
            member.get(column_mapping.get('state'), ''),
            member.get(column_mapping.get('temporary_team_name'), ''),
            member.get(column_mapping.get('previous_coach_name'), '')
        ])
        ws.append(row)
        print(f"Added solo group {idx} with user {member.get(column_mapping.get('user_id'), 'Unknown')}")
        # Color code user_id and name cells for each member
        for i in range(7):
            if i < len(group):
                member = group[i]
                gender_pref = member.get(column_mapping.get('gender_preference'), '')
                kaizen_client_type = member.get(column_mapping.get('kaizen_client_type'), '')
                apply_color_to_cell(ws.cell(row=ws.max_row, column=2 + i*3), member.get(column_mapping.get('gender_identity'), ''))
                apply_color_to_cell(ws.cell(row=ws.max_row, column=3 + i*3), member.get(column_mapping.get('gender_identity'), ''), gender_pref, kaizen_client_type)
    
    # Write grouped participants
    print(f"Writing {len(grouped)} regular groups to Excel...")
    # Track regular groups with 5 or more members for highlighting
    regular_group_row_indices = []
    for group_name, members in grouped.items():
        # --- SORT small group members ---
        if len(members) < 7:
            members = sorted(members, key=lambda m: (
                m.get(column_mapping.get('user_id'), ''),
                m.get(column_mapping.get('name'), ''),
                m.get(column_mapping.get('city'), '')
            ))
        row = [group_name]
        for i in range(7):
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
            member.get(column_mapping.get('state'), ''),
            member.get(column_mapping.get('temporary_team_name'), ''),
            member.get(column_mapping.get('previous_coach_name'), '')
        ])
        ws.append(row)
        
        # Check if group has 5 or more members and all members have the same location
        should_highlight = False
        if len(members) >= 5:
            # Check if all members have the same location
            first_member = members[0]
            first_residing_ph = str(first_member.get(column_mapping.get('residing_ph'), '0')).strip().lower()
            
            if first_residing_ph in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
                # Philippines residents - check if all have same city
                first_city = str(first_member.get(column_mapping.get('city'), '')).strip()
                all_same_location = all(
                    str(member.get(column_mapping.get('city'), '')).strip() == first_city 
                    for member in members[:7]
                )
            else:
                # International residents - check if all have same state and country
                first_state = str(first_member.get(column_mapping.get('state'), '')).strip()
                first_country = str(first_member.get(column_mapping.get('country'), '')).strip()
                all_same_location = all(
                    str(member.get(column_mapping.get('state'), '')).strip() == first_state and
                    str(member.get(column_mapping.get('country'), '')).strip() == first_country
                    for member in members[:7]
                )
            
            if all_same_location:
                regular_group_row_indices.append(ws.max_row)
        
        # Color code user_id and name cells for each member
        for i in range(7):
            if i < len(members):
                member = members[i]
                gender_pref = member.get(column_mapping.get('gender_preference'), '')
                kaizen_client_type = member.get(column_mapping.get('kaizen_client_type'), '')
                apply_color_to_cell(ws.cell(row=ws.max_row, column=2 + i*3), member.get(column_mapping.get('gender_identity'), ''))
                # Apply bold to name if same_gender preference, dark red if team_member
                apply_color_to_cell(ws.cell(row=ws.max_row, column=3 + i*3), member.get(column_mapping.get('gender_identity'), ''), gender_pref, kaizen_client_type)
    
    # Apply highlighting to regular groups with 5 or more members and same location
    if regular_group_row_indices:
        # Use a different color for regular groups with 5 or more members and same location (light blue)
        regular_group_fill = PatternFill(start_color="87CEEB", end_color="87CEEB", fill_type="solid")
        for row_idx in regular_group_row_indices:
            ws.cell(row=row_idx, column=1).fill = regular_group_fill
    
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
            
            # Add empty cells for remaining slots (to fill up to 7 members)
            for i in range(6):  # 6 more slots (total 7)
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
                user.get(column_mapping.get('state'), ''),
                user.get(column_mapping.get('temporary_team_name'), ''),
                user.get(column_mapping.get('previous_coach_name'), '')
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