import pandas as pd
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font

# File paths
INPUT_FILE = 'participants.csv'
OUTPUT_FILE = 'grouped_participants.xlsx'

# Column mapping (0-based index)
COL_NAME = 1
COL_GENDER_IDENTITY = 3  # D
COL_SEX = 7              # H
COL_RESIDING_PH = 8      # I
COL_GENDER_PREF = 10     # K
COL_COUNTRY = 16         # Q
COL_PROVINCE = 17        # R
COL_CITY = 18            # S
COL_STATE = 19           # T
COL_GO_SOLO = 20         # U
COL_USER_ID = 0          # A (assuming user_id is the first column)

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

def get_country_region(country):
    """Get the region for a given country"""
    country = str(country).strip()
    for region, countries in SIMILAR_COUNTRIES.items():
        if country in countries:
            return region
    return 'other'

def merge_small_groups_with_preference_separation(groups_dict, max_group_size=5):
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
        residing_ph = str(member[COL_RESIDING_PH]) == '1'
        if residing_ph:
            province = member[COL_PROVINCE] if len(member) > COL_PROVINCE and member[COL_PROVINCE] else 'Unknown Province'
            key = ("same_gender" if is_same_gender else "no_preference", gender_key, "PH", province)
        else:
            country = member[COL_COUNTRY] if len(member) > COL_COUNTRY and member[COL_COUNTRY] else 'Unknown Country'
            state = member[COL_STATE] if len(member) > COL_STATE and member[COL_STATE] else 'Unknown State'
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
        gender_pref = str(member[COL_GENDER_PREF]).lower()
        if gender_pref == 'same_gender':
            if str(member[COL_GENDER_IDENTITY]).upper() == 'LGBTQ+':
                gender_key = f"lgbtq+_{str(member[COL_SEX]).lower()}"
            else:
                gender_key = str(member[COL_GENDER_IDENTITY]).lower()
            pref_type = 'same_gender'
        else:
            gender_key = 'no_preference'
            pref_type = 'no_preference'
        
        # Separate Philippines from international
        country = member[COL_COUNTRY] if len(member) > COL_COUNTRY and member[COL_COUNTRY] else 'Unknown Country'
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
        country_region = get_country_region(members[0][COL_COUNTRY])
        
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

def apply_color_to_cell(cell, gender_identity, same_gender=None):
    gender_identity = str(gender_identity).lower()
    if gender_identity in GENDER_COLOR:
        cell.fill = PatternFill(start_color=GENDER_COLOR[gender_identity], end_color=GENDER_COLOR[gender_identity], fill_type="solid")
    if same_gender is not None and str(same_gender).lower() == "same_gender":
        cell.font = Font(bold=True)

def group_participants(data):
    solo_groups = []
    grouped = defaultdict(list)
    group_counter = 1
    
    print(f"Total participants: {len(data)}")
    
    # 1. Handle Solo participants
    solo_count = 0
    for row in data:
        if len(row) > COL_GO_SOLO:
            go_solo_value = str(row[COL_GO_SOLO]).strip()
            print(f"User {row[COL_USER_ID]}: Column U = '{go_solo_value}'")
            # Handle both '1' and '1.0' formats
            if go_solo_value == '1' or go_solo_value == '1.0':
                solo_groups.append([row])
                solo_count += 1
                print(f"Added to solo: User {row[COL_USER_ID]}")
    
    print(f"Found {solo_count} solo participants")
    
    # 2. Handle non-solo participants
    non_solo = [row for row in data if len(row) <= COL_GO_SOLO or (str(row[COL_GO_SOLO]).strip() != '1' and str(row[COL_GO_SOLO]).strip() != '1.0')]
    print(f"Non-solo participants: {len(non_solo)}")
    
    # Group by gender preference
    gender_pref_groups = defaultdict(list)
    for row in non_solo:
        gender_pref = str(row[COL_GENDER_PREF]).lower()
        if gender_pref == 'same_gender':
            # Special handling for LGBTQ+
            if str(row[COL_GENDER_IDENTITY]).upper() == 'LGBTQ+':
                gender_key = f"lgbtq+_{str(row[COL_SEX]).lower()}"
            else:
                gender_key = str(row[COL_GENDER_IDENTITY]).lower()
        elif gender_pref == 'no_preference':
            gender_key = 'no_preference'
        else:
            gender_key = 'other'
        gender_pref_groups[gender_key].append(row)
    
    # Now, within each gender group, group by location with hierarchical approach
    for gender_key, rows in gender_pref_groups.items():
        # Split by PH or not
        ph_rows = [r for r in rows if str(r[COL_RESIDING_PH]) == '1']
        non_ph_rows = [r for r in rows if str(r[COL_RESIDING_PH]) == '0']
        
        # Group Philippines participants by Province -> City hierarchy
        province_groups = defaultdict(list)
        for r in ph_rows:
            province = r[COL_PROVINCE] if len(r) > COL_PROVINCE and r[COL_PROVINCE] else 'Unknown Province'
            province_groups[province].append(r)
        
        for province, province_members in province_groups.items():
            # Further group by city within each province
            city_groups = defaultdict(list)
            for r in province_members:
                city = r[COL_CITY] if len(r) > COL_CITY and r[COL_CITY] else 'Unknown City'
                city_groups[city].append(r)
            
            for city, members in city_groups.items():
                # Split into chunks of 5
                for i in range(0, len(members), 5):
                    location_info = f"Province: {province}, City: {city}"
                    grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = members[i:i+5]
                    group_counter += 1
        
        # Group International participants by Country -> State hierarchy
        country_groups = defaultdict(list)
        for r in non_ph_rows:
            country = r[COL_COUNTRY] if len(r) > COL_COUNTRY and r[COL_COUNTRY] else 'Unknown Country'
            country_groups[country].append(r)
        
        for country, country_members in country_groups.items():
            # Further group by state within each country
            state_groups = defaultdict(list)
            for r in country_members:
                state = r[COL_STATE] if len(r) > COL_STATE and r[COL_STATE] else 'Unknown State'
                state_groups[state].append(r)
            
            for state, members in state_groups.items():
                for i in range(0, len(members), 5):
                    location_info = f"Country: {country}, State: {state}"
                    grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = members[i:i+5]
                    group_counter += 1
    
    # Merge small groups with similar countries, but keep same_gender and no_preference separate
    print(f"Before merging: {len(grouped)} groups")
    grouped = merge_small_groups_with_preference_separation(grouped, max_group_size=5)
    print(f"After merging: {len(grouped)} groups")
    
    print(f"Created {len(solo_groups)} solo groups and {len(grouped)} regular groups")
    return solo_groups, grouped

def save_to_excel(solo_groups, grouped, filename_or_buffer):
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
    
    # Write solo groups
    print(f"Writing {len(solo_groups)} solo groups to Excel...")
    for idx, group in enumerate(solo_groups, 1):
        row = [f"Solo {idx}"]
        for i in range(5):
            if i < len(group):
                member = group[i]
                row.extend([member[COL_USER_ID], member[COL_NAME], member[COL_CITY]])
            else:
                row.extend(["", "", ""])
        # Add extra info for the first member
        member = group[0]
        row.extend([
            member[COL_GENDER_IDENTITY], member[COL_SEX], member[COL_RESIDING_PH], member[COL_GENDER_PREF],
            member[COL_COUNTRY], member[COL_PROVINCE], member[COL_CITY], member[COL_STATE]
        ])
        ws.append(row)
        print(f"Added solo group {idx} with user {member[COL_USER_ID]}")
        # Color code user_id and name cells for each member
        for i in range(5):
            if i < len(group):
                member = group[i]
                # User ID cell: col 2, 5, 8, 11, 14
                apply_color_to_cell(ws.cell(row=ws.max_row, column=2 + i*3), member[COL_GENDER_IDENTITY])
                # Name cell: col 3, 6, 9, 12, 15
                apply_color_to_cell(ws.cell(row=ws.max_row, column=3 + i*3), member[COL_GENDER_IDENTITY])
    
    # Write grouped participants
    print(f"Writing {len(grouped)} regular groups to Excel...")
    for group_name, members in grouped.items():
        row = [group_name]
        for i in range(5):
            if i < len(members):
                member = members[i]
                row.extend([member[COL_USER_ID], member[COL_NAME], member[COL_CITY]])
            else:
                row.extend(["", "", ""])
        # Add extra info for the first member
        member = members[0]
        row.extend([
            member[COL_GENDER_IDENTITY], member[COL_SEX], member[COL_RESIDING_PH], member[COL_GENDER_PREF],
            member[COL_COUNTRY], member[COL_PROVINCE], member[COL_CITY], member[COL_STATE]
        ])
        ws.append(row)
        # Color code user_id and name cells for each member
        for i in range(5):
            if i < len(members):
                member = members[i]
                apply_color_to_cell(ws.cell(row=ws.max_row, column=2 + i*3), member[COL_GENDER_IDENTITY])
                apply_color_to_cell(ws.cell(row=ws.max_row, column=3 + i*3), member[COL_GENDER_IDENTITY])
    
    # Check if filename_or_buffer is a string (file path) or BytesIO buffer
    if isinstance(filename_or_buffer, str):
        wb.save(filename_or_buffer)
        print(f"Groups have been saved to '{filename_or_buffer}'.")
    else:
        # It's a BytesIO buffer
        wb.save(filename_or_buffer)
        print("Groups have been saved to buffer.")

def main():
    df = pd.read_csv(INPUT_FILE)
    data = df.values.tolist()
    solo_groups, grouped = group_participants(data)
    save_to_excel(solo_groups, grouped, OUTPUT_FILE)

if __name__ == "__main__":
    main() 