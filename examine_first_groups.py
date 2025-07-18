import pandas as pd

def examine_first_groups():
    """Examine the first few groups to understand the grouping logic"""
    
    print("🔍 EXAMINING FIRST GROUPS")
    print("=" * 50)
    
    # Read the output Excel file
    OUTPUT_FILE = 'grouped_participants.xlsx'
    
    try:
        df = pd.read_excel(OUTPUT_FILE, sheet_name='Grouped Members')
        print(f"✅ Successfully read output file with {len(df)} rows")
    except Exception as e:
        print(f"❌ Error reading output file: {e}")
        return
    
    # Examine the first 5 groups
    print(f"\n📋 FIRST 5 GROUPS:")
    for i in range(min(5, len(df))):
        row = df.iloc[i]
        group_name = row['Group Name']
        
        print(f"\n{i+1}. {group_name}")
        
        # Count how many members are in this group
        member_count = 0
        members = []
        
        for j in range(1, 8):  # Check User ID 1 through User ID 7
            user_id_col = f'User ID {j}'
            name_col = f'Name {j}'
            
            if user_id_col in df.columns and name_col in df.columns:
                user_id = row[user_id_col]
                name = row[name_col]
                
                if pd.notna(user_id):
                    member_count += 1
                    members.append(f"User {user_id}: {name}")
        
        print(f"   Members: {member_count}")
        for member in members:
            print(f"     {member}")
        
        # Check if this is a requested group and look for missing buddies
        if 'Requested Group' in str(group_name) and 'Missing:' in str(group_name):
            print(f"   ⚠️  This group has missing accountability buddies")
        
        # Check team names and other info
        if 'Temporary Team Name' in df.columns:
            team_names = row['Temporary Team Name']
            if pd.notna(team_names):
                print(f"   Team Names: {team_names}")

if __name__ == "__main__":
    examine_first_groups() 