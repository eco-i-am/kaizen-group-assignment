import pandas as pd
import sys
sys.path.append('.')

from group_assignment_to_excel import find_column_mapping

def verify_final_result():
    """Verify that Morris and Gerard are correctly grouped together in the final output"""
    
    print("🔍 VERIFYING FINAL RESULT")
    print("=" * 60)
    
    # Read the final output file
    OUTPUT_FILE = 'grouped_participants.xlsx'
    
    try:
        # Read the Grouped Members sheet
        df_requested = pd.read_excel(OUTPUT_FILE, sheet_name='Grouped Members')
        print(f"✅ Successfully read grouped members with {len(df_requested)} rows")
    except Exception as e:
        print(f"❌ Error reading requested groups: {e}")
        return
    
    # Find Morris and Gerard in the requested groups
    morris_found = False
    gerard_found = False
    morris_group = None
    gerard_group = None
    
    for index, row in df_requested.iterrows():
        # Check each column for user IDs
        for col in df_requested.columns:
            if pd.notna(row[col]):
                user_id = str(row[col]).strip()
                if user_id == '2360':  # Morris
                    morris_found = True
                    morris_group = index + 1
                    print(f"✅ Found Morris (ID: 2360) in Requested Group {morris_group}")
                elif user_id == '2123':  # Gerard
                    gerard_found = True
                    gerard_group = index + 1
                    print(f"✅ Found Gerard (ID: 2123) in Requested Group {gerard_group}")
    
    if not morris_found:
        print("❌ Morris (ID: 2360) not found in requested groups")
    if not gerard_found:
        print("❌ Gerard (ID: 2123) not found in requested groups")
    
    if morris_found and gerard_found:
        if morris_group == gerard_group:
            print(f"\n🎉 SUCCESS! Morris and Gerard are in the same group: Requested Group {morris_group}")
            
            # Show the members of this group
            print(f"\n📋 Members of Requested Group {morris_group}:")
            group_row = df_requested.iloc[morris_group - 1]
            for col in df_requested.columns:
                if pd.notna(group_row[col]):
                    user_id = str(group_row[col]).strip()
                    print(f"  - User ID: {user_id}")
        else:
            print(f"\n❌ FAILURE! Morris and Gerard are in different groups:")
            print(f"  Morris: Requested Group {morris_group}")
            print(f"  Gerard: Requested Group {gerard_group}")
    
    # Also check if John Michael Joseph Pineda and Patricia Palacios are in the same group
    john_found = False
    patricia_found = False
    john_group = None
    patricia_group = None
    
    for index, row in df_requested.iterrows():
        for col in df_requested.columns:
            if pd.notna(row[col]):
                user_id = str(row[col]).strip()
                if user_id == '2817':  # John Michael Joseph Pineda
                    john_found = True
                    john_group = index + 1
                elif user_id == '2539':  # Patricia Palacios
                    patricia_found = True
                    patricia_group = index + 1
    
    if john_found and patricia_found:
        if john_group == patricia_group:
            print(f"\n✅ John Michael Joseph Pineda and Patricia Palacios are in the same group: Requested Group {john_group}")
        else:
            print(f"\n⚠️  John Michael Joseph Pineda and Patricia Palacios are in different groups:")
            print(f"  John: Requested Group {john_group}")
            print(f"  Patricia: Requested Group {patricia_group}")
    
    # Check if all four users are in the same group
    if morris_found and gerard_found and john_found and patricia_found:
        if morris_group == gerard_group == john_group == patricia_group:
            print(f"\n🎉 PERFECT! All four users are in the same group: Requested Group {morris_group}")
            
            # Show all members of this group
            print(f"\n📋 All members of Requested Group {morris_group}:")
            group_row = df_requested.iloc[morris_group - 1]
            for col in df_requested.columns:
                if pd.notna(group_row[col]):
                    user_id = str(group_row[col]).strip()
                    print(f"  - User ID: {user_id}")
        else:
            print(f"\n⚠️  Not all four users are in the same group:")
            print(f"  Morris: Requested Group {morris_group}")
            print(f"  Gerard: Requested Group {gerard_group}")
            print(f"  John: Requested Group {john_group}")
            print(f"  Patricia: Requested Group {patricia_group}")

if __name__ == "__main__":
    verify_final_result() 