# Kaizen Group Assignment System

A Python-based system for creating optimized group assignments for fitness and wellness programs. This system intelligently groups participants based on gender preferences, geographic location, and individual preferences while respecting solo work preferences.

## 🚀 Features

- **Smart Grouping Algorithm**: Groups participants based on multiple criteria
- **Gender Preference Support**: Respects same-gender and no-preference options
- **Geographic Optimization**: Groups by city (Philippines) or state (international)
- **Solo Participant Handling**: Identifies and handles participants who prefer to work alone
- **Visual Output**: Excel export with color-coded participants by gender identity
- **Data Analysis Tools**: Built-in analysis for understanding group distributions
- **Test Data Generation**: Tools for creating realistic test scenarios

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🛠️ Installation

1. **Clone or download the project files**

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📁 Project Structure

```
kaizen-group-assignment/
├── app.py                         # 🖥️ Web UI (Streamlit)
├── run_ui.py                     # 🚀 UI launcher script
├── group_assignment_to_excel.py   # Main grouping engine
├── generate_additional_records.py # Test data generator
├── analyze_scenarios.py           # Data analysis tool
├── participants.csv               # Input participant data
├── grouped_participants.xlsx     # Output grouped results
├── requirements.txt              # Python dependencies
└── README.md                    # This file
```

## 🎯 Usage

### Web Interface (Recommended)

Launch the user-friendly web interface:
```bash
python run_ui.py
```

Or directly with Streamlit:
```bash
streamlit run app_simple.py  # Simple version (no plotly)
streamlit run app.py         # Full version (with charts)
```

This opens a web browser with an intuitive interface for:
- 📁 Uploading participant data
- 👥 Creating groups with customizable options
- 📊 Viewing analytics and charts
- 📤 Exporting results in Excel or CSV format

### Command Line Interface

Run the main grouping script directly:
```bash
python group_assignment_to_excel.py
```

This will:
- Read participant data from `participants.csv`
- Apply the grouping algorithm
- Generate `grouped_participants.xlsx` with results

### Input Data Format

The system expects a CSV file (`participants.csv`) with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `user_id` | Unique participant identifier | `138` |
| `gender_identity` | Gender identity | `Male`, `Female`, `LGBTQ+` |
| `sex` | Biological sex | `Male`, `Female` |
| `residing_in_philippines` | Location indicator | `1` (PH), `0` (International) |
| `group_gender_preference` | Grouping preference | `same_gender`, `no_preference` |
| `country` | Country of residence | `Philippines`, `United States` |
| `province` | Province/State | `Metro Manila`, `California` |
| `city` | City | `Quezon City`, `Los Angeles` |
| `state` | State (for international) | `California` |
| `go_solo` | Solo preference | `1` (solo), `0` (group) |

### Output Format

The system generates an Excel file with:
- **Group assignments** with descriptive names
- **Color coding** by gender identity:
  - 🔵 Blue: Male participants
  - 🔴 Pink: Female participants  
  - 🟢 Green: LGBTQ+ participants
- **Member details** including user IDs, names, and cities
- **Group metadata** (gender preference, location info)

## 🔧 Grouping Algorithm

The system uses a hierarchical approach:

1. **Solo Participants**: Identifies participants with `go_solo = 1`
2. **Gender Preferences**: Groups by `group_gender_preference`
3. **Geographic Location**: 
   - Philippines: Groups by city
   - International: Groups by state
4. **Group Size**: Creates groups of up to 5 participants

### Grouping Logic

```python
# 1. Handle Solo Participants
if go_solo == 1:
    create_solo_group()

# 2. Group by Gender Preference
if gender_preference == "same_gender":
    group_by_gender_identity()
elif gender_preference == "no_preference":
    group_by_location()

# 3. Sub-group by Location
if residing_in_philippines == 1:
    group_by_city()
else:
    group_by_state()

# 4. Create Groups of 5
split_into_groups_of_5()
```

## 🛠️ Additional Tools

### Generate Test Data

Create additional participant records for testing:
```bash
python generate_additional_records.py
```

### Analyze Results

Analyze group distributions and scenarios:
```bash
python analyze_scenarios.py
```

## 📊 Example Output

The system creates groups like:
- `Group 1 (same_gender, City: Quezon City)` - 5 participants
- `Group 2 (no_preference, State: California)` - 4 participants  
- `Solo 1` - Individual participant

## 🔧 Configuration

### Customizing Group Size

Edit `group_assignment_to_excel.py` and modify the group size in the grouping logic:
```python
# Change from 5 to your desired group size
for i in range(0, len(members), 5):  # Change 5 here
```

### Adding New Grouping Criteria

Modify the `group_participants()` function to add new grouping logic based on:
- Experience level
- Fitness goals
- Age groups
- Coach assignments

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've activated the virtual environment
   ```bash
   source venv/bin/activate
   ```

2. **Missing Dependencies**: Reinstall requirements
   ```bash
   pip install -r requirements.txt
   ```

3. **File Not Found**: Ensure `participants.csv` is in the project directory

4. **Permission Errors**: Check file permissions for input/output files

### Python Version Compatibility

- **Python 3.8-3.11**: Full compatibility
- **Python 3.12+**: May need updated pandas version
- **Python 3.13**: Use updated requirements.txt

## 🤝 Contributing

To extend the system:

1. **Add New Grouping Criteria**: Modify `group_participants()` function
2. **Custom Output Formats**: Extend `save_to_excel()` function  
3. **Additional Analysis**: Create new analysis scripts
4. **UI Improvements**: Add command-line interface with Click

## 📝 License

This project is designed for internal use by Kaizen Group for fitness program management.

## 📞 Support

For questions or issues:
- Check the troubleshooting section above
- Review the code comments in each script
- Ensure your input data follows the expected format

---

**Note**: This system is specifically designed for fitness and wellness programs with consideration for gender preferences, geographic proximity, and individual work preferences. 