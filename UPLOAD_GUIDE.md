# Upload Guide - CSV and Excel File Support

The upload functionality has been updated to support both CSV files and Excel files with merged data. This guide explains how to use each option.

## Upload Options

### Option 1: CSV File Upload (Original Format)

**When to use:** When you have participant data in CSV format with the standard column structure.

**Required columns:**
- `user_id`: Unique participant identifier
- `gender_identity`: Gender identity (Male, Female, LGBTQ+)
- `sex`: Biological sex (Male, Female)
- `residing_in_philippines`: Location indicator (1 for PH, 0 for International)
- `group_gender_preference`: Grouping preference (same_gender, no_preference)
- `country`: Country of residence
- `province`: Province/State
- `city`: City
- `state`: State (for international participants)
- `go_solo`: Solo preference (1 for solo, 0 for group)

**How to upload:**
1. Go to "Upload Data" page
2. Select "CSV File"
3. Choose your CSV file
4. The system will validate the required columns
5. If valid, the data will be loaded and ready for group creation

### Option 2: Excel File Upload (Merged Data)

**When to use:** When you have merged user and grouping preference data from the API or other sources.

**File requirements:**
- Excel file (.xlsx or .xls)
- Must contain a "Merged Data" sheet
- Column names will be automatically detected

**Expected columns (automatic detection):**
- `user_id`, `id`, `userid`, `user id`
- `name`, `full_name`, `fullname`, `first_name`, `last_name`
- `gender_identity`, `gender`, `genderidentity`
- `sex`, `biological_sex`, `biologicalsex`
- `residing_ph`, `residing_in_philippines`, `philippines_resident`
- `gender_preference`, `grouping_preference`, `preference`
- `country`, `nationality`
- `province`, `state_province`
- `city`, `municipality`
- `state`, `region`
- `go_solo`, `solo`, `prefer_solo`

**How to upload:**
1. Go to "Upload Data" page
2. Select "Excel File (Merged Data)"
3. Choose your Excel file
4. The system will:
   - Read the "Merged Data" sheet
   - Automatically detect column mappings
   - Validate essential columns
   - Show column mapping details
5. If valid, the data will be loaded and ready for group creation

## Step-by-Step Upload Process

### For CSV Files:
```
1. Navigate to "Upload Data" page
2. Select "CSV File" radio button
3. Click "Browse files" and select your CSV
4. Wait for validation
5. Review data preview and statistics
6. Go to "Create Groups" page to create groups
```

### For Excel Files:
```
1. Navigate to "Upload Data" page
2. Select "Excel File (Merged Data)" radio button
3. Click "Browse files" and select your Excel file
4. Wait for column mapping detection
5. Review column mapping details (expand the section)
6. Review data preview and statistics
7. Go to "Create Groups" page to create groups
```

## Data Validation

### CSV Validation:
- Checks for all required columns
- Shows missing columns if any
- Displays data statistics

### Excel Validation:
- Checks for "Merged Data" sheet
- Validates essential columns (user_id, gender_identity, gender_preference)
- Shows column mapping details
- Displays data statistics

## Error Handling

### Common CSV Errors:
- **Missing columns:** Add the required columns to your CSV
- **Invalid format:** Ensure the file is a valid CSV
- **Wrong data types:** Check that numeric fields contain numbers

### Common Excel Errors:
- **No "Merged Data" sheet:** Ensure your Excel file has this sheet
- **Missing essential columns:** Add user_id, gender_identity, and gender_preference columns
- **Invalid file format:** Use .xlsx or .xls format

## Example Files

Test files have been created to demonstrate the functionality:

- `test_upload_data.csv` - Example CSV file with standard format
- `test_merged_data.xlsx` - Example Excel file with merged data format

You can use these files to test the upload functionality.

## Integration with Group Creation

After successful upload:

1. **CSV Data:** Will be available as "CSV Data" in the group creation page
2. **Excel Data:** Will be available as "Merged API Data" in the group creation page

The group creation process will automatically handle the different data formats and create appropriate groups.

## Tips for Success

### For CSV Files:
- Use the exact column names listed above
- Ensure data types are correct (numbers for numeric fields)
- Check for missing values in required fields

### For Excel Files:
- Always include a "Merged Data" sheet
- Use descriptive column names that match the expected patterns
- Include at least the essential columns (user_id, gender_identity, gender_preference)
- The system is flexible with column names - it will try to match variations

## Troubleshooting

### Upload Fails:
1. Check file format (.csv for CSV, .xlsx/.xls for Excel)
2. Verify required columns are present
3. Check for data format issues
4. Ensure Excel files have "Merged Data" sheet

### Column Mapping Issues:
1. Review the column mapping details in the UI
2. Check if your column names match the expected patterns
3. Consider renaming columns to match expected names

### Data Statistics Look Wrong:
1. Check your data for missing or incorrect values
2. Verify that numeric fields contain valid numbers
3. Ensure boolean fields use consistent values (1/0, true/false, etc.) 