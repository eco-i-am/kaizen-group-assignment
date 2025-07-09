#!/usr/bin/env python3
import re
import json
from collections import defaultdict, Counter

def analyze_sql_file(filename):
    """Analyze the SQL file to check scenario coverage"""
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Extract all INSERT statements - simpler approach
    # Find all lines that start with a number (user_id)
    lines = content.split('\n')
    records = []
    
    for line in lines:
        if line.strip().startswith('(') and line.strip().endswith('),'):
            # Remove the trailing comma and parentheses
            line = line.strip().rstrip(',').strip('()')
            parts = line.split(', ')
            
            if len(parts) >= 20:  # Ensure we have enough parts
                try:
                    user_id = parts[0]
                    gender = parts[2].strip("'")
                    client_type = parts[3].strip("'")
                    experience_level = parts[8].strip("'")
                    gender_preference = parts[9].strip("'")
                    goal = parts[10].strip("'")
                    fitness_level = parts[11].strip("'")
                    accountability_group = parts[12]
                    group_name = parts[13] if parts[13] != 'NULL' else 'NULL'
                    location_country = parts[16].strip("'")
                    location_state = parts[17] if parts[17] != 'NULL' else 'NULL'
                    location_city = parts[18].strip("'")
                    going_solo = parts[19]
                    accountability_buddies = parts[20]
                    coach_name = parts[21] if len(parts) > 21 and parts[21] != 'NULL' else 'NULL'
                    
                    records.append({
                        'user_id': user_id,
                        'gender': gender,
                        'client_type': client_type,
                        'experience_level': experience_level,
                        'gender_preference': gender_preference,
                        'goal': goal,
                        'fitness_level': fitness_level,
                        'accountability_group': accountability_group,
                        'group_name': group_name,
                        'location_country': location_country,
                        'location_state': location_state,
                        'location_city': location_city,
                        'going_solo': going_solo,
                        'accountability_buddies': accountability_buddies,
                        'coach_name': coach_name
                    })
                except:
                    continue
    
    print(f"Total records found: {len(records)}")
    print("=" * 50)
    
    # Analyze each field
    fields = {
        'gender': [],
        'client_type': [],
        'experience_level': [],
        'gender_preference': [],
        'goal': [],
        'fitness_level': [],
        'accountability_group': [],
        'location_country': [],
        'location_state': [],
        'location_city': [],
        'going_solo': [],
        'accountability_buddies': [],
        'group_name': [],
        'coach_name': []
    }
    
    for record in records:
        for field in fields:
            if field in record:
                fields[field].append(record[field])
    
    # Print analysis for each field
    for field_name, values in fields.items():
        print(f"\n{field_name.upper()}:")
        counter = Counter(values)
        for value, count in counter.most_common():
            print(f"  {value}: {count}")
    
    # Check specific scenarios
    print("\n" + "=" * 50)
    print("SCENARIO ANALYSIS:")
    print("=" * 50)
    
    # Scenario 1: Gender distribution
    gender_counts = Counter(fields['gender'])
    print(f"\nGender Distribution:")
    for gender, count in gender_counts.items():
        print(f"  {gender}: {count}")
    
    # Scenario 2: Client types
    client_type_counts = Counter(fields['client_type'])
    print(f"\nClient Type Distribution:")
    for client_type, count in client_type_counts.items():
        print(f"  {client_type}: {count}")
    
    # Scenario 3: Experience levels
    experience_counts = Counter(fields['experience_level'])
    print(f"\nExperience Level Distribution:")
    for level, count in experience_counts.items():
        print(f"  {level}: {count}")
    
    # Scenario 4: Goals
    goal_counts = Counter(fields['goal'])
    print(f"\nGoal Distribution:")
    for goal, count in goal_counts.items():
        print(f"  {goal}: {count}")
    
    # Scenario 5: Fitness levels
    fitness_counts = Counter(fields['fitness_level'])
    print(f"\nFitness Level Distribution:")
    for level, count in fitness_counts.items():
        print(f"  {level}: {count}")
    
    # Scenario 6: Gender preferences
    gender_pref_counts = Counter(fields['gender_preference'])
    print(f"\nGender Preference Distribution:")
    for pref, count in gender_pref_counts.items():
        print(f"  {pref}: {count}")
    
    # Scenario 7: Location countries
    country_counts = Counter(fields['location_country'])
    print(f"\nLocation Country Distribution:")
    for country, count in country_counts.most_common(10):
        print(f"  {country}: {count}")
    
    # Scenario 8: Going solo vs accountability
    going_solo_counts = Counter(fields['going_solo'])
    print(f"\nGoing Solo Distribution:")
    for solo, count in going_solo_counts.items():
        print(f"  {solo}: {count}")
    
    accountability_counts = Counter(fields['accountability_buddies'])
    print(f"\nAccountability Buddies Distribution:")
    for buddies, count in accountability_counts.items():
        print(f"  {buddies}: {count}")
    
    # Scenario 9: Accountability groups
    group_counts = Counter(fields['accountability_group'])
    print(f"\nAccountability Group Distribution:")
    for group, count in group_counts.items():
        print(f"  {group}: {count}")
    
    # Check for edge cases
    print("\n" + "=" * 50)
    print("EDGE CASE ANALYSIS:")
    print("=" * 50)
    
    # Check for NULL values in location fields
    null_state_count = sum(1 for state in fields['location_state'] if state == 'NULL')
    null_city_count = sum(1 for city in fields['location_city'] if city == 'NULL')
    
    print(f"\nRecords with NULL state: {null_state_count}")
    print(f"Records with NULL city: {null_city_count}")
    
    # Check for group names vs NULL
    group_name_counts = Counter([name for name in fields['group_name'] if name != 'NULL'])
    print(f"\nGroup Names Used:")
    for name, count in group_name_counts.most_common(10):
        print(f"  {name}: {count}")
    
    # Check for coach assignments
    coach_counts = Counter([coach for coach in fields['coach_name'] if coach != 'NULL'])
    print(f"\nCoach Assignments:")
    for coach, count in coach_counts.most_common():
        print(f"  {coach}: {count}")
    
    # Check for unique combinations
    print("\n" + "=" * 50)
    print("COMBINATION ANALYSIS:")
    print("=" * 50)
    
    # Check gender + client_type combinations
    gender_client_combos = Counter([(r['gender'], r['client_type']) for r in records])
    print(f"\nGender + Client Type Combinations:")
    for (gender, client_type), count in gender_client_combos.most_common(10):
        print(f"  {gender} + {client_type}: {count}")
    
    # Check experience + goal combinations
    experience_goal_combos = Counter([(r['experience_level'], r['goal']) for r in records])
    print(f"\nExperience + Goal Combinations:")
    for (exp, goal), count in experience_goal_combos.most_common(10):
        print(f"  {exp} + {goal}: {count}")
    
    # Check location + going_solo combinations
    location_solo_combos = Counter([(r['location_country'], r['going_solo']) for r in records])
    print(f"\nLocation + Going Solo Combinations:")
    for (country, solo), count in location_solo_combos.most_common(10):
        print(f"  {country} + {solo}: {count}")

if __name__ == "__main__":
    analyze_sql_file("phpmyadmin_test_data.sql") 