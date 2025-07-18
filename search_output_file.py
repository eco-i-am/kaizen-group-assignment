import pandas as pd

def search_output_file():
    """Search the output file more thoroughly"""
    
    print("🔍 SEARCHING OUTPUT FILE THOROUGHLY")
    print("=" * 50)
    
    # Read the output Excel file
    OUTPUT_FILE = 'grouped_participants.xlsx'
    
    try:
        df = pd.read_excel(OUTPUT_FILE, sheet_name='Grouped Members')
        print(f"✅ Successfully read output file with {len(df)} rows")
    except Exception as e:
        print(f"❌ Error reading output file: {e}")
        return
    
    # Print column names to understand the structure
    print(f"\n📋 COLUMN NAMES:")
    for i, col in enumerate(df.columns):
        print(f"  {i}: {col}")
    
    # Search for our users in all columns
    print(f"\n🔍 SEARCHING FOR OUR USERS:")
    
    al_baljon_found = False
    mark_lester_found = False
    mark_anthony_found = False
    
    for index, row in df.iterrows():
        group_name = row['Group Name']
        
        # Check all columns for our user IDs
        for col in df.columns:
            if 'User ID' in col:
                user_id = row[col]
                if pd.notna(user_id):
                    user_id_str = str(user_id).strip()
                    
                    if user_id_str == '1754':  # Al Baljon
                        al_baljon_found = True
                        print(f"✅ Found Al Baljon (ID: 1754) in {group_name} - Column: {col}")
                    
                    elif user_id_str == '1710':  # Mark Lester
                        mark_lester_found = True
                        print(f"✅ Found Mark Lester (ID: 1710) in {group_name} - Column: {col}")
                    
                    elif user_id_str == '2013':  # Mark Anthony
                        mark_anthony_found = True
                        print(f"✅ Found Mark Anthony (ID: 2013) in {group_name} - Column: {col}")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Al Baljon found: {al_baljon_found}")
    print(f"  Mark Lester found: {mark_lester_found}")
    print(f"  Mark Anthony found: {mark_anthony_found}")
    
    # Also search for any group with "3 members" since we expect them to be together
    print(f"\n🔍 SEARCHING FOR GROUPS WITH 3 MEMBERS:")
    for index, row in df.iterrows():
        group_name = row['Group Name']
        if '3 members' in str(group_name):
            print(f"  Found group: {group_name}")
            
            # Check what users are in this group
            for col in df.columns:
                if 'User ID' in col:
                    user_id = row[col]
                    if pd.notna(user_id):
                        user_id_str = str(user_id).strip()
                        name_col = col.replace('User ID', 'Name')
                        if name_col in df.columns:
                            name = row[name_col]
                            print(f"    User {user_id_str}: {name}")

if __name__ == "__main__":
    search_output_file() 