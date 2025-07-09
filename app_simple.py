import streamlit as st
import pandas as pd
from collections import defaultdict
import io
from datetime import datetime
import os

# Import the grouping logic from the existing script
from group_assignment_to_excel import group_participants, save_to_excel

def create_download_buttons(solo_groups, grouped):
    """Create download buttons for Excel and CSV files"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Create Excel file
        output_buffer = io.BytesIO()
        save_to_excel(solo_groups, grouped, output_buffer)
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
        for i, group in enumerate(solo_groups, 1):
            participant = group[0]
            csv_data.append({
                'Group': f'Solo {i}',
                'User ID': participant[0],
                'Name': participant[1],
                'Gender': participant[3],
                'City': participant[18] if len(participant) > 18 else '',
                'Type': 'Solo'
            })
        
        for group_name, members in grouped.items():
            for member in members:
                csv_data.append({
                    'Group': group_name,
                    'User ID': member[0],
                    'Name': member[1],
                    'Gender': member[3],
                    'City': member[18] if len(member) > 18 else '',
                    'Type': 'Group'
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
            ["📊 Dashboard", "📁 Upload Data", "👥 Create Groups", "📈 Analysis", "⚙️ Settings"]
        )
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        if 'participants_data' in st.session_state:
            data = st.session_state.participants_data
            st.metric("Total Participants", len(data))
            st.metric("Solo Participants", len(data[data['go_solo'] == 1]))
            st.metric("Group Participants", len(data[data['go_solo'] == 0]))
        else:
            st.info("Upload data to see statistics")
    
    # Page routing
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📁 Upload Data":
        show_upload_page()
    elif page == "👥 Create Groups":
        show_grouping_page()
    elif page == "📈 Analysis":
        show_analysis_page()
    elif page == "⚙️ Settings":
        show_settings_page()

def show_dashboard():
    st.header("📊 Dashboard")
    
    if 'participants_data' not in st.session_state:
        st.warning("Please upload participant data first!")
        st.info("Go to 'Upload Data' page to get started.")
        return
    
    data = st.session_state.participants_data
    
    # Show download options if groups exist
    if 'solo_groups' in st.session_state and 'grouped' in st.session_state:
        st.subheader("📤 Download Results")
        st.info("Groups have been created! You can download the results here.")
        create_download_buttons(st.session_state.solo_groups, st.session_state.grouped)
        st.markdown("---")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Participants", len(data))
    
    with col2:
        solo_count = len(data[data['go_solo'] == 1])
        st.metric("Solo Participants", solo_count)
    
    with col3:
        group_count = len(data[data['go_solo'] == 0])
        st.metric("Group Participants", group_count)
    
    with col4:
        ph_count = len(data[data['residing_in_philippines'] == 1])
        st.metric("Philippines Residents", ph_count)
    
    # Data overview
    st.subheader("📋 Data Overview")
    st.dataframe(data.head(10), use_container_width=True)
    
    # Simple statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Gender Distribution")
        gender_counts = data['gender_identity'].value_counts()
        for gender, count in gender_counts.items():
            st.write(f"**{gender}:** {count} participants")
    
    with col2:
        st.subheader("🌍 Geographic Distribution")
        country_counts = data['country'].value_counts().head(10)
        for country, count in country_counts.items():
            st.write(f"**{country}:** {count} participants")

def show_upload_page():
    st.header("📁 Upload Participant Data")
    
    st.markdown("""
    ### Upload your participant data file
    The system supports CSV files with the following required columns:
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
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file with participant data"
    )
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            data = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = [
                'user_id', 'gender_identity', 'sex', 'residing_in_philippines',
                'group_gender_preference', 'country', 'province', 'city', 'state', 'go_solo'
            ]
            
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                st.info("Please ensure your CSV file contains all required columns.")
            else:
                # Store data in session state
                st.session_state.participants_data = data
                
                st.success("✅ Data uploaded successfully!")
                st.info(f"Loaded {len(data)} participants")
                
                # Show data preview
                st.subheader("📋 Data Preview")
                st.dataframe(data.head(), use_container_width=True)
                
                # Show data statistics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Data Statistics")
                    st.write(f"**Total Participants:** {len(data)}")
                    st.write(f"**Solo Participants:** {len(data[data['go_solo'] == 1])}")
                    st.write(f"**Group Participants:** {len(data[data['go_solo'] == 0])}")
                    st.write(f"**Philippines Residents:** {len(data[data['residing_in_philippines'] == 1])}")
                
                with col2:
                    st.subheader("🎯 Gender Preferences")
                    gender_pref_counts = data['group_gender_preference'].value_counts()
                    for pref, count in gender_pref_counts.items():
                        st.write(f"**{pref}:** {count}")
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please ensure the file is a valid CSV format.")

def show_grouping_page():
    st.header("👥 Create Groups")
    
    if 'participants_data' not in st.session_state:
        st.warning("Please upload participant data first!")
        st.info("Go to 'Upload Data' page to get started.")
        return
    
    data = st.session_state.participants_data
    
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
                # Convert DataFrame to list format expected by the grouping function
                data_list = data.values.tolist()
                
                # Call the grouping function
                solo_groups, grouped = group_participants(data_list)
                
                # Store results in session state
                st.session_state.solo_groups = solo_groups
                st.session_state.grouped = grouped
                
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
                
                # Solo groups
                if solo_groups:
                    st.write("**Solo Participants:**")
                    for i, group in enumerate(solo_groups[:5], 1):  # Show first 5
                        participant = group[0]
                        st.write(f"  {i}. User {participant[0]} - {participant[1]} ({participant[3]})")
                
                # Regular groups
                if grouped:
                    st.write("**Regular Groups:**")
                    for i, (group_name, members) in enumerate(list(grouped.items())[:5], 1):  # Show first 5
                        st.write(f"  {i}. {group_name} ({len(members)} members)")
                        for member in members[:3]:  # Show first 3 members
                            st.write(f"     - User {member[0]} - {member[1]}")
                        if len(members) > 3:
                            st.write(f"     ... and {len(members) - 3} more")
                
                # Export options
                st.subheader("📤 Export Results")
                
                # Store results in session state for download
                st.session_state.solo_groups = solo_groups
                st.session_state.grouped = grouped
                
                create_download_buttons(solo_groups, grouped)
            
            except Exception as e:
                st.error(f"Error creating groups: {str(e)}")
                st.info("Please check your data format and try again.")

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
            st.write("**Top 10 Countries:**")
            country_counts = data['country'].value_counts().head(10)
            for country, count in country_counts.items():
                st.write(f"- {country}: {count} participants")
        
        with col2:
            st.write("**Philippines vs International:**")
            ph_count = len(data[data['residing_in_philippines'] == 1])
            int_count = len(data[data['residing_in_philippines'] == 0])
            st.write(f"- Philippines: {ph_count} participants")
            st.write(f"- International: {int_count} participants")
    
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