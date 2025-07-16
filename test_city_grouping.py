#!/usr/bin/env python3
"""
Test script to identify issues with same city grouping logic
"""

from collections import defaultdict

def test_city_grouping_logic():
    """Test the city grouping logic with various scenarios"""
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Scenario 1: Multiple cities with small groups',
            'data': {
                'Metro Manila': {
                    'Quezon City': 3,  # Should combine with others
                    'Makati': 2,       # Should combine with others  
                    'Taguig': 1        # Should combine with others
                }
            },
            'expected_groups': 1,  # Should form 1 group of 6
            'expected_same_city_groups': 0  # No complete same-city groups
        },
        {
            'name': 'Scenario 2: One city with exactly 5',
            'data': {
                'Metro Manila': {
                    'Quezon City': 5,  # Should form 1 complete group
                    'Makati': 2,       # Should remain separate
                    'Taguig': 1        # Should remain separate
                }
            },
            'expected_groups': 3,  # 1 complete + 2 small groups
            'expected_same_city_groups': 1  # 1 complete same-city group
        },
        {
            'name': 'Scenario 3: Multiple cities with complete groups',
            'data': {
                'Metro Manila': {
                    'Quezon City': 7,  # Should form 1 complete group + 2 remaining
                    'Makati': 5,       # Should form 1 complete group
                    'Taguig': 3        # Should combine with remaining from QC
                }
            },
            'expected_groups': 3,  # 2 complete + 1 mixed group
            'expected_same_city_groups': 2  # 2 complete same-city groups
        },
        {
            'name': 'Scenario 4: Edge case - all small groups',
            'data': {
                'Metro Manila': {
                    'Quezon City': 1,
                    'Makati': 1,
                    'Taguig': 1,
                    'Pasig': 1,
                    'Caloocan': 1
                }
            },
            'expected_groups': 1,  # Should form 1 group of 5
            'expected_same_city_groups': 0  # No complete same-city groups
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'='*60}")
        print(f"Testing: {scenario['name']}")
        print(f"{'='*60}")
        
        # Simulate the current logic
        province_groups = scenario['data']
        group_counter = 1
        grouped = {}
        
        for province, city_groups in province_groups.items():
            print(f"Processing province: {province}")
            
            # Simulate city data
            city_data = {}
            for city, count in city_groups.items():
                city_data[city] = [f"{city}_user_{i+1}" for i in range(count)]
            
            print(f"  Cities: {list(city_data.keys())}")
            
            # Current logic simulation
            remaining_city_members = {}
            same_city_groups_created = 0
            
            for city, members in city_data.items():
                print(f"    City '{city}': {len(members)} participants")
                
                # Create complete groups of 5 from this city
                i = 0
                while i + 5 <= len(members):
                    group_members = members[i:i+5]
                    location_info = f"Province: {province}, City: {city}"
                    grouped[f"Group {group_counter} ({location_info})"] = group_members
                    print(f"      Created Group {group_counter} with {len(group_members)} members (same city)")
                    group_counter += 1
                    same_city_groups_created += 1
                    i += 5
                
                # Keep remaining members from this city for later combination
                if i < len(members):
                    remaining_city_members[city] = members[i:]
                    print(f"      Remaining from {city}: {len(members[i:])} members")
            
            # Now combine remaining members from different cities in the same province
            if remaining_city_members:
                print(f"    Combining remaining members from different cities in {province}")
                all_remaining = []
                for city, members in remaining_city_members.items():
                    all_remaining.extend(members)
                
                # Create groups of up to 5 from remaining members
                i = 0
                while i < len(all_remaining):
                    group_members = all_remaining[i:i+5]
                    location_info = f"Province: {province} (mixed cities)"
                    grouped[f"Group {group_counter} ({location_info})"] = group_members
                    print(f"      Created Group {group_counter} with {len(group_members)} members (mixed cities)")
                    group_counter += 1
                    i += 5
        
        # Analyze results
        total_groups = len(grouped)
        print(f"\nResults:")
        print(f"  Total groups created: {total_groups}")
        print(f"  Expected total groups: {scenario['expected_groups']}")
        print(f"  Same city groups created: {same_city_groups_created}")
        print(f"  Expected same city groups: {scenario['expected_same_city_groups']}")
        
        # Check for issues
        issues = []
        if total_groups != scenario['expected_groups']:
            issues.append(f"Wrong number of groups: got {total_groups}, expected {scenario['expected_groups']}")
        
        if same_city_groups_created != scenario['expected_same_city_groups']:
            issues.append(f"Wrong number of same-city groups: got {same_city_groups_created}, expected {scenario['expected_same_city_groups']}")
        
        # Check for mixed city groups that could have been same city
        mixed_city_groups = [name for name in grouped.keys() if "mixed cities" in name]
        if mixed_city_groups:
            print(f"  Mixed city groups: {len(mixed_city_groups)}")
            for group_name in mixed_city_groups:
                members = grouped[group_name]
                cities = set()
                for member in members:
                    city = member.split('_')[0]  # Extract city from member name
                    cities.add(city)
                if len(cities) == 1:
                    issues.append(f"Group {group_name} has all members from same city but was marked as mixed")
        
        if issues:
            print(f"  ❌ Issues found:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  ✅ No issues found")
        
        print(f"\nGroup details:")
        for group_name, members in grouped.items():
            cities = set()
            for member in members:
                city = member.split('_')[0]
                cities.add(city)
            city_info = "same city" if len(cities) == 1 else f"mixed cities: {', '.join(cities)}"
            print(f"  {group_name}: {len(members)} members ({city_info})")

if __name__ == "__main__":
    test_city_grouping_logic() 