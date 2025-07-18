import pandas as pd

def verify_three_users():
    """Verify that Al Baljon, Mark Lester, and Mark Anthony are in the same group"""
    
    print("🔍 VERIFYING THREE USERS ARE IN SAME GROUP")
    print("=" * 50)
    
    # Read the output Excel file
    OUTPUT_FILE = 'grouped_participants.xlsx'
    
    try:
        df = pd.read_excel(OUTPUT_FILE, sheet_name='Grouped Members')
        print(f"✅ Successfully read output file with {len(df)} rows")
    except Exception as e:
        print(f"❌ Error reading output file: {e}")
        return
    
    # Look for our three users
    al_baljon_found = False
    mark_lester_found = False
    mark_anthony_found = False
    
    al_baljon_group = None
    mark_lester_group = None
    mark_anthony_group = None
    
    for index, row in df.iterrows():
        group_name = row['Group Name']
        
        # Check all user ID columns
        for i in range(1, 8):  # User ID 1 through User ID 7
            user_id_col = f'User ID {i}'
            if user_id_col in df.columns:
                user_id = row[user_id_col]
                if pd.notna(user_id):
                    user_id_str = str(user_id).strip()
                    
                    if user_id_str == '1754':  # Al Baljon
                        al_baljon_found = True
                        al_baljon_group = group_name
                        print(f"✅ Found Al Baljon (ID: 1754) in {group_name}")
                    
                    elif user_id_str == '1710':  # Mark Lester
                        mark_lester_found = True
                        mark_lester_group = group_name
                        print(f"✅ Found Mark Lester (ID: 1710) in {group_name}")
                    
                    elif user_id_str == '2013':  # Mark Anthony
                        mark_anthony_found = True
                        mark_anthony_group = group_name
                        print(f"✅ Found Mark Anthony (ID: 2013) in {group_name}")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Al Baljon found: {al_baljon_found}")
    print(f"  Mark Lester found: {mark_lester_found}")
    print(f"  Mark Anthony found: {mark_anthony_found}")
    
    if all([al_baljon_found, mark_lester_found, mark_anthony_found]):
        print(f"\n🔍 GROUP COMPARISON:")
        print(f"  Al Baljon group: {al_baljon_group}")
        print(f"  Mark Lester group: {mark_lester_group}")
        print(f"  Mark Anthony group: {mark_anthony_group}")
        
        if al_baljon_group == mark_lester_group == mark_anthony_group:
            print(f"\n🎉 SUCCESS: All three users are in the same group!")
            print(f"   Group: {al_baljon_group}")
        else:
            print(f"\n❌ FAILURE: Users are in different groups")
    else:
        print(f"\n❌ FAILURE: Not all users were found")

if __name__ == "__main__":
    verify_three_users() 