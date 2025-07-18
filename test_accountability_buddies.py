import pandas as pd
from group_assignment_to_excel import group_participants, save_to_excel, find_column_mapping

# Create test data with accountability buddies
test_data = [
    {
        'user_id': 1,
        'full_name': 'User 1',
        'gender_identity': 'Female',
        'biological_sex': 'female',
        'residing_in_philippines': 1,
        'grouping_preference': 'same_gender',
        'country': 'Philippines',
        'state_province': 'Metro Manila',
        'city': 'Manila',
        'region': 'NCR',
        'prefer_solo': 0,
        'email': 'user1@test.com',
        'accountability_buddies': '["user2@test.com", "user3@test.com", "missing@test.com"]',
        'has_accountability_buddies': 1,
        'temporary_team_name': '',
        'previous_coach_name': ''
    },
    {
        'user_id': 2,
        'full_name': 'User 2',
        'gender_identity': 'Female',
        'biological_sex': 'female',
        'residing_in_philippines': 1,
        'grouping_preference': 'same_gender',
        'country': 'Philippines',
        'state_province': 'Metro Manila',
        'city': 'Manila',
        'region': 'NCR',
        'prefer_solo': 0,
        'email': 'user2@test.com',
        'accountability_buddies': '["user1@test.com", "user3@test.com"]',
        'has_accountability_buddies': 1,
        'temporary_team_name': '',
        'previous_coach_name': ''
    },
    {
        'user_id': 3,
        'full_name': 'User 3',
        'gender_identity': 'Female',
        'biological_sex': 'female',
        'residing_in_philippines': 1,
        'grouping_preference': 'same_gender',
        'country': 'Philippines',
        'state_province': 'Metro Manila',
        'city': 'Manila',
        'region': 'NCR',
        'prefer_solo': 0,
        'email': 'user3@test.com',
        'accountability_buddies': '["user1@test.com", "user2@test.com"]',
        'has_accountability_buddies': 1,
        'temporary_team_name': '',
        'previous_coach_name': ''
    },
    {
        'user_id': 4,
        'full_name': 'User 4',
        'gender_identity': 'Male',
        'biological_sex': 'male',
        'residing_in_philippines': 1,
        'grouping_preference': 'same_gender',
        'country': 'Philippines',
        'state_province': 'Metro Manila',
        'city': 'Manila',
        'region': 'NCR',
        'prefer_solo': 0,
        'email': 'user4@test.com',
        'accountability_buddies': '["missing1@test.com", "missing2@test.com"]',
        'has_accountability_buddies': 1,
        'temporary_team_name': '',
        'previous_coach_name': ''
    },
    {
        'user_id': 5,
        'full_name': 'User 5',
        'gender_identity': 'Male',
        'biological_sex': 'male',
        'residing_in_philippines': 1,
        'grouping_preference': 'same_gender',
        'country': 'Philippines',
        'state_province': 'Metro Manila',
        'city': 'Manila',
        'region': 'NCR',
        'prefer_solo': 0,
        'email': 'user5@test.com',
        'accountability_buddies': '["user6@test.com"]',
        'has_accountability_buddies': 1,
        'temporary_team_name': '',
        'previous_coach_name': ''
    },
    {
        'user_id': 6,
        'full_name': 'User 6',
        'gender_identity': 'Male',
        'biological_sex': 'male',
        'residing_in_philippines': 1,
        'grouping_preference': 'same_gender',
        'country': 'Philippines',
        'state_province': 'Metro Manila',
        'city': 'Manila',
        'region': 'NCR',
        'prefer_solo': 0,
        'email': 'user6@test.com',
        'accountability_buddies': '["user5@test.com"]',
        'has_accountability_buddies': 1,
        'temporary_team_name': '',
        'previous_coach_name': ''
    }
]

# Create DataFrame
df = pd.DataFrame(test_data)

# Find column mapping
column_mapping = find_column_mapping(df)
print("Column mapping:")
for key, value in column_mapping.items():
    print(f"  {key}: {value}")

# Convert to list of dictionaries
data = df.to_dict('records')

print(f"\nProcessing {len(data)} records...")

# Group participants
solo_groups, grouped, excluded_users, requested_groups = group_participants(data, column_mapping)

print(f"\nResults:")
print(f"Solo groups: {len(solo_groups)}")
print(f"Regular groups: {len(grouped)}")
print(f"Requested groups: {len(requested_groups)}")
print(f"Excluded users: {len(excluded_users)}")

# Show requested groups
if requested_groups:
    print(f"\nRequested Groups:")
    for i, group in enumerate(requested_groups, 1):
        print(f"  Group {i}: {len(group)} members")
        for member in group:
            user_id = member.get(column_mapping.get('user_id'), 'Unknown')
            email = member.get(column_mapping.get('email'), 'No email')
            print(f"    - User {user_id}: {email}")

# Save to Excel
save_to_excel(solo_groups, grouped, 'test_accountability_output.xlsx', column_mapping, excluded_users, requested_groups)
print(f"\nResults saved to: test_accountability_output.xlsx") 