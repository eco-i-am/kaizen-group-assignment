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
    
    # Now, within each gender group, group by location
    for gender_key, rows in gender_pref_groups.items():
        # Split by PH or not
        ph_rows = [r for r in rows if str(r[COL_RESIDING_PH]) == '1']
        non_ph_rows = [r for r in rows if str(r[COL_RESIDING_PH]) == '0']
        
        # Group PH by city
        city_groups = defaultdict(list)
        for r in ph_rows:
            city = r[COL_CITY] if len(r) > COL_CITY else 'Unknown'
            city_groups[city].append(r)
        
        for city, members in city_groups.items():
            # Split into chunks of 5
            for i in range(0, len(members), 5):
                grouped[f"Group {group_counter} ({gender_key}, City: {city})"] = members[i:i+5]
                group_counter += 1
        
        # Group non-PH by state
        state_groups = defaultdict(list)
        for r in non_ph_rows:
            state = r[COL_STATE] if len(r) > COL_STATE else 'Unknown'
            state_groups[state].append(r)
        
        for state, members in state_groups.items():
            for i in range(0, len(members), 5):
                grouped[f"Group {group_counter} ({gender_key}, State: {state})"] = members[i:i+5]
                group_counter += 1
    
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