#!/usr/bin/env python3

try:
    from group_assignment_to_excel import group_participants, save_to_excel, find_column_mapping
    print("✅ Successfully imported group_assignment_to_excel module")
    print("✅ No syntax errors found")
except SyntaxError as e:
    print(f"❌ Syntax error found: {e}")
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")

print("\nTesting basic functionality...")

# Test the column mapping function
try:
    import pandas as pd
    # Create a simple test DataFrame
    test_data = pd.DataFrame({
        'user_id': ['1', '2'],
        'name': ['Alice', 'Bob'],
        'email': ['alice@test.com', 'bob@test.com'],
        'accountability_buddies': ['["bob@test.com"]', ''],
        'has_accountability_buddies': ['1', '0']
    })
    
    column_mapping = find_column_mapping(test_data)
    print(f"✅ Column mapping test passed: {column_mapping}")
    
except Exception as e:
    print(f"❌ Column mapping test failed: {e}")

print("\nAll tests completed!") 