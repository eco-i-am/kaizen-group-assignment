import pandas as pd

def test_accountability_buddies():
    try:
        # Try to read the sample merged data
        df = pd.read_excel('sample_merged_data.xlsx', sheet_name='Merged Data')
        print(f"Successfully read sample_merged_data.xlsx with {len(df)} records")
        print(f"Available columns: {list(df.columns)}")
        
        # Check for accountability buddies related columns
        accountability_cols = [col for col in df.columns if 'accountability' in col.lower() or 'buddy' in col.lower()]
        print(f"\nAccountability buddies related columns: {accountability_cols}")
        
        # Check for has_accountability_buddies column
        has_buddies_cols = [col for col in df.columns if 'has' in col.lower() and ('accountability' in col.lower() or 'buddy' in col.lower())]
        print(f"Has accountability buddies columns: {has_buddies_cols}")
        
        # Show first few rows for these columns
        if accountability_cols:
            print(f"\nFirst 5 rows of accountability buddies data:")
            for col in accountability_cols:
                print(f"\n{col}:")
                for i, value in enumerate(df[col].head()):
                    print(f"  Row {i}: {value} (type: {type(value)})")
        
        # Check if there are any non-null values
        if accountability_cols:
            for col in accountability_cols:
                non_null_count = df[col].notna().sum()
                non_empty_count = (df[col].astype(str).str.strip() != '').sum()
                print(f"\n{col}: {non_null_count} non-null values, {non_empty_count} non-empty values")
                
                # Show some non-empty values
                non_empty_values = df[df[col].astype(str).str.strip() != ''][col].head()
                if len(non_empty_values) > 0:
                    print(f"  Sample non-empty values: {list(non_empty_values)}")
        
    except Exception as e:
        print(f"Error reading sample_merged_data.xlsx: {e}")
        
        # Try other Excel files
        excel_files = ['test_merged_data.xlsx', 'grouped_participants_merged_20250716_215553.xlsx']
        for file in excel_files:
            try:
                print(f"\nTrying {file}...")
                df = pd.read_excel(file, sheet_name='Merged Data')
                print(f"Successfully read {file} with {len(df)} records")
                print(f"Available columns: {list(df.columns)}")
                
                accountability_cols = [col for col in df.columns if 'accountability' in col.lower() or 'buddy' in col.lower()]
                print(f"Accountability buddies related columns: {accountability_cols}")
                break
            except Exception as e2:
                print(f"Error reading {file}: {e2}")

if __name__ == "__main__":
    test_accountability_buddies() 