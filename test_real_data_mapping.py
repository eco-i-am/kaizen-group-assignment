#!/usr/bin/env python3
"""
Test script to verify column mapping with the actual merged data structure
"""

import pandas as pd
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from group_assignment_to_excel import find_column_mapping

def test_real_data_mapping():
    """Test column mapping with the actual data structure"""
    
    print("🧪 TESTING COLUMN MAPPING WITH REAL DATA STRUCTURE")
    print("=" * 60)
    
    # Create sample data with the actual column names from the user's file
    sample_data = {
        '@id_x': ['user1', 'user2', 'user3'],
        '@type_x': ['type1', 'type2', 'type3'],
        'id_x': [1, 2, 3],
        'user': ['user1', 'user2', 'user3'],
        'program': ['program1', 'program2', 'program3'],
        'gender': ['Male', 'Female', 'LGBTQ+'],
        'identitizen': ['Male', 'Female', 'LGBTQ+'],
        'clientType': ['type1', 'type2', 'type3'],
        'createdAt_x': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'updatedAt_x': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'sex': ['male', 'female', 'male'],
        'lingInPhilippineExperience': ['1', '0', '1'],
        'genderPref': ['same_gender', 'no_preference', 'same_gender'],
        'currentGoal': ['goal1', 'goal2', 'goal3'],
        'followUpLevel': ['level1', 'level2', 'level3'],
        'accountabilityBuddy': ['buddy1', 'buddy2', 'buddy3'],
        'province': ['Metro Manila', 'California', 'Ontario'],
        'city': ['Manila', 'Los Angeles', 'Toronto'],
        'lingAsStudent': ['1', '0', '1'],
        'accountability': ['acc1', 'acc2', 'acc3'],
        'country': ['Philippines', 'United States', 'Canada'],
        'goSolo': ['0', '1', '0'],
        'state': ['NCR', 'CA', 'ON'],
        'temporaryTe': ['temp1', 'temp2', 'temp3'],
        'amInPreviousCousCoachN': ['prev1', 'prev2', 'prev3'],
        '@id_y': ['email1', 'email2', 'email3'],
        '@type_y': ['email_type1', 'email_type2', 'email_type3'],
        'id_y': [101, 102, 103],
        'email': ['user1@example.com', 'user2@example.com', 'user3@example.com'],
        'name': ['User One', 'User Two', 'User Three'],
        'createdAt_y': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'lingTasksCo': ['task1', 'task2', 'task3'],
        'firstName': ['User', 'User', 'User'],
        'lastName': ['One', 'Two', 'Three'],
        'nickname': ['U1', 'U2', 'U3'],
        'guid': ['guid1', 'guid2', 'guid3'],
        'trackers': ['tracker1', 'tracker2', 'tracker3'],
        'enrolledPrograms': ['program1', 'program2', 'program3']
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    print(f"📋 Sample data created with {len(df)} records")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Test column mapping
    print(f"\n🔍 Testing column mapping...")
    column_mapping = find_column_mapping(df)
    
    print(f"\n📊 Column Mapping Results:")
    for key, value in column_mapping.items():
        if value:
            print(f"  ✅ {key}: {value}")
        else:
            print(f"  ❌ {key}: Not found")
    
    # Check essential columns
    essential_fields = ['user_id', 'gender_identity', 'gender_preference']
    missing_essential = [field for field in essential_fields if not column_mapping.get(field)]
    
    if missing_essential:
        print(f"\n❌ Missing essential columns: {', '.join(missing_essential)}")
        print(f"⚠️  The system may not work properly without these columns.")
    else:
        print(f"\n✅ All essential columns found!")
    
    # Show what data would be used for grouping
    print(f"\n📋 Data that would be used for grouping:")
    if column_mapping.get('user_id'):
        print(f"  User ID column: {column_mapping['user_id']}")
        print(f"  Sample values: {df[column_mapping['user_id']].tolist()}")
    
    if column_mapping.get('gender_identity'):
        print(f"  Gender Identity column: {column_mapping['gender_identity']}")
        print(f"  Sample values: {df[column_mapping['gender_identity']].tolist()}")
    
    if column_mapping.get('gender_preference'):
        print(f"  Gender Preference column: {column_mapping['gender_preference']}")
        print(f"  Sample values: {df[column_mapping['gender_preference']].tolist()}")
    
    if column_mapping.get('go_solo'):
        print(f"  Go Solo column: {column_mapping['go_solo']}")
        print(f"  Sample values: {df[column_mapping['go_solo']].tolist()}")
    
    if column_mapping.get('country'):
        print(f"  Country column: {column_mapping['country']}")
        print(f"  Sample values: {df[column_mapping['country']].tolist()}")
    
    return column_mapping

if __name__ == "__main__":
    test_real_data_mapping() 