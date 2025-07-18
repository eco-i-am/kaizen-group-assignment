import pandas as pd

# Read the merged Excel file
df = pd.read_excel('merged_users_grouping_preferences_20250717_201414.xlsx', sheet_name='Merged Data')

print("Fixing email mismatch for Jaw Ybañez and Agnes Rosero:")
print("=" * 60)

# Find Agnes Rosero
agnes_mask = df['name'] == 'Agnes Rosero'
agnes_indices = df[agnes_mask].index

if len(agnes_indices) > 0:
    agnes_index = agnes_indices[0]
    
    print(f"\nBefore fix:")
    print(f"  Agnes Rosero's accountability buddies: {df.loc[agnes_index, 'accountabilityBuddies']}")
    
    # Get the current accountability buddies
    current_buddies = df.loc[agnes_index, 'accountabilityBuddies']
    
    # Replace the incorrect email with the correct one
    if isinstance(current_buddies, str):
        # Convert string representation to list
        import ast
        try:
            buddies_list = ast.literal_eval(current_buddies)
        except:
            # If it's not a valid list format, try to parse it manually
            buddies_str = current_buddies.strip('[]').replace('"', '').replace("'", '')
            buddies_list = [email.strip() for email in buddies_str.split(',') if email.strip()]
        
        # Replace the incorrect email
        updated_buddies = []
        for buddy in buddies_list:
            if buddy == 'jaw.ybanez@yahoo.com':
                updated_buddies.append('yo21st@gmail.com')
                print(f"  Replacing 'jaw.ybanez@yahoo.com' with 'yo21st@gmail.com'")
            else:
                updated_buddies.append(buddy)
        
        # Update the dataframe
        df.loc[agnes_index, 'accountabilityBuddies'] = str(updated_buddies)
        
        print(f"\nAfter fix:")
        print(f"  Agnes Rosero's accountability buddies: {df.loc[agnes_index, 'accountabilityBuddies']}")
        
        # Save the updated file with proper encoding
        output_file = 'merged_users_grouping_preferences_20250717_201414_fixed.xlsx'
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Merged Data', index=False)
        print(f"\n✅ Updated file saved as: {output_file}")
        
    else:
        print(f"❌ Unexpected format for accountability buddies: {type(current_buddies)}")
else:
    print(f"❌ Agnes Rosero not found in the data")

# Verify the fix by checking both users
print(f"\n" + "="*60)
print("VERIFICATION:")
print("="*60)

# Check Jaw Ybañez
jaw_mask = df['name'] == 'Jaw Ybañez'
if len(df[jaw_mask]) > 0:
    jaw_user = df[jaw_mask].iloc[0]
    print(f"\nJaw Ybañez:")
    print(f"  Email: {jaw_user['email']}")
    print(f"  Accountability Buddies: {jaw_user['accountabilityBuddies']}")

# Check Agnes Rosero
if len(agnes_indices) > 0:
    agnes_user = df.loc[agnes_index]
    print(f"\nAgnes Rosero:")
    print(f"  Email: {agnes_user['email']}")
    print(f"  Accountability Buddies: {agnes_user['accountabilityBuddies']}")
    
    # Check if the fix worked
    buddies_str = agnes_user['accountabilityBuddies']
    if 'yo21st@gmail.com' in buddies_str and 'jaw.ybanez@yahoo.com' not in buddies_str:
        print(f"  ✅ Email fix successful!")
    else:
        print(f"  ❌ Email fix failed!") 