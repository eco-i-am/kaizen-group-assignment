#!/usr/bin/env python3
"""
Simple test to verify file uploader configuration
"""

import streamlit as st
import pandas as pd

def test_file_uploader():
    """Test the file uploader configuration"""
    
    st.title("File Uploader Test")
    
    # Test the exact configuration from the app
    file_type = st.radio(
        "Choose file type:",
        ["CSV File", "Excel File (Merged Data)"],
        help="Select the type of file you want to upload"
    )
    
    if file_type == "CSV File":
        st.write("### CSV File Upload")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file with participant data"
        )
    else:
        st.write("### Excel File Upload")
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with merged data (should have 'Merged Data' sheet)"
        )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.write(f"File type: {uploaded_file.type}")
        st.write(f"File size: {uploaded_file.size} bytes")
        
        # Try to read the file
        try:
            if file_type == "CSV File":
                data = pd.read_csv(uploaded_file)
                st.write("✅ CSV file read successfully")
            else:
                data = pd.read_excel(uploaded_file, sheet_name='Merged Data')
                st.write("✅ Excel file read successfully")
            
            st.write(f"Data shape: {data.shape}")
            st.write(f"Columns: {list(data.columns)}")
            
        except Exception as e:
            st.error(f"Error reading file: {e}")

if __name__ == "__main__":
    test_file_uploader() 