# Kaizen Group Assignment System - Documentation

## 📋 Overview

The Kaizen Group Assignment System is a sophisticated participant grouping algorithm that creates optimized groups based on multiple criteria including accountability relationships, gender preferences, geographic proximity, and user choices. The system processes merged participant data and outputs organized Excel files with color-coded group assignments.

## 🎯 System Architecture

### Processing Pipeline (6 Phases)

```
PHASE 1: Data Preparation & Filtering
PHASE 2: Accountability Buddies (Highest Priority)
PHASE 3: Solo Participants (User Choice)
PHASE 4: Priority Same-Gender Groups (Females First)
PHASE 5: Regular Algorithmic Grouping (Remaining Participants)
PHASE 6: Small Group Optimization (Post-Processing)
```

---

## 📊 PHASE 1: Data Preparation & Filtering

### Input Processing
- **File Format**: Excel (.xlsx) or CSV
- **Dynamic Column Mapping**: Automatically detects column names using flexible matching
- **Email Normalization**: Maps aliases (e.g., `jaw.ybanez@yahoo.com` → `yo21st@gmail.com`)

### Participant Filtering
- **Excludes**: Users where `joiningAsStudent = False` (keeps NaN values)
- **Tracks**: All users for diagnostic reporting

### Column Mapping Examples
```python
EXPECTED_COLUMNS = {
    'user_id': ['user_id', 'id', 'userid', 'id_y', 'id_x'],
    'name': ['name', 'full_name', 'firstName', 'lastName'],
    'email': ['email', 'userEmail', 'email_address'],
    'gender_preference': ['groupGenderPreference', 'gender_pref'],
    # ... more mappings
}
```

---

## 👥 PHASE 2: Accountability Buddies (Highest Priority)

### Overview
Processes users who explicitly requested to be grouped with specific buddies. Uses graph-based clustering to find connected components of mutual accountability relationships.

### Algorithm Steps

#### 1. Participant Collection
```python
# Find users with accountability buddy requests
if has_accountability_buddies == True:
    accountability_participants.append(user)

# Find users referenced as buddies by others
referenced_buddies = extract_emails_from_buddy_fields()
```

#### 2. Email Extraction (Multiple Formats Supported)
- **Format 1**: `['Name (email@domain.com)', 'Another Name (email2@domain.com)']`
- **Format 2**: `['email1@domain.com', 'email2@domain.com']`
- **Format 3**: String representations of arrays

#### 3. Graph-Based Clustering
- **DFS Algorithm**: Finds connected components through mutual buddy relationships
- **Large Group Splitting**: Splits groups >7 members by prioritizing team names
- **Missing Buddy Handling**: Ensures referenced users are included in groups

#### 4. Team Name Integration
- **Team Groups**: Users with same `temporary_team_name` (no accountability buddies)
- **Combined Groups**: Merges team and accountability groups when possible

### Output Example
```
"Requested Group 3 (5 members) - Missing: user@domain.com"
"Team Group 1 - Study Group A (4 members)"
```

---

## 🧍 PHASE 3: Solo Participants (User Choice)

### Simple Logic
```python
if go_solo == True:
    solo_groups.append([user])
    # Creates single-member group
```

Users who explicitly choose individual work are placed in solo groups.

---

## 🎯 PHASE 4: Priority Same-Gender Groups (Females First)

### Overview
**NEW PRIORITY SYSTEM**: Processes `same_gender` participants first with females prioritized, targeting 5-member groups from same locations.

### Processing Order
1. **Females First**: Process female participants before males
2. **Same Gender Priority**: `groupGenderPreference = "same_gender"`
3. **Location Matching**: Exact same city/state
4. **Target Size**: 5 members per group
5. **Gap Filling**: Add `no_preference` participants from same location

### Algorithm Logic

#### Gender Separation
```python
sex_preference_groups = {
    'female': {'same_gender': [], 'no_preference': []},
    'male': {'same_gender': [], 'no_preference': []}
}
```

#### Location-Based Grouping
```python
# Philippines
location_key = f"PH_{province}_{city}"

# International
location_key = f"INT_{country}_{state}"
```

#### Group Formation with Gap Filling
```python
# Create groups from same_gender participants
while len(participants) >= 3:
    group_members = participants[:5]  # Target 5

    # Fill gaps with no_preference from same location
    if len(group_members) < 5:
        fillers = find_no_preference_same_location()
        group_members.extend(fillers[:fillers_needed])

    create_group(group_members)
```

### Output Examples
```
"Group 1 (female, same_gender, Province: Cebu, City: Cebu City)"
"Group 3 (male, same_gender, Country: USA, State: California)"
```

---

## 🌍 PHASE 5: Regular Algorithmic Grouping (Remaining Participants)

### Hierarchical Geographic Grouping

#### Step 1: Gender-Based Separation
```python
if gender_preference == 'same_gender':
    if gender_identity == 'LGBTQ+':
        gender_key = f"lgbtq+_{sex}"
    else:
        gender_key = sex  # 'male', 'female'
elif gender_preference == 'no_preference':
    gender_key = 'no_preference'
```

#### Step 2: Geographic Separation
```python
# PHILIPPINES vs INTERNATIONAL
if residing_ph in ['1', 'true', 'philippines']:
    ph_rows.append(participant)
else:
    non_ph_rows.append(participant)
```

### Philippines Grouping (Hierarchical)

#### Level 1: Regional Sorting
- **Regions**: Luzon → Visayas → Mindanao → Unknown
- **Sorting**: By geographic region first, then province name

#### Level 2: Province-Level Grouping
- Groups by province within regions
- **Example**: All Metro Manila participants grouped together

#### Level 3: City-Level Optimization
```python
# PRIORITY: Complete 5-member groups from same city
for city in province:
    while len(city_members) >= 5:
        create_group(city_members[:5])  # Same-city group

    # Store remaining <5 for mixing
    remaining_by_city[city] = city_members

# SECOND PASS: Mix remaining city members
combine_remaining_cities()  # Never split city units
```

### International Grouping (Hierarchical)

#### Level 1: Country Sorting
- Alphabetical country sorting

#### Level 2: State-Level Optimization
```python
# PRIORITY: Complete groups from same state
for state in country:
    while len(state_members) >= 5:
        create_group(state_members[:5])

    # Mix with other states if needed
    if remaining:
        mix_with_other_states(remaining)
```

### Group Naming Convention
```
"Group 5 (male, Province: Metro Manila, City: Quezon City)"
"Group 10 (no_preference, Country: United States, State: CA)"
```

---

## 🔄 PHASE 6: Small Group Optimization

### Post-Processing Algorithm
```python
def merge_small_groups(grouped, column_mapping):
    # Find groups with <4 members
    if len(group) < 4 and group_name.startswith("Group "):
        # Merge based on geographic + gender compatibility
        find_similar_groups(group, location_key, gender_key)
```

### Merging Strategies
1. **Exact Match**: Same location + same gender preference
2. **Broader Match**: Same gender preference only
3. **Final Merge**: Combine remaining <4 groups by gender only
4. **Size Limits**: Never exceed 5 members per group

---

## 🎨 FORMATTING LOGIC

### Excel Output Structure

#### Sheet Layout
```
Group Name | User ID 1-7 | Name 1-7 | Location 1-7 | Coach 1-7
Gender Identity | Sex | Residing in PH | Gender Preference
Country | Province | City | State | Previous Coach Name
```

#### Color Coding System

##### User ID Colors (Sex-Based)
```python
SEX_COLOR = {
    'male': 'ADD8E6',    # Light Blue
    'female': 'FFC0CB',  # Pink
}
```

##### Special Formatting
- **Green Fill**: `get_bigger` goal participants
- **Maroon Font**: LGBTQ+ participants
- **Bold Text**: Same-gender preference groups
- **Underline**: Users with accountability buddies

##### Group Highlighting
- **Green Background**: Requested groups (accountability buddies) ≥5 members
- **Light Blue Background**: Regular groups ≥5 members + same location

### Visual Indicators
- **Group Names**: Color-coded based on group type and size
- **Member Formatting**: Individual styling based on participant attributes
- **Location Display**: Smart formatting (PH vs International)

---

## ⚙️ CONFIGURATION OPTIONS

### File Paths
```python
INPUT_FILE = 'merged_users_grouping_preferences.xlsx'
OUTPUT_FILE = 'grouped_participants.xlsx'
```

### Geographic Regions
```python
PHILIPPINES_REGIONS = {
    'luzon': ['Metro Manila', 'Batangas', 'Bulacan', ...],
    'visayas': ['Cebu', 'Bohol', 'Iloilo', ...],
    'mindanao': ['Davao', 'Cotabato', 'Bukidnon', ...]
}
```

### Timezone Mappings
```python
TIMEZONE_REGIONS = {
    'pst_pdt': ['United States', 'Canada'],  # Pacific Time
    'est_edt': ['United States', 'Canada'],  # Eastern Time
    # ... more mappings
}
```

---

## 📈 DIAGNOSTIC REPORTING

### User Status Tracking
```python
user_tracking[user_id] = {
    'email': email,
    'status': 'accountability_buddies',  # or 'solo', 'regular_grouping', etc.
    'reason': 'Has accountability buddies',
    'row_data': participant_data
}
```

### Analysis Reports
- **User Distribution**: Breakdown by status and group type
- **Missing Users**: Identifies unassigned participants
- **Duplicate Detection**: Finds users in multiple groups
- **Group Size Analysis**: Statistics on group distributions

### Console Output
```
📊 USER DISTRIBUTION DIAGNOSTIC REPORT
Total original users: 1140
Solo groups created: 25
Regular groups created: 45
Accountability groups: 30
Missing users: 0
✅ All users accounted for
```

---

## 🔧 EMAIL PROCESSING

### Supported Formats
```python
# Dictionary format
{'1': 'email1@domain.com', '2': 'email2@domain.com'}

# List with names
['John Doe (john@email.com)', 'Jane Smith (jane@email.com)']

# Simple email list
['email1@domain.com', 'email2@domain.com']

# String representations
"['Name (email)', 'email2']"
```

### Email Normalization
```python
# Known aliases
email_mapping = {
    'jaw.ybanez@yahoo.com': 'yo21st@gmail.com'
}

# Apply mapping
normalized_email = email_mapping.get(email, email)
```

---

## 📋 OUTPUT EXAMPLES

### Requested Groups (Accountability Buddies)
```
Requested Group 1 (5 members)
├── User ID: 123 | Name: John Doe | Location: Cebu City | Coach: Jane Smith
├── User ID: 124 | Name: Jane Smith | Location: Cebu City | Coach: John Doe
├── User ID: 125 | Name: Bob Wilson | Location: Cebu City | Coach: Alice Brown
├── User ID: 126 | Name: Alice Brown | Location: Cebu City | Coach: Bob Wilson
└── User ID: 127 | Name: Carol Davis | Location: Cebu City | Coach: David Evans

Gender Identity: Straight | Sex: Mixed | Residing in PH: Yes
Gender Preference: Mixed | Country: Philippines | Province: Cebu
```

### Priority Same-Gender Groups
```
Group 2 (female, same_gender, Province: Cebu, City: Cebu City)
├── User ID: 201 | Name: Maria Santos | Location: Cebu City | Coach: Anna Reyes
├── User ID: 202 | Name: Anna Reyes | Location: Cebu City | Coach: Maria Santos
├── User ID: 203 | Name: Lisa Cruz | Location: Cebu City | Coach: Maria Santos
├── User ID: 204 | Name: Diana Flores | Location: Cebu City | Coach: Anna Reyes
└── User ID: 205 | Name: Rosa Garcia | Location: Cebu City | Coach: Lisa Cruz

Gender Identity: Straight | Sex: Female | Residing in PH: Yes
Gender Preference: Same Gender | Country: Philippines | Province: Cebu
```

### Regular Algorithmic Groups
```
Group 15 (no_preference, Province: Metro Manila, City: Quezon City)
├── User ID: 301 | Name: Jose Rodriguez | Location: Quezon City | Coach: Maria Santos
├── User ID: 302 | Name: Elena Vargas | Location: Quezon City | Coach: Jose Rodriguez
├── User ID: 303 | Name: Miguel Torres | Location: Quezon City | Coach: Elena Vargas
├── User ID: 304 | Name: Sofia Morales | Location: Quezon City | Coach: Miguel Torres
└── User ID: 305 | Name: Diego Luna | Location: Quezon City | Coach: Sofia Morales

Gender Identity: Mixed | Sex: Mixed | Residing in PH: Yes
Gender Preference: No Preference | Country: Philippines | Province: Metro Manila
```

---

## 🚀 USAGE INSTRUCTIONS

### Basic Usage
```python
from group_assignment_to_excel import main

# Update INPUT_FILE path in the configuration section
INPUT_FILE = 'your_merged_data.xlsx'

# Run the complete pipeline
main()
```

### Configuration
1. Update `INPUT_FILE` path to your merged participant data
2. Optionally modify `OUTPUT_FILE` for custom output location
3. Adjust color schemes in `SEX_COLOR`, `LGBTQ_FONT_COLOR`, etc.
4. Modify geographic regions if needed

### Input Data Requirements
- Excel/CSV format with participant information
- Columns automatically detected using flexible mapping
- Minimum required: user_id, email, gender_preference, sex, location fields

### Output
- Formatted Excel file with color coding
- Multiple sheets with group assignments
- Diagnostic reports in console
- Comprehensive participant tracking

---

## 🔍 TROUBLESHOOTING

### Common Issues

#### 1. Column Mapping Errors
**Symptom**: `❌ column_name: NOT FOUND`
**Solution**: Check column names in input file, add variations to `EXPECTED_COLUMNS`

#### 2. Missing Participants
**Symptom**: Users not appearing in any groups
**Solution**: Check `joiningAsStudent` field, verify email formats

#### 3. Incorrect Group Sizes
**Symptom**: Groups with unexpected member counts
**Solution**: Review `merge_small_groups()` logic, check target sizes

#### 4. Geographic Grouping Issues
**Symptom**: Participants grouped across distant locations
**Solution**: Verify `residing_ph` values, check location field accuracy

### Debug Mode
Enable detailed logging by modifying the diagnostic report sections to print intermediate results.

---

## 📈 PERFORMANCE CHARACTERISTICS

- **Time Complexity**: O(n log n) for sorting, O(n²) worst case for graph algorithms
- **Space Complexity**: O(n) for participant storage and tracking
- **Typical Performance**: Processes 1000+ participants in <30 seconds
- **Memory Usage**: ~50MB for large datasets with extensive relationships

---

## 🔄 ALGORITHM EVOLUTION

### Version History
- **v1.0**: Basic geographic grouping
- **v2.0**: Added accountability buddy support
- **v3.0**: Implemented gender preference handling
- **v4.0**: Added priority same-gender grouping (current)

### Future Enhancements
- Machine learning-based group optimization
- Dynamic group size adjustment based on engagement data
- Integration with external calendar/meeting systems
- Advanced timezone conflict resolution

---

*This documentation covers the complete Kaizen Group Assignment System as of the latest implementation. For technical support or feature requests, refer to the codebase comments or contact the development team.*
