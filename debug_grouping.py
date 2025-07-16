#!/usr/bin/env python3
"""
Debug script to test the exact grouping logic with the Mandaluyong scenario
"""

from collections import defaultdict

def debug_mandaluyong_scenario():
    """Debug the Mandaluyong grouping issue"""
    
    # Simulate the exact scenario from the screenshot
    # Two participants from Mandaluyong should be grouped together
    test_data = [
        # Group 1 participants (from screenshot)
        {'user_id': '54', 'name': 'ER Gapan', 'city': 'Marikina', 'province': 'Metro Manila', 'gender_preference': 'same_gender', 'sex': 'male', 'gender_identity': 'LGBTQ+'},
        {'user_id': '2311', 'name': 'Arthur Ger', 'city': 'Quezon City', 'province': 'Metro Manila', 'gender_preference': 'same_gender', 'sex': 'male', 'gender_identity': 'LGBTQ+'},
        {'user_id': '2752', 'name': 'marklimju', 'city': 'Quezon City', 'province': 'Metro Manila', 'gender_preference': 'same_gender', 'sex': 'male', 'gender_identity': 'LGBTQ+'},
        {'user_id': '510', 'name': 'Noel Herna', 'city': 'Taguig', 'province': 'Metro Manila', 'gender_preference': 'same_gender', 'sex': 'male', 'gender_identity': 'LGBTQ+'},
        {'user_id': '1232', 'name': 'Reuben Ba', 'city': 'Mandaluyong', 'province': 'Metro Manila', 'gender_preference': 'same_gender', 'sex': 'male', 'gender_identity': 'LGBTQ+'},
        
        # Group 2 participants (from screenshot)
        {'user_id': '1775', 'name': 'Joco Rafael', 'city': 'Mandaluyong', 'province': 'Metro Manila', 'gender_preference': 'same_gender', 'sex': 'male', 'gender_identity': 'LGBTQ+'},
        {'user_id': '2276', 'name': 'Mc Gill Cor', 'city': 'Caloocan', 'province': 'Metro Manila', 'gender_preference': 'same_gender', 'sex': 'male', 'gender_identity': 'LGBTQ+'},
        {'user_id': '2542', 'name': 'BRIAN MIC', 'city': 'Makati', 'province': 'Metro Manila', 'gender_preference': 'same_gender', 'sex': 'male', 'gender_identity': 'LGBTQ+'},
        {'user_id': '2589', 'name': 'Marcelo M', 'city': 'Manila', 'province': 'Metro Manila', 'gender_preference': 'same_gender', 'sex': 'male', 'gender_identity': 'LGBTQ+'},
        {'user_id': '2632', 'name': 'Phillip Tian', 'city': 'Pasig', 'province': 'Metro Manila', 'gender_preference': 'same_gender', 'sex': 'male', 'gender_identity': 'LGBTQ+'},
    ]
    
    print("Testing Mandaluyong grouping scenario:")
    print("=" * 60)
    print(f"Total participants: {len(test_data)}")
    
    # Simulate the grouping logic
    def get_value(row, key, default=''):
        return row.get(key, default)
    
    # Group by gender preference first
    gender_pref_groups = defaultdict(list)
    for row in test_data:
        gender_pref = str(get_value(row, 'gender_preference', '')).lower()
        sex = str(get_value(row, 'sex', '')).lower()
        gender_identity = str(get_value(row, 'gender_identity', '')).upper()
        
        if gender_pref == 'same_gender':
            if gender_identity == 'LGBTQ+':
                gender_key = f"lgbtq+_{sex}"
            else:
                gender_key = sex
        else:
            gender_key = 'no_preference'
        
        gender_pref_groups[gender_key].append(row)
    
    print(f"Gender preference groups: {dict(gender_pref_groups)}")
    
    # Process each gender group
    for gender_key, rows in gender_pref_groups.items():
        print(f"\nProcessing gender group: {gender_key} ({len(rows)} participants)")
        
        # Split by PH or not (all should be PH in this case)
        ph_rows = []
        for r in rows:
            ph_val = str(get_value(r, 'residing_ph', '1')).strip().lower()
            if ph_val in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
                ph_rows.append(r)
        
        print(f"  Philippines residents: {len(ph_rows)}")
        
        # Group by province
        province_groups = defaultdict(list)
        for r in ph_rows:
            province = get_value(r, 'province', 'Unknown Province')
            province_norm = province.strip().lower() if isinstance(province, str) else str(province).strip().lower()
            province_groups[province_norm].append(r)
        
        print(f"  Provinces found: {list(province_groups.keys())}")
        
        # Process each province
        for province_norm, province_members in province_groups.items():
            province = get_value(province_members[0], 'province', 'Unknown Province')
            print(f"    Processing province: {province} ({len(province_members)} participants)")
            
            # Group by city
            city_groups = defaultdict(list)
            for r in province_members:
                city = get_value(r, 'city', 'Unknown City')
                city_norm = city.strip().lower() if isinstance(city, str) else str(city).strip().lower()
                city_groups[city_norm].append(r)
            
            print(f"      Cities found: {list(city_groups.keys())}")
            for city_norm, members in city_groups.items():
                print(f"        {city_norm}: {len(members)} participants")
            
            # Apply the new grouping logic
            print(f"      Applying new grouping logic...")
            
            # Collect all participants from this province
            all_province_members = []
            for city_norm, members in city_groups.items():
                all_province_members.extend(members)
            
            print(f"        Total participants in {province}: {len(all_province_members)}")
            
            # Group by city within the province
            city_members = defaultdict(list)
            for member in all_province_members:
                city = get_value(member, 'city', 'Unknown City')
                city_norm = city.strip().lower() if isinstance(city, str) else str(city).strip().lower()
                city_members[city_norm].append(member)
            
            print(f"        City breakdown:")
            for city_norm, members in city_members.items():
                print(f"          {city_norm}: {len(members)} participants")
            
            # First, create complete groups (5 members) from each city
            remaining_by_city = {}
            group_counter = 1
            grouped = {}
            
            for city_norm, members in city_members.items():
                print(f"          Processing {city_norm}: {len(members)} participants")
                
                # Create complete groups of 5 from this city
                i = 0
                while i + 5 <= len(members):
                    group_members = members[i:i+5]
                    location_info = f"Province: {province}, City: {city_norm}"
                    grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                    print(f"            Created Group {group_counter} with {len(group_members)} members (same city)")
                    group_counter += 1
                    i += 5
                
                # Keep remaining members from this city
                if i < len(members):
                    remaining_by_city[city_norm] = members[i:]
                    print(f"            Remaining from {city_norm}: {len(members[i:])} members")
            
            # Now handle remaining members - prioritize same-city groups
            if remaining_by_city:
                print(f"        Processing remaining members from {province}")
                print(f"        Remaining by city: {dict([(k, len(v)) for k, v in remaining_by_city.items()])}")
                
                # First, try to form same-city groups from remaining members
                for city_norm, members in list(remaining_by_city.items()):
                    if len(members) >= 5:
                        # Can form a complete group from this city
                        group_members = members[:5]
                        location_info = f"Province: {province}, City: {city_norm}"
                        grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                        print(f"            Created Group {group_counter} with {len(group_members)} members (same city, from remaining)")
                        group_counter += 1
                        remaining_by_city[city_norm] = members[5:]
                    elif len(members) == 0:
                        del remaining_by_city[city_norm]
                
                # Collect all final remaining members (less than 5 per city)
                final_remaining = []
                for members in remaining_by_city.values():
                    final_remaining.extend(members)
                
                print(f"        Final remaining: {len(final_remaining)} members")
                
                # Create mixed-city groups from final remaining
                if final_remaining:
                    print(f"        Creating mixed-city groups from {len(final_remaining)} final remaining members")
                    i = 0
                    while i < len(final_remaining):
                        group_members = final_remaining[i:i+5]
                        # Check if all members are from the same city
                        cities_in_group = set()
                        for member in group_members:
                            city = get_value(member, 'city', 'Unknown City')
                            cities_in_group.add(city.strip().lower() if isinstance(city, str) else str(city).strip().lower())
                        
                        if len(cities_in_group) == 1:
                            city_name = get_value(group_members[0], 'city', 'Unknown City')
                            location_info = f"Province: {province}, City: {city_name}"
                            print(f"            Created Group {group_counter} with {len(group_members)} members (same city, from final remaining)")
                        else:
                            location_info = f"Province: {province} (mixed cities)"
                            print(f"            Created Group {group_counter} with {len(group_members)} members (mixed cities)")
                        
                        grouped[f"Group {group_counter} ({gender_key}, {location_info})"] = group_members
                        group_counter += 1
                        i += 5
    
    # Analyze results
    print(f"\nResults:")
    print(f"=" * 60)
    for group_name, members in grouped.items():
        print(f"\n{group_name}:")
        cities = set()
        for member in members:
            city = get_value(member, 'city', 'Unknown City')
            cities.add(city)
            print(f"  - {get_value(member, 'user_id')} {get_value(member, 'name')} from {city}")
        
        if len(cities) == 1:
            print(f"  ✅ Same city group: {list(cities)[0]}")
        else:
            print(f"  ❌ Mixed city group: {', '.join(cities)}")
    
    # Check for Mandaluyong issue
    mandaluyong_participants = []
    for group_name, members in grouped.items():
        for member in members:
            if get_value(member, 'city', '').lower() == 'mandaluyong':
                mandaluyong_participants.append((group_name, member))
    
    print(f"\nMandaluyong participants:")
    for group_name, member in mandaluyong_participants:
        print(f"  - {get_value(member, 'user_id')} {get_value(member, 'name')} in {group_name}")
    
    if len(mandaluyong_participants) > 1:
        groups = set([group_name for group_name, _ in mandaluyong_participants])
        if len(groups) > 1:
            print(f"  ❌ ISSUE: Mandaluyong participants are in different groups: {groups}")
        else:
            print(f"  ✅ Mandaluyong participants are grouped together in: {list(groups)[0]}")

if __name__ == "__main__":
    debug_mandaluyong_scenario() 