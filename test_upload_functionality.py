#!/usr/bin/env python3
"""
Test script to verify the updated upload functionality works with both CSV and Excel files.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from group_assignment_to_excel import find_column_mapping

def create_test_files():
    """Create test CSV and Excel files to test upload functionality"""
    
    print("🧪 CREATING TEST FILES FOR UPLOAD FUNCTIONALITY")
    print("=" * 60)
    
    # Create sample CSV data (old format)
    print("\n1️⃣ Creating test CSV file...")
    
    csv_data = {
        'user_id': range(1, 21),
        'name': [f'CSV User {i}' for i in range(1, 21)],
        'email': [f'user{i}@example.com' for i in range(1, 21)],
        'gender_identity': np.random.choice(['Male', 'Female', 'LGBTQ+'], 20),
        'age': np.random.randint(18, 65, 20),
        'weight': np.random.randint(50, 120, 20),
        'height': np.random.randint(150, 200, 20),
        'sex': np.random.choice(['male', 'female'], 20),
        'residing_in_philippines': np.random.choice([1, 0], 20),
        'lifting_experience': np.random.choice(['Beginner', 'Intermediate', 'Advanced'], 20),
        'group_gender_preference': np.random.choice(['same_gender', 'no_preference'], 20),
        'preferred_group_size': np.random.randint(3, 6, 20),
        'availability': np.random.choice(['Weekdays', 'Weekends', 'Both'], 20),
        'timezone': np.random.choice(['PHT', 'EST', 'PST'], 20),
        'communication_preference': np.random.choice(['Email', 'WhatsApp', 'Discord'], 20),
        'go_solo': np.random.choice([1, 0], 20, p=[0.1, 0.9]),
        'country': np.random.choice(['Philippines', 'United States', 'Canada'], 20),
        'province': np.random.choice(['Metro Manila', 'California', 'Ontario'], 20),
        'city': np.random.choice(['Manila', 'Los Angeles', 'Toronto'], 20),
        'state': np.random.choice(['NCR', 'CA', 'ON'], 20)
    }
    
    csv_df = pd.DataFrame(csv_data)
    csv_file = 'test_upload_data.csv'
    csv_df.to_csv(csv_file, index=False)
    print(f"✅ Created CSV file: {csv_file}")
    print(f"📋 CSV columns: {list(csv_df.columns)}")
    
    # Create sample Excel data (merged format)
    print("\n2️⃣ Creating test Excel file...")
    
    excel_data = {
        'user_id': range(1, 21),
        'full_name': [f'Excel User {i}' for i in range(1, 21)],
        'gender_identity': np.random.choice(['Male', 'Female', 'LGBTQ+'], 20),
        'biological_sex': np.random.choice(['male', 'female'], 20),
        'residing_in_philippines': np.random.choice(['1', '0'], 20),
        'grouping_preference': np.random.choice(['same_gender', 'no_preference'], 20),
        'country': np.random.choice(['Philippines', 'United States', 'Canada'], 20),
        'state_province': np.random.choice(['Metro Manila', 'California', 'Ontario'], 20),
        'city': np.random.choice(['Manila', 'Los Angeles', 'Toronto'], 20),
        'region': np.random.choice(['NCR', 'CA', 'ON'], 20),
        'prefer_solo': np.random.choice(['1', '0'], 20, p=[0.15, 0.85])
    }
    
    excel_df = pd.DataFrame(excel_data)
    excel_file = 'test_merged_data.xlsx'
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Main merged data
        excel_df.to_excel(writer, sheet_name='Merged Data', index=False)
        
        # Additional sheets (like real merged file)
        users_df = excel_df[['user_id', 'full_name', 'gender_identity', 'biological_sex', 'country']].copy()
        grouping_df = excel_df[['user_id', 'residing_in_philippines', 'grouping_preference', 'prefer_solo']].copy()
        
        users_df.to_excel(writer, sheet_name='Users Data', index=False)
        grouping_df.to_excel(writer, sheet_name='Grouping Preferences', index=False)
        
        # Summary sheet
        summary_data = {
            'Metric': ['Total Records', 'Users Data', 'Grouping Preferences', 'Merged Records'],
            'Count': [len(excel_df), len(users_df), len(grouping_df), len(excel_df)]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"✅ Created Excel file: {excel_file}")
    print(f"📋 Excel columns: {list(excel_df.columns)}")
    
    return csv_file, excel_file

def test_csv_upload_simulation(csv_file):
    """Simulate CSV upload functionality"""
    
    print(f"\n3️⃣ Testing CSV upload simulation...")
    
    try:
        # Simulate reading CSV file
        data = pd.read_csv(csv_file)
        print(f"✅ Successfully read CSV file with {len(data)} records")
        
        # Validate required columns
        required_columns = [
            'user_id', 'gender_identity', 'sex', 'residing_in_philippines',
            'group_gender_preference', 'country', 'province', 'city', 'state', 'go_solo'
        ]
        
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {', '.join(missing_columns)}")
            return False
        else:
            print(f"✅ All required columns present")
            
            # Show statistics
            solo_count = len(data[data['go_solo'] == 1])
            group_count = len(data[data['go_solo'] == 0])
            ph_count = len(data[data['residing_in_philippines'] == 1])
            
            print(f"📊 Statistics:")
            print(f"  - Total Participants: {len(data)}")
            print(f"  - Solo Participants: {solo_count}")
            print(f"  - Group Participants: {group_count}")
            print(f"  - Philippines Residents: {ph_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return False

def test_excel_upload_simulation(excel_file):
    """Simulate Excel upload functionality"""
    
    print(f"\n4️⃣ Testing Excel upload simulation...")
    
    try:
        # Simulate reading Excel file
        data = pd.read_excel(excel_file, sheet_name='Merged Data')
        print(f"✅ Successfully read Excel file with {len(data)} records")
        
        # Find column mapping
        column_mapping = find_column_mapping(data)
        print(f"✅ Column mapping found: {len(column_mapping)} fields mapped")
        
        # Check for essential columns
        essential_fields = ['user_id', 'gender_identity', 'gender_preference']
        missing_essential = [field for field in essential_fields if not column_mapping.get(field)]
        
        if missing_essential:
            print(f"❌ Missing essential columns: {', '.join(missing_essential)}")
            return False
        else:
            print(f"✅ All essential columns present")
            
            # Show column mapping
            print(f"🔍 Column Mapping:")
            for key, value in column_mapping.items():
                if value:
                    print(f"  ✅ {key}: {value}")
                else:
                    print(f"  ❌ {key}: Not found")
            
            # Show statistics
            go_solo_col = column_mapping.get('go_solo')
            solo_count = len(data[data[go_solo_col] == 1]) if go_solo_col else 0
            group_count = len(data[data[go_solo_col] == 0]) if go_solo_col else len(data)
            
            residing_ph_col = column_mapping.get('residing_ph')
            ph_count = len(data[data[residing_ph_col] == 1]) if residing_ph_col else 0
            
            print(f"📊 Statistics:")
            print(f"  - Total Participants: {len(data)}")
            print(f"  - Solo Participants: {solo_count}")
            print(f"  - Group Participants: {group_count}")
            print(f"  - Philippines Residents: {ph_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False

def main():
    """Main test function"""
    
    print("🧪 TESTING UPLOAD FUNCTIONALITY")
    print("=" * 60)
    
    # Create test files
    csv_file, excel_file = create_test_files()
    
    # Test CSV upload
    csv_success = test_csv_upload_simulation(csv_file)
    
    # Test Excel upload
    excel_success = test_excel_upload_simulation(excel_file)
    
    # Summary
    print(f"\n🎉 UPLOAD FUNCTIONALITY TEST COMPLETED")
    print(f"✅ CSV upload: {'PASSED' if csv_success else 'FAILED'}")
    print(f"✅ Excel upload: {'PASSED' if excel_success else 'FAILED'}")
    
    if csv_success and excel_success:
        print(f"\n🎉 All tests passed! The upload functionality works correctly.")
        print(f"📁 Test files created:")
        print(f"  - {csv_file}")
        print(f"  - {excel_file}")
        print(f"\n💡 You can now upload these files in the Streamlit UI to test the functionality.")
    else:
        print(f"\n❌ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 