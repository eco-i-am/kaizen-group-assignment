import pandas as pd
from collections import defaultdict

def test_same_gender_separation():
    """Test the updated same_gender logic that ensures strict male/female separation"""
    
    # Create sample data with same_gender preference
    sample_data = [
        {
            'user_id': '1',
            'name': 'Alice',
            'email': 'alice@example.com',
            'gender_preference': 'same_gender',
            'gender_identity': 'Female',
            'sex': 'female',
            'residing_ph': '1',
            'province': 'Manila',
            'city': 'Manila'
        },
        {
            'user_id': '2',
            'name': 'Bob',
            'email': 'bob@example.com',
            'gender_preference': 'same_gender',
            'gender_identity': 'Male',
            'sex': 'male',
            'residing_ph': '1',
            'province': 'Manila',
            'city': 'Manila'
        },
        {
            'user_id': '3',
            'name': 'Carol',
            'email': 'carol@example.com',
            'gender_preference': 'same_gender',
            'gender_identity': 'Female',
            'sex': 'female',
            'residing_ph': '1',
            'province': 'Manila',
            'city': 'Manila'
        },
        {
            'user_id': '4',
            'name': 'David',
            'email': 'david@example.com',
            'gender_preference': 'same_gender',
            'gender_identity': 'Male',
            'sex': 'male',
            'residing_ph': '1',
            'province': 'Manila',
            'city': 'Manila'
        },
        {
            'user_id': '5',
            'name': 'Eve',
            'email': 'eve@example.com',
            'gender_preference': 'same_gender',
            'gender_identity': 'LGBTQ+',
            'sex': 'female',
            'residing_ph': '1',
            'province': 'Manila',
            'city': 'Manila'
        },
        {
            'user_id': '6',
            'name': 'Frank',
            'email': 'frank@example.com',
            'gender_preference': 'same_gender',
            'gender_identity': 'LGBTQ+',
            'sex': 'male',
            'residing_ph': '1',
            'province': 'Manila',
            'city': 'Manila'
        },
        {
            'user_id': '7',
            'name': 'Grace',
            'email': 'grace@example.com',
            'gender_preference': 'no_preference',
            'gender_identity': 'Female',
            'sex': 'female',
            'residing_ph': '1',
            'province': 'Manila',
            'city': 'Manila'
        },
        {
            'user_id': '8',
            'name': 'Henry',
            'email': 'henry@example.com',
            'gender_preference': 'no_preference',
            'gender_identity': 'Male',
            'sex': 'male',
            'residing_ph': '1',
            'province': 'Manila',
            'city': 'Manila'
        }
    ]
    
    # Column mapping for the sample data
    column_mapping = {
        'user_id': 'user_id',
        'name': 'name',
        'email': 'email',
        'gender_preference': 'gender_preference',
        'gender_identity': 'gender_identity',
        'sex': 'sex',
        'residing_ph': 'residing_ph',
        'province': 'province',
        'city': 'city'
    }
    
    def get_value(row, key, default=''):
        if key in column_mapping:
            return row.get(column_mapping[key], default)
        return default
    
    # Test the updated same_gender logic
    print("Testing same_gender separation logic:")
    print("=" * 50)
    
    # Group by gender preference
    gender_pref_groups = defaultdict(list)
    
    for row in sample_data:
        gender_pref = str(get_value(row, 'gender_preference', '')).lower()
        user_id = get_value(row, 'user_id', 'Unknown')
        name = get_value(row, 'name', 'Unknown')
        
        print(f"User {user_id} ({name}): gender_preference = '{gender_pref}'")
        
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
    
    print(f"\nGender preference groups created:")
    for key, members in gender_pref_groups.items():
        print(f"  {key}: {len(members)} participants")
        for member in members:
            user_id = get_value(member, 'user_id', 'Unknown')
            name = get_value(member, 'name', 'Unknown')
            gender_identity = get_value(member, 'gender_identity', 'Unknown')
            sex = get_value(member, 'sex', 'Unknown')
            print(f"    - User {user_id}: {name} (gender_identity: {gender_identity}, sex: {sex})")
    
    # Verify separation
    print(f"\nVerification:")
    for key, members in gender_pref_groups.items():
        if 'same_gender' in key or key in ['male', 'female', 'lgbtq+_male', 'lgbtq+_female']:
            print(f"\nGroup '{key}':")
            for member in members:
                user_id = get_value(member, 'user_id', 'Unknown')
                name = get_value(member, 'name', 'Unknown')
                sex = get_value(member, 'sex', 'Unknown')
                print(f"  - {name} (sex: {sex})")
            
            # Check if all members have the same sex
            sexes = set(get_value(member, 'sex', '').lower() for member in members)
            if len(sexes) == 1:
                print(f"  ✅ All members have same sex: {list(sexes)[0]}")
            else:
                print(f"  ❌ Mixed sexes found: {sexes}")
    
    return gender_pref_groups

if __name__ == "__main__":
    test_same_gender_separation() 