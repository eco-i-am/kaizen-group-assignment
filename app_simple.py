import streamlit as st
import pandas as pd
from collections import defaultdict
import io
from datetime import datetime
import os
import requests
import json

# Import the grouping logic from the existing script
from group_assignment_to_excel import group_participants, save_to_excel, find_column_mapping

def get_available_data():
    """Get data from any available source in the session state"""
    # Check for different possible data sources in order of preference
    if 'participants_data' in st.session_state:
        data = st.session_state.participants_data
    elif 'merged_data' in st.session_state:
        data = st.session_state.merged_data
    elif 'all_api_records' in st.session_state:
        data = st.session_state.all_api_records
    elif 'api_data' in st.session_state and isinstance(st.session_state.api_data, dict) and 'data' in st.session_state.api_data:
        data = st.session_state.api_data['data']
    else:
        return None

    # Convert data to DataFrame if it's not already
    if not isinstance(data, pd.DataFrame):
        try:
            data = pd.DataFrame(data)
        except Exception:
            return None

    return data

def format_location_display(member, column_mapping):
    """Format location display based on residing_ph status"""
    residing_ph = str(member.get(column_mapping.get('residing_ph'), '0')).strip().lower()
    
    if residing_ph in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
        # Philippines resident - show "city, province" format
        city = member.get(column_mapping.get('city'), '')
        province = member.get(column_mapping.get('province'), '')
        
        # Use "MM" as acronym for Metro Manila
        if province and str(province).lower() == 'metro manila':
            province = 'MM'
        
        if city and province:
            return f"{city}, {province}"
        elif city:
            return city
        elif province:
            return province
        else:
            return ''
    else:
        # International resident - show "State, Country"
        state = member.get(column_mapping.get('state'), '')
        country = member.get(column_mapping.get('country'), '')
        if state and country:
            return f"{state}, {country}"
        elif country:
            return country
        else:
            return member.get(column_mapping.get('city'), '')

def create_download_buttons(solo_groups, grouped, column_mapping=None, excluded_users=None, requested_groups=None, combined_group_info=None):
    """Create download buttons for Excel and CSV files"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Create Excel file
        output_buffer = io.BytesIO()
        save_to_excel(solo_groups, grouped, output_buffer, column_mapping, excluded_users, requested_groups, combined_group_info)
        output_buffer.seek(0)
        
        st.download_button(
            label="📥 Download Excel File",
            data=output_buffer.getvalue(),
            file_name=f"kaizen_groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Create CSV format
        csv_data = []
        
        # Helper function to get value safely
        def get_value(participant, key, default=''):
            if column_mapping and key in column_mapping:
                return participant.get(column_mapping[key], default)
            else:
                # Fallback to old format
                if key == 'user_id':
                    return participant.get(0, default) if isinstance(participant, (list, tuple)) else participant.get('user_id', default)
                elif key == 'name':
                    return participant.get(1, default) if isinstance(participant, (list, tuple)) else participant.get('name', default)
                elif key == 'gender_identity':
                    return participant.get(3, default) if isinstance(participant, (list, tuple)) else participant.get('gender_identity', default)
                elif key == 'city':
                    return participant.get(18, default) if isinstance(participant, (list, tuple)) else participant.get('city', default)
                else:
                    return default
        
        # Add requested groups to CSV
        if requested_groups:
            for i, group in enumerate(requested_groups, 1):
                for participant in group:
                    csv_data.append({
                        'Group': f'Requested Group {i}',
                        'User ID': get_value(participant, 'user_id'),
                        'Name': get_value(participant, 'name'),
                        'Gender': get_value(participant, 'gender_identity'),
                        'City': format_location_display(participant, column_mapping) if column_mapping else get_value(participant, 'city'),
                        'Type': 'Requested'
                    })
        
        for i, group in enumerate(solo_groups, 1):
            participant = group[0]
            csv_data.append({
                'Group': f'Solo {i}',
                'User ID': get_value(participant, 'user_id'),
                'Name': get_value(participant, 'name'),
                'Gender': get_value(participant, 'gender_identity'),
                'City': format_location_display(participant, column_mapping) if column_mapping else get_value(participant, 'city'),
                'Type': 'Solo'
            })
        
        for group_name, members in grouped.items():
            for member in members:
                csv_data.append({
                    'Group': group_name,
                    'User ID': get_value(member, 'user_id'),
                    'Name': get_value(member, 'name'),
                    'Gender': get_value(member, 'gender_identity'),
                    'City': format_location_display(member, column_mapping) if column_mapping else get_value(member, 'city'),
                    'Type': 'Group'
                })
        
        # Add excluded users to CSV
        if excluded_users:
            for user in excluded_users:
                csv_data.append({
                    'Group': 'Excluded',
                    'User ID': get_value(user, 'user_id'),
                    'Name': get_value(user, 'name'),
                    'Gender': get_value(user, 'gender_identity'),
                    'City': format_location_display(user, column_mapping) if column_mapping else get_value(user, 'city'),
                    'Type': 'Excluded'
                })
        
        csv_df = pd.DataFrame(csv_data)
        csv_buffer = io.StringIO()
        csv_df.to_csv(csv_buffer, index=False)
        
        st.download_button(
            label="📥 Download CSV File",
            data=csv_buffer.getvalue(),
            file_name=f"kaizen_groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Page configuration
st.set_page_config(
    page_title="Kaizen Group Assignment System",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🏋️ Kaizen Group Assignment System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["🔗 API Data", "📁 Data Management", "📈 Analysis", "⚙️ Settings"]
        )
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        data = get_available_data()
        if data is not None:
            st.metric("Total Participants", len(data))
            try:
                solo_count = len(data[data['go_solo'] == 1]) if 'go_solo' in data.columns else 0
                st.metric("Solo Participants", solo_count)
                group_count = len(data[data['go_solo'] == 0]) if 'go_solo' in data.columns else len(data)
                st.metric("Group Participants", group_count)
            except:
                st.metric("Data Loaded", "✅")
        else:
            st.info("Upload or fetch data to see statistics")
    
    # Page routing
    if page == "🔗 API Data":
        show_api_page()
    elif page == "📁 Data Management":
        show_data_management_page()
    elif page == "📈 Analysis":
        show_analysis_page()
    elif page == "⚙️ Settings":
        show_settings_page()

def show_upload_page():
    st.header("📁 Upload Participant Data")

    st.markdown("""
    ### Upload your merged Excel file
    The system supports Excel files with merged user and grouping preference data.
    The file should contain a "Merged Data" sheet with columns like:
    - `user_id`, `full_name`, `gender_identity`, `biological_sex`
    - `residing_in_philippines`, `grouping_preference`, `country`
    - `state_province`, `city`, `region`, `prefer_solo`

    **Note:** The system will automatically detect column names and map them appropriately.
    """)

    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with merged data (should have 'Merged Data' sheet)"
    )
    
    if uploaded_file is not None:
        try:
            # Read the Excel file
            try:
                data = pd.read_excel(uploaded_file, sheet_name='Merged Data')
            except Exception as e:
                st.error(f"Could not read 'Merged Data' sheet: {str(e)}")
                st.info("Please ensure your Excel file has a 'Merged Data' sheet.")
                return

            # Find column mapping
            column_mapping = find_column_mapping(data)

            # Check for essential columns using flexible mapping
            essential_fields = ['user_id', 'gender_identity', 'gender_preference']
            missing_essential = [field for field in essential_fields if not column_mapping.get(field)]

            if missing_essential:
                detected_cols = ', '.join(list(data.columns))
                st.error(f"Missing essential columns: {', '.join(missing_essential)}")
                st.info(f"Please ensure your Excel file contains columns for user_id, gender_identity, and gender_preference.\nDetected columns: {detected_cols}")
                st.info("The system accepts alternative column names such as 'genderPref', 'goSolo', etc. See documentation for details.")
                return

            # Store data in session state
            st.session_state.merged_data = data
            st.session_state.column_mapping = column_mapping
            data_source = "Merged Excel"
            
            # Show success message
            st.success("✅ Data uploaded successfully!")
            st.info(f"Loaded {len(data)} participants from {data_source}")
            
            # Show data preview
            st.subheader("📋 Data Preview")
            st.dataframe(data.head(), use_container_width=True)
            
            # Show column mapping
            st.subheader("🔍 Column Mapping")
            with st.expander("View detected column mappings"):
                for key, value in column_mapping.items():
                    if value:
                        st.write(f"**{key}:** {value}")
                    else:
                        st.write(f"**{key}:** ❌ Not found")
            
            # Show data statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Data Statistics")
                st.write(f"**Total Participants:** {len(data)}")
                
                # Get solo count based on data type
                if file_type == "CSV File":
                    solo_count = len(data[data['go_solo'] == 1])
                    group_count = len(data[data['go_solo'] == 0])
                    ph_count = len(data[data['residing_in_philippines'] == 1])
                else:
                    go_solo_col = column_mapping.get('go_solo')
                    if go_solo_col:
                        go_solo_values = data[go_solo_col].astype(str).str.strip().str.lower()
                        solo_count = go_solo_values.isin(['1', '1.0', 'true']).sum()
                        group_count = len(data) - solo_count
                    else:
                        solo_count = 0
                        group_count = len(data)
                    
                    residing_ph_col = column_mapping.get('residing_ph')
                    if residing_ph_col:
                        ph_values = data[residing_ph_col].astype(str).str.strip().str.lower()
                        ph_count = ph_values.isin(['1', 'true', 'yes', 'ph', 'philippines']).sum()
                    else:
                        ph_count = 0
                
                st.write(f"**Solo Participants:** {solo_count}")
                st.write(f"**Group Participants:** {group_count}")
                st.write(f"**Philippines Residents:** {ph_count}")
            
            with col2:
                st.subheader("🎯 Gender Preferences")
                if file_type == "CSV File":
                    gender_pref_counts = data['group_gender_preference'].value_counts()
                else:
                    gender_pref_col = column_mapping.get('gender_preference')
                    if gender_pref_col:
                        gender_pref_counts = data[gender_pref_col].value_counts()
                    else:
                        gender_pref_counts = pd.Series({'Unknown': len(data)})
                
                for pref, count in gender_pref_counts.items():
                    st.write(f"**{pref}:** {count}")
            
            # Show next steps
            st.success("✅ Data is ready for group creation!")
            st.info("💡 Go to the 'Create Groups' page to create groups from this data.")
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please ensure the file is a valid Excel format with a 'Merged Data' sheet.")

def show_grouping_page():
    st.header("👥 Create Groups")
    
    # Check for different data sources
    has_csv_data = 'participants_data' in st.session_state
    has_merged_data = 'merged_data' in st.session_state
    
    if not has_csv_data and not has_merged_data:
        st.warning("Please upload participant data first!")
        st.info("Go to 'Upload Data' or 'API Data' page to get started.")
        return
    
    # Data source selection
    if has_csv_data and has_merged_data:
        data_source = st.radio(
            "Choose data source:",
            ["CSV Data", "Merged API Data"],
            help="Select which dataset to use for group creation"
        )
    elif has_csv_data:
        data_source = "CSV Data"
    else:
        data_source = "Merged API Data"
    
    # Get the appropriate data
    if data_source == "CSV Data":
        data = st.session_state.participants_data
        data_format = "csv"
    else:
        data = st.session_state.merged_data
        data_format = "merged"
    
    # Grouping options
    st.subheader("⚙️ Grouping Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        group_size = st.slider("Group Size", min_value=2, max_value=10, value=5, 
                              help="Maximum number of participants per group")
        
        include_solo = st.checkbox("Include Solo Participants", value=True,
                                  help="Create separate entries for solo participants")
    
    with col2:
        color_coding = st.checkbox("Enable Color Coding", value=True,
                                  help="Color code participants by gender identity in Excel")
        
        export_format = st.selectbox("Export Format", ["Excel", "CSV"], 
                                    help="Choose output format")
    
    # Information about small group merging
    st.info("""
    **🔄 Small Group Merging:** Groups with less than 5 members will be automatically merged with participants from similar countries/regions:
    - **Southeast Asia:** Philippines, Indonesia, Malaysia, Thailand, Vietnam, Singapore, etc.
    - **East Asia:** China, Japan, South Korea, Taiwan, Hong Kong, Macau
    - **South Asia:** India, Pakistan, Bangladesh, Sri Lanka, Nepal, Bhutan, Maldives
    - **North America:** United States, Canada, Mexico
    - **Europe:** UK, Germany, France, Italy, Spain, Netherlands, Belgium, Switzerland, Austria, Sweden, Norway, Denmark, Finland
    - **Middle East:** Saudi Arabia, UAE, Qatar, Kuwait, Bahrain, Oman, Jordan, Lebanon, Israel, Turkey
    - **Africa:** South Africa, Nigeria, Kenya, Egypt, Morocco, Ghana, Ethiopia
    - **Oceania:** Australia, New Zealand, Fiji, Papua New Guinea
    
    **⚠️ Important:** Participants with "same_gender" preference will NEVER be mixed with participants who have "no_preference". Philippines participants are never mixed with participants from other countries.
    """)
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            respect_gender_pref = st.checkbox("Respect Gender Preferences", value=True)
            geographic_grouping = st.checkbox("Geographic Grouping", value=True)
        
        with col2:
            max_groups = st.number_input("Maximum Groups", min_value=1, value=100,
                                       help="Limit the number of groups created")
            group_naming = st.selectbox("Group Naming Convention", 
                                      ["Descriptive", "Simple", "Custom"])
    
    # Create groups button
    if st.button("🚀 Create Groups", type="primary", use_container_width=True):
        with st.spinner("Creating groups..."):
            try:
                column_mapping = None
                
                if data_format == "merged":
                    # For merged data, find column mapping
                    column_mapping = find_column_mapping(data)
                    st.info(f"📋 Column mapping detected: {len(column_mapping)} fields mapped")
                    
                    # Show column mapping details
                    with st.expander("🔍 Column Mapping Details"):
                        for key, value in column_mapping.items():
                            if value:
                                st.write(f"**{key}:** {value}")
                            else:
                                st.write(f"**{key}:** ❌ Not found")
                    
                    # Convert DataFrame to list of dictionaries
                    data_list = data.to_dict('records')
                else:
                    # For CSV data, convert to list format
                    data_list = data.values.tolist()
                
                # Call the grouping function
                solo_groups, grouped, excluded_users, requested_groups, combined_group_info = group_participants(data_list, column_mapping)
                
                # Store results in session state
                st.session_state.solo_groups = solo_groups
                st.session_state.grouped = grouped
                st.session_state.excluded_users = excluded_users
                st.session_state.requested_groups = requested_groups
                st.session_state.combined_group_info = combined_group_info
                st.session_state.column_mapping = column_mapping
                
                # Display results
                st.success("✅ Groups created successfully!")
                
                # Show summary
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Solo Groups", len(solo_groups))
                
                with col2:
                    st.metric("Regular Groups", len(grouped))
                
                with col3:
                    total_participants = sum(len(group) for group in solo_groups) + sum(len(members) for members in grouped.values())
                    st.metric("Total Grouped", total_participants)
                
                # Show groups preview
                st.subheader("📋 Groups Preview")
                
                # Helper function to get participant info
                def get_participant_info(participant, column_mapping):
                    if column_mapping:
                        user_id = participant.get(column_mapping.get('user_id'), 'Unknown')
                        name = participant.get(column_mapping.get('name'), 'Unknown')
                        gender = participant.get(column_mapping.get('gender_identity'), 'Unknown')
                    else:
                        # Fallback to old format
                        user_id = participant[0] if len(participant) > 0 else 'Unknown'
                        name = participant[1] if len(participant) > 1 else 'Unknown'
                        gender = participant[3] if len(participant) > 3 else 'Unknown'
                    return user_id, name, gender
                
                # Solo groups
                if solo_groups:
                    st.write("**Solo Participants:**")
                    for i, group in enumerate(solo_groups[:5], 1):  # Show first 5
                        participant = group[0]
                        user_id, name, gender = get_participant_info(participant, column_mapping)
                        st.write(f"  {i}. User {user_id} - {name} ({gender})")
                
                # Regular groups
                if grouped:
                    st.write("**Regular Groups:**")
                    for i, (group_name, members) in enumerate(list(grouped.items())[:5], 1):  # Show first 5
                        st.write(f"  {i}. {group_name} ({len(members)} members)")
                        for member in members[:3]:  # Show first 3 members
                            user_id, name, gender = get_participant_info(member, column_mapping)
                            st.write(f"     - User {user_id} - {name}")
                        if len(members) > 3:
                            st.write(f"     ... and {len(members) - 3} more")
                
                # Export options
                st.subheader("📤 Export Results")
                
                # Store results in session state for download
                st.session_state.solo_groups = solo_groups
                st.session_state.grouped = grouped
                st.session_state.column_mapping = column_mapping
                
                create_download_buttons(solo_groups, grouped, column_mapping, excluded_users, requested_groups, combined_group_info)
            
            except Exception as e:
                st.error(f"Error creating groups: {str(e)}")
                st.info("Please check your data format and try again.")
                import traceback
                st.error(f"Error details: {traceback.format_exc()}")

def show_analysis_page():
    st.header("📈 Analysis")
    
    if 'participants_data' not in st.session_state:
        st.warning("Please upload participant data first!")
        return
    
    data = st.session_state.participants_data
    
    # Analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Demographics", "🌍 Geographic", "👥 Grouping", "📈 Trends"])
    
    with tab1:
        st.subheader("📊 Demographic Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Gender Distribution:**")
            gender_counts = data['gender_identity'].value_counts()
            for gender, count in gender_counts.items():
                st.write(f"- {gender}: {count} participants")
        
        with col2:
            if 'lifting_experience' in data.columns:
                st.write("**Experience Level Distribution:**")
                exp_counts = data['lifting_experience'].value_counts()
                for exp, count in exp_counts.items():
                    st.write(f"- {exp}: {count} participants")
            else:
                st.info("Experience level data not available")
    
    with tab2:
        st.subheader("🌍 Geographic Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top Countries:**")
            country_counts = data['country'].value_counts().head(10)
            for country, count in country_counts.items():
                st.write(f"- {country}: {count} participants")
        
        with col2:
            st.write("**Philippines vs International:**")
            ph_count = len(data[data['residing_in_philippines'] == 1])
            int_count = len(data[data['residing_in_philippines'] == 0])
            st.write(f"- Philippines: {ph_count} participants")
            st.write(f"- International: {int_count} participants")
            
            # Show Philippines provinces
            if ph_count > 0 and 'province' in data.columns:
                st.write("**Philippines Provinces:**")
                ph_data = data[data['residing_in_philippines'] == 1]
                province_counts = ph_data['province'].value_counts().head(5)
                for province, count in province_counts.items():
                    if province and str(province).lower() != 'nan':
                        st.write(f"- {province}: {count} participants")
    
    with tab3:
        st.subheader("👥 Grouping Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Gender Preferences:**")
            gender_pref_counts = data['group_gender_preference'].value_counts()
            for pref, count in gender_pref_counts.items():
                st.write(f"- {pref}: {count} participants")
        
        with col2:
            st.write("**Solo vs Group Preferences:**")
            solo_count = len(data[data['go_solo'] == 1])
            group_count = len(data[data['go_solo'] == 0])
            st.write(f"- Solo: {solo_count} participants")
            st.write(f"- Group: {group_count} participants")
    
    with tab4:
        st.subheader("📈 Data Trends")
        
        # Summary statistics
        st.write("**Data Summary:**")
        st.write(f"- Total participants: {len(data)}")
        st.write(f"- Solo participants: {len(data[data['go_solo'] == 1])}")
        st.write(f"- Group participants: {len(data[data['go_solo'] == 0])}")
        st.write(f"- Philippines residents: {len(data[data['residing_in_philippines'] == 1])}")
        st.write(f"- International participants: {len(data[data['residing_in_philippines'] == 0])}")
        
        # Data quality metrics
        st.write("**Data Quality:**")
        missing_data = data.isnull().sum()
        if missing_data.sum() > 0:
            st.warning(f"Missing data found: {missing_data.sum()} total missing values")
            st.write(missing_data[missing_data > 0])
        else:
            st.success("✅ No missing data found")

def show_user_list_page():
    """Page to generate and download a simple user list with 4 columns"""
    st.header("📋 User List Generator")

    st.markdown("""
    ### Generate User List Excel
    This page generates a simple Excel file containing all users with 4 key columns:
    - **User ID**: Unique participant identifier
    - **Name**: Participant's full name
    - **Location**: Formatted location (City, Province for PH; City, State, Country for international)
    - **Coach**: Previous coach assignment
    """)

    # Check if data is available from any source
    data = get_available_data()
    if data is None:
        st.warning("⚠️ No data available. Please upload data using the 'Upload Data' page or fetch data using the 'API Data' page.")
        return

    # Determine data source for display
    data_source = "Unknown"
    if 'participants_data' in st.session_state:
        data_source = "Uploaded Data"
    elif 'merged_data' in st.session_state:
        data_source = "Merged API Data"
    elif 'all_api_records' in st.session_state:
        data_source = "API Data"
    elif 'api_data' in st.session_state:
        data_source = "API Data"

    st.info(f"📊 Found {len(data)} participants from {data_source}")

    # Generate user list button
    if st.button("🚀 Generate User List Excel", type="primary", use_container_width=True):
        try:
            with st.spinner("Generating user list..."):
                # Import the user list function
                from user_list_to_excel import save_user_list_to_excel
                from user_list_to_excel import find_column_mapping as find_column_mapping_user

                # Convert data to list of dicts (same format as the Excel processing)
                data_dicts = data.to_dict('records')

                # Debug: Check for duplicates before processing
                user_id_col = None
                for col in data.columns:
                    if col.lower() in ['id_y', 'id', 'userid', 'user_id']:
                        user_id_col = col
                        break

                if user_id_col:
                    user_ids = data[user_id_col].dropna().astype(str).str.strip()
                    duplicate_count = len(user_ids) - len(user_ids.unique())
                    if duplicate_count > 0:
                        st.warning(f"⚠️ Found {duplicate_count} duplicate user IDs in the data!")
                        # Show some examples of duplicates
                        duplicates = user_ids[user_ids.duplicated(keep=False)]
                        if len(duplicates) > 0:
                            st.info(f"Example duplicate IDs: {', '.join(duplicates.unique()[:5])}")
                    else:
                        st.info(f"✅ No duplicate user IDs found ({len(user_ids.unique())} unique users)")
                else:
                    st.warning("⚠️ Could not find user ID column to check for duplicates")

                # Find column mapping
                column_mapping = find_column_mapping_user(data)

                # Create BytesIO buffer for download
                import io
                buffer = io.BytesIO()

                # Generate the Excel file
                save_user_list_to_excel(data_dicts, buffer, column_mapping)

                buffer.seek(0)

                st.success("✅ User list generated successfully!")

                # Download button
                st.download_button(
                    label="📥 Download User List Excel",
                    data=buffer,
                    file_name="user_list.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"❌ Error generating user list: {str(e)}")
            st.error("Please check that all required columns are present in your data")

    # Show column mapping info
    st.subheader("📋 Column Mapping")
    data_for_mapping = get_available_data()
    if data_for_mapping is not None:
        from user_list_to_excel import find_column_mapping as find_column_mapping_user
        column_mapping = find_column_mapping_user(data_for_mapping)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Required Columns:**")
            required_cols = ['user_id', 'name', 'residing_ph', 'city', 'province', 'state', 'country', 'previous_coach_name']
            for col in required_cols:
                status = "✅" if column_mapping.get(col) else "❌"
                mapped_to = f" → {column_mapping.get(col, 'Not found')}" if column_mapping.get(col) else ""
                st.write(f"{status} {col}{mapped_to}")

        with col2:
            st.markdown("**Optional Columns:**")
            optional_cols = ['gender_identity', 'sex', 'gender_preference', 'email', 'temporary_team_name']
            for col in optional_cols:
                status = "✅" if column_mapping.get(col) else "⚪"
                mapped_to = f" → {column_mapping.get(col, 'Not found')}" if column_mapping.get(col) else ""
                st.write(f"{status} {col}{mapped_to}")

def show_data_management_page():
    """Combined page for Upload Data, User List, and Create Groups"""

    # Upload Data Section
    st.header("📁 Upload Data")

    st.markdown("""
    ### Upload your merged Excel file
    The system supports Excel files with merged user and grouping preference data.
    The file should contain a "Merged Data" sheet with columns like:
    - `user_id`, `full_name`, `gender_identity`, `biological_sex`
    - `residing_in_philippines`, `grouping_preference`, `country`
    - `state_province`, `city`, `region`, `prefer_solo`

    **Note:** The system will automatically detect column names and map them appropriately.
    """)

    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with merged data (should have 'Merged Data' sheet)"
    )

    if uploaded_file is not None:
        try:
            # Read the Excel file
            try:
                data = pd.read_excel(uploaded_file, sheet_name='Merged Data')
            except Exception as e:
                st.error(f"Could not read 'Merged Data' sheet: {str(e)}")
                st.info("Please ensure your Excel file has a 'Merged Data' sheet.")
                return

            # Find column mapping
            column_mapping = find_column_mapping(data)

            # Check for essential columns using flexible mapping
            essential_fields = ['user_id', 'gender_identity', 'gender_preference']
            missing_essential = [field for field in essential_fields if not column_mapping.get(field)]

            if missing_essential:
                detected_cols = ', '.join(list(data.columns))
                st.error(f"Missing essential columns: {', '.join(missing_essential)}")
                st.info(f"Please ensure your Excel file contains columns for user_id, gender_identity, and gender_preference.\nDetected columns: {detected_cols}")
                st.info("The system accepts alternative column names such as 'genderPref', 'goSolo', etc. See documentation for details.")
                return

            # Store data in session state
            st.session_state.merged_data = data
            st.session_state.column_mapping = column_mapping
            data_source = "Merged Excel"

            # Show success message
            st.success("✅ Data uploaded successfully!")
            st.info(f"Loaded {len(data)} participants from {data_source}")

            # Show data preview
            st.subheader("📋 Data Preview")
            st.dataframe(data.head(), use_container_width=True)

            # Show column mapping
            st.subheader("🔍 Column Mapping")
            with st.expander("View detected column mappings"):
                for key, value in column_mapping.items():
                    if value:
                        st.write(f"**{key}:** {value}")
                    else:
                        st.write(f"**{key}:** ❌ Not found")

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please ensure the file is a valid Excel format with a 'Merged Data' sheet.")

    st.markdown("---")

    # User List Section
    st.header("📋 User List")

    st.markdown("""
    Generate a comprehensive Excel file with all user information. This includes participant details,
    formatted names, locations, coaches, and visual formatting based on various criteria.
    """)

    # Determine data source for display
    data_source = "Unknown"
    if 'participants_data' in st.session_state:
        data_source = "Uploaded Data"
    elif 'merged_data' in st.session_state:
        data_source = "Merged API Data"
    elif 'all_api_records' in st.session_state:
        data_source = "API Data"
    elif 'api_data' in st.session_state:
        data_source = "API Data"

    data = get_available_data()
    if data is not None:
        st.info(f"📊 Found {len(data)} participants from {data_source}")

        # Generate user list button
        if st.button("🚀 Generate User List Excel", type="primary", use_container_width=True):
            try:
                with st.spinner("Generating user list..."):
                    # Import the user list function
                    from user_list_to_excel import save_user_list_to_excel
                    from user_list_to_excel import find_column_mapping as find_column_mapping_user

                    # Convert data to list of dicts (same format as the Excel processing)
                    data_dicts = data.to_dict('records')

                    # Debug: Check for duplicates before processing
                    user_id_col = None
                    for col in data.columns:
                        if col.lower() in ['id_y', 'id', 'userid', 'user_id']:
                            user_id_col = col
                            break

                    if user_id_col:
                        user_ids = data[user_id_col].dropna().astype(str).str.strip()
                        duplicate_count = len(user_ids) - len(user_ids.unique())
                        if duplicate_count > 0:
                            st.warning(f"⚠️ Found {duplicate_count} duplicate user IDs in the data!")
                            # Show some examples of duplicates
                            duplicates = user_ids[user_ids.duplicated(keep=False)]
                            if len(duplicates) > 0:
                                st.info(f"Example duplicate IDs: {', '.join(duplicates.unique()[:5])}")
                        else:
                            st.info(f"✅ No duplicate user IDs found ({len(user_ids.unique())} unique users)")
                    else:
                        st.warning("⚠️ Could not find user ID column to check for duplicates")

                    # Find column mapping
                    column_mapping = find_column_mapping_user(data)

                    # Create BytesIO buffer for download
                    import io
                    buffer = io.BytesIO()

                    # Generate the Excel file
                    save_user_list_to_excel(data_dicts, buffer, column_mapping)

                    buffer.seek(0)

                    st.success("✅ User list generated successfully!")

                    # Download button
                    st.download_button(
                        label="📥 Download User List Excel",
                        data=buffer,
                        file_name="user_list.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"Error generating user list: {str(e)}")
                st.info("Please check your data format and try again.")
    else:
        st.warning("⚠️ No data available. Please upload data first using the 'Upload Data' section above or fetch from API.")

    st.markdown("---")

    # Create Groups Section
    st.header("👥 Create Groups")

    # Check for different data sources
    has_csv_data = 'participants_data' in st.session_state
    has_merged_data = 'merged_data' in st.session_state

    if not has_csv_data and not has_merged_data:
        st.warning("Please upload participant data first!")
        st.info("Go to 'Upload Data' or 'API Data' section above to get started.")
        return

    # Data source selection (only if both are available)
    if has_csv_data and has_merged_data:
        data_source = st.radio(
            "Choose data source:",
            ["Merged API Data", "Uploaded Data"],
            help="Select which dataset to use for group creation"
        )
    elif has_csv_data:
        data_source = "Uploaded Data"
    else:
        data_source = "Merged API Data"

    # Get the appropriate data
    if data_source == "Uploaded Data":
        data = st.session_state.participants_data
        data_format = "csv"
    else:
        data = st.session_state.merged_data
        data_format = "excel"

    # Display data info
    st.info(f"📊 Using {data_source}: {len(data)} participants")

    # Grouping parameters
    col1, col2 = st.columns(2)

    with col1:
        max_group_size = st.slider(
            "Maximum group size:",
            min_value=3,
            max_value=7,
            value=5,
            help="Maximum number of participants per group"
        )

    with col2:
        merge_small_groups = st.checkbox(
            "Merge small groups",
            value=True,
            help="Automatically merge groups with fewer than 4 members"
        )

    # Create groups button
    if st.button("🚀 Create Groups", type="primary", use_container_width=True):
        try:
            with st.spinner("Creating groups..."):
                # Import the grouping function
                from group_assignment_to_excel import group_participants, save_to_excel

                # Convert data to list of dicts
                data_dicts = data.to_dict('records')

                # Find column mapping if not already available
                if data_format == "excel" and 'column_mapping' in st.session_state:
                    column_mapping = st.session_state.column_mapping
                else:
                    from user_list_to_excel import find_column_mapping as find_column_mapping_user
                    column_mapping = find_column_mapping_user(data)

                # Group participants
                solo_groups, grouped, excluded_users, requested_groups, combined_group_info = group_participants(data_dicts, column_mapping)

                # Create BytesIO buffer for download
                import io
                buffer = io.BytesIO()

                # Save to Excel buffer
                save_to_excel(solo_groups, grouped, buffer, column_mapping, excluded_users, requested_groups, combined_group_info)

                buffer.seek(0)

                # Store results in session state
                st.session_state.grouping_results = {
                    'solo_groups': solo_groups,
                    'grouped': grouped,
                    'excluded_users': excluded_users,
                    'requested_groups': requested_groups
                }

                st.success("✅ Groups created successfully!")

                # Show summary
                total_groups = len(grouped) + len(solo_groups) + len(requested_groups)
                st.info(f"📊 Created {total_groups} groups: {len(grouped)} regular, {len(solo_groups)} solo, {len(requested_groups)} requested")

                # Download button
                st.download_button(
                    label="📥 Download Group Results Excel",
                    data=buffer,
                    file_name="grouped_participants.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Error creating groups: {str(e)}")
            st.info("Please check your data format and try again.")

def show_api_page():
    import io
    from datetime import datetime

    st.header("🔗 API Data")

    st.markdown("""
    ### Fetch Grouping Preferences from Lazy Lifter API
    This page allows you to fetch and view grouping preferences data from the Lazy Lifter portal API.
    """)

    # Access token (shared for all operations)
    access_token = st.text_input(
        "🔑 Access Token",
        value="joo9iL1wai8ii1koojaiy1ath3ooxahL7oaphoo1johPhaege8ieQuaGh0shiew0",
        type="password",
        help="Bearer token for API authentication"
    )

    # Comprehensive fetch and merge button (FIRST - AFTER TOKEN)
    st.subheader("🔄 Complete Data Fetch & Merge")

    st.markdown("""
    **One-click solution**: Fetch all users, then fetch grouping preferences for Season 9,
    merge the data, and download the complete merged Excel file.
    """)

    if st.button("🚀 Fetch & Merge All Data", type="primary", use_container_width=True):
        try:
            if not access_token or access_token.strip() == "":
                st.error("❌ Please enter a valid access token.")
                return

            with st.spinner("Step 1/4: Fetching all users..."):
                # Fetch all users
                users_url = "https://portal.thelazylifter.com/api/users"
                fetch_all_api_data(users_url, access_token, max_pages=500)
                users_data = st.session_state.get('all_api_records', [])

            with st.spinner("Step 2/4: Fetching grouping preferences..."):
                # Fetch grouping preferences for season 9
                grouping_url = "https://portal.thelazylifter.com/api/grouping_preferences?program=/api/programs/7"
                fetch_all_api_data(grouping_url, access_token, max_pages=500)
                grouping_data = st.session_state.get('all_api_records', [])

            with st.spinner("Step 3/4: Merging data..."):
                # Merge the data
                if users_data and grouping_data:
                    # Convert to DataFrames for merging
                    users_df = pd.DataFrame(users_data)
                    grouping_df = pd.DataFrame(grouping_data)

                    # Perform merge on user field
                    # First, check what fields are available for merging
                    if 'id' in users_df.columns and any(col in grouping_df.columns for col in ['user', 'user_id']):
                        # Find the user field in grouping data
                        user_field = None
                        for col in ['user', 'user_id', 'userid']:
                            if col in grouping_df.columns:
                                user_field = col
                                break

                        if user_field:
                            # Handle different user field formats
                            if user_field == 'user':
                                # User field might be a URL like /api/users/123, extract the ID
                                grouping_df['user_id'] = grouping_df['user'].astype(str).str.extract(r'/users/(\d+)').astype(float)
                            elif user_field == 'user_id':
                                grouping_df['user_id'] = grouping_df['user_id']

                            # Merge with grouping preferences as left table (preserves all grouping preference rows)
                            merged_df = pd.merge(grouping_df, users_df, left_on='user_id', right_on='id', how='left', suffixes=('_x', '_y'))

                            # Reorder columns to match the requested format
                            desired_columns = [
                                '@id_x', '@type_x', 'id_x', 'user', 'program', 'genderIdentity',
                                'kaizenClientType', 'createdAt_x', 'updatedAt', 'sex', 'residingInPhilippines',
                                'liftingExperience', 'groupGenderPreference', 'currentGoal', 'followUpLevel',
                                'accountabilityBuddies', 'province', 'city', 'goSolo', 'hasAccountabilityBuddies',
                                'retainPreviousCoach', 'joiningAsStudent', 'ageGroup', 'previousCoachName',
                                'country', 'locationIdentifier', 'internationalCity', 'internationalState',
                                '@id_y', '@type_y', 'id_y', 'email', 'name', 'createdAt_y',
                                'OnboardingTasksCompleted', 'firstName', 'lastName', 'nickname', 'guid',
                                'trackers', 'enrolledPrograms'
                            ]

                            # Keep only columns that exist in the merged dataframe
                            final_columns = [col for col in desired_columns if col in merged_df.columns]
                            merged_df = merged_df[final_columns]

                            # Store merged data
                            st.session_state.merged_data = merged_df
                            st.session_state.column_mapping = {}  # Will be set when needed

                            st.success(f"✅ Data merged successfully! Users: {len(users_df)}, Grouping: {len(grouping_df)}, Merged: {len(merged_df)}")

                        else:
                            st.error("❌ Could not find user field in grouping data for merging")
                            return
                    else:
                        st.error("❌ Required fields not found for merging (users.id or grouping.user)")
                        return
                else:
                    st.error("❌ Failed to fetch both users and grouping data")
                    return

            with st.spinner("Step 4/4: Creating merged Excel file..."):
                # Create Excel file with multiple sheets like the manual process
                import io
                from datetime import datetime

                # Store merged data in session state for group creation
                st.session_state.merged_data = merged_df

                # Normalize data types to prevent display issues (same as manual process)
                for df in [users_df, grouping_df, merged_df]:
                    for col in df.columns:
                        try:
                            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict, tuple)) or pd.isna(x) else x)
                            df[col] = df[col].astype(str)
                        except:
                            df[col] = "Data conversion error"

                # Clean accountabilityBuddies field (same as manual process)
                if 'accountabilityBuddies' in merged_df.columns:
                    if 'hasAccountabilityBuddies' in merged_df.columns:
                        merged_df['hasAccountabilityBuddies'] = merged_df['hasAccountabilityBuddies'].astype(str).str.lower()
                        mask = merged_df['hasAccountabilityBuddies'].isin(['false', '0', '0.0', 'no'])
                        merged_df.loc[mask, 'accountabilityBuddies'] = ''

                    def clean_accountability_buddies(value):
                        if pd.isna(value) or value == 'None' or value == 'nan':
                            return ''
                        if isinstance(value, str):
                            if value == '[None, None]' or value == '[None]' or value == "{'1': None}":
                                return ''
                            cleaned = value.strip('[]').replace('"', '').replace("'", '')
                            if cleaned == '' or cleaned == 'None':
                                return ''
                            emails = [email.strip() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
                            if not emails:
                                return ''
                            return value
                        return value

                    merged_df['accountabilityBuddies'] = merged_df['accountabilityBuddies'].apply(clean_accountability_buddies)

                # Create Excel file with multiple sheets (same as manual process)
                buffer = io.BytesIO()

                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    # Main merged data
                    merged_df.to_excel(writer, sheet_name='Merged Data', index=False)

                    # Individual datasets
                    users_df.to_excel(writer, sheet_name='Users Data', index=False)
                    grouping_df.to_excel(writer, sheet_name='Grouping Preferences', index=False)

                    # Summary sheet
                    summary_data = {
                        'Metric': ['Total Records', 'Users Data', 'Grouping Preferences', 'Merged Records'],
                        'Count': [len(merged_df), len(users_df), len(grouping_df), len(merged_df)]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)

                buffer.seek(0)

                st.success(f"✅ Successfully merged data! Result: {len(merged_df)} records")

                # Show merged data info (same as manual process)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Records", len(merged_df))
                with col2:
                    st.metric("Users Data", len(users_df))
                with col3:
                    st.metric("Grouping Preferences", len(grouping_df))

                # Download button (same as manual process)
                st.download_button(
                    label="📥 Download Merged Excel File",
                    data=buffer.getvalue(),
                    file_name=f"merged_users_grouping_preferences_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                # Show preview of merged data (same as manual process)
                st.subheader("📊 Merged Data Preview")
                st.dataframe(merged_df.head(10), use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error during fetch and merge: {str(e)}")
            import traceback
            st.error(f"Details: {traceback.format_exc()}")

    st.markdown("---")

    # API Configuration
    st.subheader("🔧 API Configuration")
    
    # Simple endpoint selection
    api_endpoint = st.selectbox(
        "Choose API Endpoint",
        [
            "Grouping Preferences",
            "Contexts Grouping Preference",
            "Users",
            "Custom URL"
        ],
        help="Select the API endpoint to fetch data from"
    )
    
    # Set API URL based on selection
    if api_endpoint == "Grouping Preferences":
        api_url = "https://portal.thelazylifter.com/api/grouping_preferences?program=/api/programs/7"
    elif api_endpoint == "Contexts Grouping Preference":
        api_url = "https://portal.thelazylifter.com/api/contexts/GroupingPreference"
    elif api_endpoint == "Users":
        api_url = "https://portal.thelazylifter.com/api/users"
    else:
        api_url = st.text_input(
            "Enter Custom API URL",
            value="https://portal.thelazylifter.com/api/grouping_preferences",
            help="Enter custom API endpoint URL"
        )

    # Fetch options
    st.subheader("📊 Fetch Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        page_number = st.number_input(
            "Page Number",
            min_value=1,
            value=1,
            help="Page number for pagination"
        )
        
        if st.button("🚀 Fetch Single Page", type="primary", use_container_width=True):
            fetch_api_data(api_url, access_token, page_number)
    
    with col2:
        if st.button("📚 Fetch All Pages", type="secondary", use_container_width=True):
            fetch_all_api_data(api_url, access_token, max_pages=20)
    
    # Test connection
    if st.button("🔍 Test API Connection", type="secondary", use_container_width=True):
        test_api_connection(api_url, access_token, page_number)


    if st.button("🚀 Fetch & Merge All Data", type="primary", use_container_width=True, key="duplicate_fetch_merge_button"):
        try:
            if not access_token or access_token.strip() == "":
                st.error("❌ Please enter a valid access token.")
                return

            with st.spinner("Step 1/4: Fetching all users..."):
                # Fetch all users
                users_url = "https://portal.thelazylifter.com/api/users"
                fetch_all_api_data(users_url, access_token, max_pages=500)
                users_data = st.session_state.get('all_api_records', [])

            with st.spinner("Step 2/4: Fetching grouping preferences..."):
                # Fetch grouping preferences for season 9
                grouping_url = "https://portal.thelazylifter.com/api/grouping_preferences?program=/api/programs/7"
                fetch_all_api_data(grouping_url, access_token, max_pages=500)
                grouping_data = st.session_state.get('all_api_records', [])

            with st.spinner("Step 3/4: Merging data..."):
                # Merge the data
                if users_data and grouping_data:
                    # Convert to DataFrames for merging
                    users_df = pd.DataFrame(users_data)
                    grouping_df = pd.DataFrame(grouping_data)

                    # Perform merge on user field
                    # First, check what fields are available for merging
                    if 'id' in users_df.columns and any(col in grouping_df.columns for col in ['user', 'user_id']):
                        # Find the user field in grouping data
                        user_field = None
                        for col in ['user', 'user_id', 'userid']:
                            if col in grouping_df.columns:
                                user_field = col
                                break

                        if user_field:
                            # Handle different user field formats
                            if user_field == 'user':
                                # User field might be a URL like /api/users/123, extract the ID
                                grouping_df['user_id'] = grouping_df['user'].astype(str).str.extract(r'/users/(\d+)').astype(float)
                            elif user_field == 'user_id':
                                grouping_df['user_id'] = grouping_df['user_id']

                            # Merge with grouping preferences as left table (preserves all grouping preference rows)
                            merged_df = pd.merge(grouping_df, users_df, left_on='user_id', right_on='id', how='left', suffixes=('_x', '_y'))

                            # Reorder columns to match the requested format
                            desired_columns = [
                                '@id_x', '@type_x', 'id_x', 'user', 'program', 'genderIdentity',
                                'kaizenClientType', 'createdAt_x', 'updatedAt', 'sex', 'residingInPhilippines',
                                'liftingExperience', 'groupGenderPreference', 'currentGoal', 'followUpLevel',
                                'accountabilityBuddies', 'province', 'city', 'goSolo', 'hasAccountabilityBuddies',
                                'retainPreviousCoach', 'joiningAsStudent', 'ageGroup', 'previousCoachName',
                                'country', 'locationIdentifier', 'internationalCity', 'internationalState',
                                '@id_y', '@type_y', 'id_y', 'email', 'name', 'createdAt_y',
                                'OnboardingTasksCompleted', 'firstName', 'lastName', 'nickname', 'guid',
                                'trackers', 'enrolledPrograms'
                            ]

                            # Keep only columns that exist in the merged dataframe
                            final_columns = [col for col in desired_columns if col in merged_df.columns]
                            merged_df = merged_df[final_columns]

                            # Store merged data
                            st.session_state.merged_data = merged_df
                            st.session_state.column_mapping = {}  # Will be set when needed

                            st.success(f"✅ Data merged successfully! Users: {len(users_df)}, Grouping: {len(grouping_df)}, Merged: {len(merged_df)}")

                        else:
                            st.error("❌ Could not find user field in grouping data for merging")
                            return
                    else:
                        st.error("❌ Required fields not found for merging (users.id or grouping.user)")
                        return
                else:
                    st.error("❌ Failed to fetch both users and grouping data")
                    return

            with st.spinner("Step 4/4: Creating merged Excel file..."):
                # Create Excel file with multiple sheets like the manual "Merge & Download Excel" process
                import io
                from datetime import datetime

                # Store merged data in session state for group creation
                st.session_state.merged_data = merged_df

                # Normalize data types to prevent display issues (same as manual process)
                for df in [users_df, grouping_df, merged_df]:
                    for col in df.columns:
                        try:
                            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict, tuple)) or pd.isna(x) else x)
                            df[col] = df[col].astype(str)
                        except:
                            df[col] = "Data conversion error"

                # Clean accountabilityBuddies field (same as manual process)
                if 'accountabilityBuddies' in merged_df.columns:
                    if 'hasAccountabilityBuddies' in merged_df.columns:
                        merged_df['hasAccountabilityBuddies'] = merged_df['hasAccountabilityBuddies'].astype(str).str.lower()
                        mask = merged_df['hasAccountabilityBuddies'].isin(['false', '0', '0.0', 'no'])
                        merged_df.loc[mask, 'accountabilityBuddies'] = ''

                    def clean_accountability_buddies(value):
                        if pd.isna(value) or value == 'None' or value == 'nan':
                            return ''
                        if isinstance(value, str):
                            if value == '[None, None]' or value == '[None]' or value == "{'1': None}":
                                return ''
                            cleaned = value.strip('[]').replace('"', '').replace("'", '')
                            if cleaned == '' or cleaned == 'None':
                                return ''
                            emails = [email.strip() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
                            if not emails:
                                return ''
                            return value
                        return value

                    merged_df['accountabilityBuddies'] = merged_df['accountabilityBuddies'].apply(clean_accountability_buddies)

                # Create Excel file with multiple sheets (same as manual process)
                buffer = io.BytesIO()

                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    # Main merged data
                    merged_df.to_excel(writer, sheet_name='Merged Data', index=False)

                    # Individual datasets
                    users_df.to_excel(writer, sheet_name='Users Data', index=False)
                    grouping_df.to_excel(writer, sheet_name='Grouping Preferences', index=False)

                    # Summary sheet
                    summary_data = {
                        'Metric': ['Total Records', 'Users Data', 'Grouping Preferences', 'Merged Records'],
                        'Count': [len(merged_df), len(users_df), len(grouping_df), len(merged_df)]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)

                buffer.seek(0)

                st.success(f"✅ Successfully merged data! Result: {len(merged_df)} records")

                # Show merged data info (same as manual process)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Records", len(merged_df))
                with col2:
                    st.metric("Users Data", len(users_df))
                with col3:
                    st.metric("Grouping Preferences", len(grouping_df))

                # Download button (same as manual process)
                st.download_button(
                    label="📥 Download Merged Excel File",
                    data=buffer.getvalue(),
                    file_name=f"merged_users_grouping_preferences_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                # Show preview of merged data (same as manual process)
                st.subheader("📊 Merged Data Preview")
                st.dataframe(merged_df.head(10), use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error during fetch and merge: {str(e)}")
            import traceback
            st.error(f"Details: {traceback.format_exc()}")

    # Merge data section
    st.subheader("🔗 Merge Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👥 Fetch All Users", type="primary", use_container_width=True):
            fetch_all_api_data("https://portal.thelazylifter.com/api/users", access_token, max_pages=500)
            st.session_state.users_data = st.session_state.all_api_records
            st.success("✅ Users data fetched and stored!")
    
    with col2:
        if st.button("📋 Fetch All Grouping Preferences for Season 9", type="primary", use_container_width=True):
            # Fetch only essential grouping preference data for Season 9
            # Necessary data includes: user_id, gender_preference, and other grouping-related fields
            # Using pagination to manage response size efficiently
            fetch_all_api_data("https://portal.thelazylifter.com/api/grouping_preferences?program=/api/programs/7", access_token, max_pages=500)

            # Filter to only include records with necessary data for grouping
            if 'all_api_records' in st.session_state:
                raw_data = st.session_state.all_api_records
                essential_fields = ['id', 'user', 'groupGenderPreference', 'genderPreference']

                # Keep only records that have at least one essential field
                filtered_data = []
                for record in raw_data:
                    if isinstance(record, dict):
                        has_essential_data = any(
                            key in record and record[key] is not None and str(record[key]).strip() != ''
                            for key in essential_fields
                        )
                        if has_essential_data:
                            filtered_data.append(record)

                st.session_state.grouping_data = filtered_data
                st.info(f"📊 Filtered to {len(filtered_data)} records with essential grouping data (from {len(raw_data)} total)")
            else:
                st.session_state.grouping_data = st.session_state.all_api_records

            st.success("✅ Essential grouping preferences data fetched and stored!")
    
    # Merge and download
    if st.button("🔗 Merge & Download Excel", type="secondary", use_container_width=True):
        merge_and_download_excel(access_token)
    
    # Display cached data if available
    if 'api_data' in st.session_state or 'all_api_records' in st.session_state:
        st.subheader("📋 API Data Table")
        
        # Get records from either single page or all pages
        if 'all_api_records' in st.session_state:
            records = st.session_state.all_api_records
            data_source = "All Pages"
        else:
            data = st.session_state.api_data
            # Handle different possible response formats
            records = []
            if isinstance(data, dict):
                if 'data' in data:
                    records = data['data']
                elif 'hydra:member' in data:
                    records = data['hydra:member']
                    # Show Hydra pagination info if available
                    if 'hydra:view' in data:
                        hydra_view = data['hydra:view']
                        st.info("📄 Hydra Pagination Info:")
                        st.json(hydra_view)
                elif 'results' in data:
                    records = data['results']
                elif 'items' in data:
                    records = data['items']
                else:
                    records = [data]
            elif isinstance(data, list):
                records = data
            else:
                st.error(f"Unexpected data type: {type(data)}")
                return
            data_source = f"Page {page_number}"
        
        if records:
            # Determine the endpoint name for display
            endpoint_name = "Unknown"
            if 'api_data' in st.session_state:
                # Try to determine endpoint from the data or use the current URL
                if hasattr(st, 'session_state') and 'current_api_url' in st.session_state:
                    current_url = st.session_state.current_api_url
                    if 'users' in current_url:
                        endpoint_name = "Users API"
                    elif 'grouping_preferences' in current_url:
                        endpoint_name = "Grouping Preferences API"
                    elif 'contexts/GroupingPreference' in current_url:
                        endpoint_name = "Contexts Grouping Preference API"
                    else:
                        endpoint_name = "Custom API"
            
            st.success(f"📊 Found {len(records)} records from {data_source} ({endpoint_name})")
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(records)
            
            # Normalize data types to prevent PyArrow conversion issues
            for col in df.columns:
                try:
                    # Convert complex data types to strings for display
                    df[col] = df[col].apply(lambda x: 
                        str(x) if isinstance(x, (list, dict, tuple)) or pd.isna(x) else x
                    )
                    
                    # Ensure all values are strings to avoid PyArrow issues
                    df[col] = df[col].astype(str)
                    
                except Exception as e:
                    # If any error occurs, convert the entire column to string
                    try:
                        df[col] = df[col].astype(str)
                    except:
                        # Last resort: replace with placeholder
                        df[col] = "Data conversion error"
            
            # Show data summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Data Source", data_source)
            
            # Show column information in expander
            with st.expander("📋 Column Information"):
                col_info = []
                for col in df.columns:
                    try:
                        # Try to get unique values count
                        unique_count = df[col].nunique()
                    except (TypeError, ValueError):
                        # If column contains unhashable types (like lists), use a different approach
                        try:
                            unique_count = len(df[col].dropna().astype(str).unique())
                        except:
                            unique_count = "N/A"
                    
                    col_info.append({
                        'Column': col,
                        'Type': str(df[col].dtype),
                        'Non-Null Count': df[col].count(),
                        'Null Count': df[col].isnull().sum(),
                        'Unique Values': unique_count
                    })
                
                col_df = pd.DataFrame(col_info)
                st.dataframe(col_df, use_container_width=True)
            
            # Display the main data table with search
            st.subheader("📊 Data Table")
            
            # Add search functionality
            search_term = st.text_input("🔍 Search in all columns:", placeholder="Enter search term...")
            
            if search_term:
                # Search in all columns with error handling for unhashable types
                search_masks = []
                for col in df.columns:
                    try:
                        # Convert to string and search
                        col_mask = df[col].astype(str).str.contains(search_term, case=False, na=False)
                        search_masks.append(col_mask)
                    except (TypeError, AttributeError):
                        # For columns with unhashable types, try a different approach
                        try:
                            col_mask = df[col].apply(lambda x: search_term.lower() in str(x).lower() if pd.notna(x) else False)
                            search_masks.append(col_mask)
                        except:
                            # If all else fails, create a mask of False values
                            col_mask = pd.Series([False] * len(df), index=df.index)
                            search_masks.append(col_mask)
                
                # Combine all masks
                if search_masks:
                    combined_mask = pd.concat(search_masks, axis=1).any(axis=1)
                    filtered_df = df[combined_mask]
                    st.info(f"Found {len(filtered_df)} records matching '{search_term}'")
                else:
                    filtered_df = df
            else:
                filtered_df = df
            
            # Show the data table with error handling
            try:
                st.dataframe(filtered_df, use_container_width=True, height=400)
            except Exception as e:
                st.error(f"Error displaying dataframe: {str(e)}")
                st.info("Attempting to display as text table...")
                
                # Fallback: display as a simple text table
                st.write("**Data Preview (first 10 rows):**")
                for i, row in filtered_df.head(10).iterrows():
                    st.write(f"**Row {i+1}:**")
                    for col, value in row.items():
                        st.write(f"  {col}: {value}")
                    st.write("---")
                
                if len(filtered_df) > 10:
                    st.info(f"... and {len(filtered_df) - 10} more rows")
            
            # Download options
            st.subheader("📥 Download Data")
            col1, col2 = st.columns(2)
            
            with col1:
                # Download filtered data as CSV
                csv_buffer = io.StringIO()
                filtered_df.to_csv(csv_buffer, index=False)
                
                st.download_button(
                    label="📥 Download Filtered CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"api_data_{data_source.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Download all data as CSV
                csv_buffer_all = io.StringIO()
                df.to_csv(csv_buffer_all, index=False)
                
                st.download_button(
                    label="📥 Download All Data CSV",
                    data=csv_buffer_all.getvalue(),
                    file_name=f"all_api_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Show sample data for debugging
            with st.expander("🔍 Debug: Raw API Response Structure"):
                if 'api_data' in st.session_state:
                    st.json(st.session_state.api_data)
                else:
                    st.write("No raw API data available (using processed records)")
        else:
            st.warning("No records found in the API response")

def test_api_connection(api_url, access_token, page_number):
    """Test the API connection"""
    try:
        url = f"{api_url}?page={page_number}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        with st.spinner("Testing API connection..."):
            response = requests.get(url, headers=headers, timeout=10)
            
        if response.status_code == 200:
            st.success("✅ API connection successful!")
            st.info(f"Status Code: {response.status_code}")
        else:
            st.error(f"❌ API connection failed!")
            st.error(f"Status Code: {response.status_code}")
            st.error(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")

def fetch_api_data(api_url, access_token, page_number):
    """Fetch data from the API"""
    try:
        url = f"{api_url}?page={page_number}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        # Store the current API URL for display purposes
        st.session_state.current_api_url = api_url
        
        with st.spinner("Fetching data from API..."):
            response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Extract records from Hydra format if present
                if isinstance(data, dict) and 'hydra:member' in data:
                    records = data['hydra:member']
                    # Add pagination info if available
                    if 'hydra:view' in data:
                        hydra_view = data['hydra:view']
                        if 'hydra:last' in hydra_view:
                            last_url = hydra_view['hydra:last']
                            try:
                                import re
                                match = re.search(r'page=(\d+)', last_url)
                                if match:
                                    total_pages = int(match.group(1))
                                    st.info(f"Total pages available: {total_pages}")
                            except:
                                pass
                    
                    # Store the records in a format consistent with other data
                    st.session_state.api_data = {'data': records}
                    st.success(f"✅ Data fetched successfully! Found {len(records)} records")
                else:
                    st.session_state.api_data = data
                    st.success("✅ Data fetched successfully!")
                
                st.info(f"Retrieved data for page {page_number}")
                
                # Show response structure for debugging
                st.write("**Response Structure:**")
                st.json(data)
                
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON response: {str(e)}")
                st.error(f"Raw response: {response.text[:500]}...")
        else:
            st.error(f"❌ API request failed!")
            st.error(f"Status Code: {response.status_code}")
            st.error(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")

def fetch_all_api_data(api_url, access_token, max_pages=50, items_per_page=30):
    """Fetch all pages of data from the API using Hydra format"""
    try:
        all_records = []
        page = 1
        total_pages = 0
        total_items = 0
        consecutive_empty_pages = 0
        current_url = api_url  # Start with the initial URL

        # Store the current API URL for display purposes
        st.session_state.current_api_url = api_url

        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        with st.spinner("Fetching all pages..."):
            while current_url and page <= max_pages:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }

                # Show the URL being used for this page
                st.write(f"🔗 Page {page} URL: {current_url}")
                status_text.text(f"Fetching page {page}...")

                response = requests.get(current_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Extract records based on Hydra format
                        records = []
                        if isinstance(data, dict):
                            # Check for Hydra format first
                            if 'hydra:member' in data:
                                records = data['hydra:member']

                                # Priority: Get pagination info from hydra:view first
                                if 'hydra:view' in data:
                                    hydra_view = data['hydra:view']
                                    if 'hydra:last' in hydra_view:
                                        # Extract page number from hydra:last URL
                                        last_url = hydra_view['hydra:last']
                                        try:
                                            # Extract page number from URL like "?page=5"
                                            import re
                                            match = re.search(r'page=(\d+)', last_url)
                                            if match:
                                                total_pages = int(match.group(1))
                                                # Silently set total_pages without showing message
                                            else:
                                                st.warning("⚠️ Could not extract page count from API")
                                        except Exception as e:
                                            pass  # Silently handle extraction errors

                                # Fallback: Get total items count from hydra:totalItems if view didn't work
                                if total_pages == 0 and 'hydra:totalItems' in data:
                                    total_items = int(data['hydra:totalItems'])
                                    # Calculate total pages based on items per page
                                    total_pages = (total_items + items_per_page - 1) // items_per_page  # Ceiling division
                                    if total_pages <= max_pages:
                                        st.info(f"📊 Estimated {total_pages} pages from {total_items} items")
                            elif 'data' in data:
                                records = data['data']
                                # Check if there's pagination info
                                if 'meta' in data and 'last_page' in data['meta']:
                                    total_pages = data['meta']['last_page']
                                elif 'pagination' in data and 'last_page' in data['pagination']:
                                    total_pages = data['pagination']['last_page']
                            elif 'results' in data:
                                records = data['results']
                            elif 'items' in data:
                                records = data['items']
                            else:
                                records = [data]
                        elif isinstance(data, list):
                            records = data
                        
                        if records:
                            all_records.extend(records)
                            consecutive_empty_pages = 0  # Reset counter when we find records
                            # Only show success messages every 5 pages or for significant events
                            if page % 5 == 1 or page == 1:
                                st.success(f"📄 Page {page}: {len(records)} records")
                        else:
                            consecutive_empty_pages += 1
                            if consecutive_empty_pages == 1:
                                st.warning(f"⚠️ Page {page}: No records found")

                            # If we get 2 consecutive empty pages, assume we've reached the end
                            if consecutive_empty_pages >= 2:
                                break
                        
                        # Update progress
                        if total_pages > 0:
                            progress = min(page / total_pages, 1.0)
                            progress_bar.progress(progress)
                            if total_items > 0:
                                status_text.text(f"Fetching page {page}/{total_pages} ({len(all_records)}/{total_items} records)")
                            else:
                                status_text.text(f"Fetching page {page}/{total_pages}")
                        else:
                            status_text.text(f"Fetching page {page}...")

                        # Check for next page URL in hydra:view
                        next_url = None
                        if isinstance(data, dict) and 'hydra:view' in data:
                            hydra_view = data['hydra:view']
                            if 'hydra:next' in hydra_view:
                                next_url = hydra_view['hydra:next']

                                # Handle relative URLs by making them absolute
                                if next_url and not next_url.startswith(('http://', 'https://')):
                                    # If it's a relative URL, prepend the confirmed base URL
                                    from urllib.parse import urljoin
                                    base_url = "https://portal.thelazylifter.com/"
                                    next_url = urljoin(base_url, next_url.lstrip('/'))
                                    # Silently fix the URL without showing a message

                        # Update current URL for next iteration
                        if next_url:
                            current_url = next_url
                        else:
                            current_url = None  # No more pages

                        page += 1

                        # If we know total pages from hydra:last, stop exactly at that page
                        if total_pages > 0 and page > total_pages:
                            break

                        # If no next URL, we've reached the end
                        if not current_url:
                            st.info("✅ Reached the last page (no more hydra:next URL)")
                            break

                        # Intelligent end detection: if we've fetched many pages with very few records, stop
                        # This indicates we've reached the actual end of data, even if hydra:last suggests more pages
                        if page > 5 and len(records) < 5 and consecutive_empty_pages == 0:
                            actual_pages = page - 1  # The last page that had records
                            if total_pages > actual_pages and total_pages > 10:  # Only adjust if significant discrepancy
                                st.warning(f"⚠️ Data ends earlier than expected (page {actual_pages} vs {total_pages})")
                                total_pages = actual_pages  # Update to reflect reality
                                # Update progress bar to reflect corrected total
                                progress = min(page / total_pages, 1.0)
                                progress_bar.progress(progress)
                            break

                        # Safety check: if we've fetched many pages with very few records, stop
                        # This prevents infinite loops when API returns empty pages
                        if page > 5 and len(records) < 5:
                            st.info(f"⚠️ Stopping at page {page} due to low record count ({len(records)} records)")
                            break
                            
                    except json.JSONDecodeError as e:
                        st.error(f"❌ Invalid JSON response on page {page}: {str(e)}")
                        break
                else:
                    st.error(f"❌ API request failed on page {page}!")
                    st.error(f"Status Code: {response.status_code}")
                    break
        
        # Store all records
        st.session_state.api_data = {'data': all_records}
        st.session_state.all_api_records = all_records
        
        progress_bar.empty()
        status_text.empty()

        if total_items > 0:
            st.success(f"✅ Successfully fetched {len(all_records)}/{total_items} records from {page-1} pages!")
        else:
            st.success(f"✅ Successfully fetched {len(all_records)} total records from {page-1} pages!")
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")

def merge_and_download_excel(access_token):
    """Merge users and grouping preferences data and download as Excel"""
    try:
        # Check if both datasets are available
        if 'users_data' not in st.session_state:
            st.error("❌ Users data not found. Please fetch users data first.")
            return
        
        if 'grouping_data' not in st.session_state:
            st.error("❌ Grouping preferences data not found. Please fetch grouping preferences data first.")
            return
        
        users_data = st.session_state.users_data
        grouping_data = st.session_state.grouping_data
        
        st.info(f"📊 Merging {len(users_data)} users with {len(grouping_data)} grouping preferences...")
        
        # Convert to DataFrames
        users_df = pd.DataFrame(users_data)
        grouping_df = pd.DataFrame(grouping_data)
        
        # Normalize data types to prevent display issues
        for df in [users_df, grouping_df]:
            for col in df.columns:
                try:
                    df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict, tuple)) or pd.isna(x) else x)
                    df[col] = df[col].astype(str)
                except:
                    df[col] = "Data conversion error"
        
        # Find the user ID field in grouping preferences
        user_id_field = None
        for col in grouping_df.columns:
            if 'user' in col.lower() and ('id' in col.lower() or 'user' in col.lower()):
                user_id_field = col
                break
        
        if user_id_field is None:
            st.error("❌ Could not find user ID field in grouping preferences data.")
            st.write("Available columns in grouping preferences:")
            st.write(list(grouping_df.columns))
            return
        
        # Find the user ID field in users data
        users_id_field = None
        for col in users_df.columns:
            if 'id' in col.lower() and 'user' not in col.lower():
                users_id_field = col
                break
        
        if users_id_field is None:
            st.error("❌ Could not find ID field in users data.")
            st.write("Available columns in users data:")
            st.write(list(users_df.columns))
            return
        
        # Merge the data with grouping preferences as left table (preserves all grouping preference rows)
        merged_df = pd.merge(
            grouping_df,
            users_df,
            left_on=user_id_field,
            right_on=users_id_field,
            how='left',
            suffixes=('_x', '_y')
        )

        # Reorder columns to match the requested format
        desired_columns = [
            '@id_x', '@type_x', 'id_x', 'user', 'program', 'genderIdentity',
            'kaizenClientType', 'createdAt_x', 'updatedAt', 'sex', 'residingInPhilippines',
            'liftingExperience', 'groupGenderPreference', 'currentGoal', 'followUpLevel',
            'accountabilityBuddies', 'province', 'city', 'goSolo', 'hasAccountabilityBuddies',
            'retainPreviousCoach', 'joiningAsStudent', 'ageGroup', 'previousCoachName',
            'country', 'locationIdentifier', 'internationalCity', 'internationalState',
            '@id_y', '@type_y', 'id_y', 'email', 'name', 'createdAt_y',
            'OnboardingTasksCompleted', 'firstName', 'lastName', 'nickname', 'guid',
            'trackers', 'enrolledPrograms'
        ]

        # Keep only columns that exist in the merged dataframe
        final_columns = [col for col in desired_columns if col in merged_df.columns]
        merged_df = merged_df[final_columns]
        
        st.success(f"✅ Successfully merged data! Result: {len(merged_df)} records")
        
        # Clean accountabilityBuddies field - replace None with blank string if no emails
        if 'accountabilityBuddies' in merged_df.columns:
            # First, check if hasAccountabilityBuddies is False and make accountabilityBuddies blank
            if 'hasAccountabilityBuddies' in merged_df.columns:
                # Convert hasAccountabilityBuddies to boolean and make accountabilityBuddies blank if False
                merged_df['hasAccountabilityBuddies'] = merged_df['hasAccountabilityBuddies'].astype(str).str.lower()
                mask = merged_df['hasAccountabilityBuddies'].isin(['false', '0', '0.0', 'no'])
                merged_df.loc[mask, 'accountabilityBuddies'] = ''
                st.info(f"🧹 Set accountabilityBuddies to blank for {mask.sum()} records where hasAccountabilityBuddies=False")
            
            def clean_accountability_buddies(value):
                if pd.isna(value) or value == 'None' or value == 'nan':
                    return ''
                
                # If it's a string representation of a list/array, check if it contains emails
                if isinstance(value, str):
                    # Handle cases like [None, None], [None], {'1': None}
                    if value == '[None, None]' or value == '[None]' or value == "{'1': None}":
                        return ''
                    
                    # Remove brackets and quotes, split by comma
                    cleaned = value.strip('[]').replace('"', '').replace("'", '')
                    if cleaned == '' or cleaned == 'None':
                        return ''
                    
                    # Check if it contains email-like strings (contains @ symbol)
                    emails = [email.strip() for email in cleaned.split(',') if email.strip() and '@' in email.strip()]
                    if not emails:
                        return ''
                    return value  # Keep original if it contains emails
                return value
            
            merged_df['accountabilityBuddies'] = merged_df['accountabilityBuddies'].apply(clean_accountability_buddies)
            st.info("🧹 Cleaned accountabilityBuddies field: replaced None/empty values with blank strings")
        
        # Show merged data info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(merged_df))
        with col2:
            st.metric("Users Data", len(users_df))
        with col3:
            st.metric("Grouping Preferences", len(grouping_df))
        
        # Create Excel file with multiple sheets
        output_buffer = io.BytesIO()
        
        with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
            # Main merged data
            merged_df.to_excel(writer, sheet_name='Merged Data', index=False)
            
            # Individual datasets
            users_df.to_excel(writer, sheet_name='Users Data', index=False)
            grouping_df.to_excel(writer, sheet_name='Grouping Preferences', index=False)
            
            # Summary sheet
            summary_data = {
                'Metric': ['Total Records', 'Users Data', 'Grouping Preferences', 'Merged Records'],
                'Count': [len(merged_df), len(users_df), len(grouping_df), len(merged_df)]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        output_buffer.seek(0)
        
        # Download button
        st.download_button(
            label="📥 Download Merged Excel File",
            data=output_buffer.getvalue(),
            file_name=f"merged_users_grouping_preferences_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        # Store merged data in session state for group creation
        st.session_state.merged_data = merged_df
        
        # Show preview of merged data
        st.subheader("📊 Merged Data Preview")
        st.dataframe(merged_df.head(10), use_container_width=True)
        
        # Show column mapping info
        with st.expander("🔍 Data Mapping Information"):
            st.write(f"**User ID Field in Grouping Preferences:** {user_id_field}")
            st.write(f"**ID Field in Users Data:** {users_id_field}")
            st.write(f"**Merge Type:** Left join (all grouping preferences with matching users)")
            st.write(f"**Total Columns:** {len(merged_df.columns)}")
            st.write("**Columns:**")
            for i, col in enumerate(merged_df.columns, 1):
                st.write(f"{i}. {col}")
        
        # Show next steps
        st.success("✅ Merged data is now available for group creation!")
        st.info("💡 Go to the 'Create Groups' page to use this merged data for group assignment.")
        
    except Exception as e:
        st.error(f"❌ Error merging data: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")

def show_settings_page():
    st.header("⚙️ Settings")
    
    st.subheader("🔧 System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Default Group Size:**")
        default_group_size = st.slider("Group Size", min_value=2, max_value=10, value=5)
        
        st.write("**Export Format:**")
        default_export = st.selectbox("Default Export", ["Excel", "CSV"])
    
    with col2:
        st.write("**Grouping Preferences:**")
        respect_gender = st.checkbox("Respect Gender Preferences", value=True)
        geographic_grouping = st.checkbox("Geographic Grouping", value=True)
        
        st.write("**Display Options:**")
        show_preview = st.checkbox("Show Data Preview", value=True)
        color_coding = st.checkbox("Enable Color Coding", value=True)
    
    # Save settings
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")
    
    st.markdown("---")
    
    st.subheader("📋 System Information")
    st.write(f"**Pandas Version:** {pd.__version__}")
    st.write(f"**Streamlit Version:** {st.__version__}")
    
    # Clear data button
    if st.button("🗑️ Clear All Data", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("All data cleared!")

if __name__ == "__main__":
    main() 