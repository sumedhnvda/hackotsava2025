import streamlit as st
import pandas as pd

# Set the page configuration for a wider, more modern layout
st.set_page_config(layout="wide")

st.title("🎓 Team Leader Registrations Dashboard")
st.write("Use the filters below to search, add, or delete entries.")

# --- Helper Functions for File Operations ---

# @st.cache_data # We remove caching because the data needs to be mutable
def load_data(file_path):
    """Loads and cleans data from the specified Excel file."""
    try:
        df = pd.read_excel(file_path)
        
        # --- Data Cleaning Step for Mobile Numbers ---
        mobile_col = "Candidate's Mobile"
        if mobile_col in df.columns:
            # Ensure the column is treated as a string, handling potential missing values (NaN) and whitespace
            df[mobile_col] = df[mobile_col].astype(str).str.strip().fillna('')
            
            # Create a boolean mask for numbers that start with '91' and are long enough
            mask = df[mobile_col].str.startswith('91') & (df[mobile_col].str.len() > 10)
            
            # Use the mask to apply the slicing operation, removing '91' only where appropriate
            df.loc[mask, mobile_col] = df.loc[mask, mobile_col].str[2:]
            
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please make sure it is in the same directory as the script.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the Excel file: {e}")
        return None

def save_to_excel(file_path):
    """Saves the current session state dataframe back to the Excel file."""
    try:
        st.session_state.df.to_excel(file_path, index=False)
        return True
    except PermissionError:
        st.error(f"Error: Could not save changes to `{file_path}`. Please make sure the file is not open in Excel or another program.")
        return False
    except Exception as e:
        st.error(f"An error occurred while saving: {e}")
        return False

# --- Main App Logic ---
input_file = 'team_leaders.xlsx'

# Load data into session state to make it editable
if 'df' not in st.session_state:
    st.session_state.df = load_data(input_file)

if st.session_state.df is None:
    st.stop() # Stop execution if data loading failed

# Check if the required columns for filtering exist in the file
org_column = "Candidate's Organisation"
team_column = "Team Name"
mobile_column = "Candidate's Mobile"
email_column = "Candidate's Email" # Use Email as a unique identifier

required_cols = [org_column, team_column, mobile_column, email_column]
if not all(col in st.session_state.df.columns for col in required_cols):
    missing = [col for col in required_cols if col not in st.session_state.df.columns]
    st.error(f"Error: The required filter/key column(s) {', '.join(missing)} were not found in the Excel file.")
    st.stop()

# --- Filter Widgets ---
organisations = sorted(st.session_state.df[org_column].dropna().unique())

col1, col2 = st.columns(2)

with col1:
    selected_orgs = st.multiselect(
        label="Filter by Organisation(s):",
        options=organisations,
        placeholder="Select one or more organisations"
    )

with col2:
    team_search_query = st.text_input(
        label="Search by Team Name:",
        placeholder="Enter a team name to search"
    ).strip()

mobile_search_query = st.text_input(
    label="Search by Mobile Number:",
    placeholder="Enter a mobile number (e.g., 987...)"
).strip()

# --- NEW: Add New Entry Section ---
st.divider()
with st.expander("➕ Add New Team Leader Entry"):
    with st.form(key="add_form", clear_on_submit=True):
        st.write("Enter the details for the new team leader. Required fields are marked with *.")
        
        # Use columns for a cleaner form layout
        c1, c2 = st.columns(2)
        with c1:
            new_team_name = st.text_input("Team Name*")
            new_candidate_name = st.text_input("Candidate's Name*")
            new_email = st.text_input("Candidate's Email* (Must be unique)")
        with c2:
            new_mobile = st.text_input("Candidate's Mobile")
            new_location = st.text_input("Candidate's Location")
            new_org = st.text_input("Candidate's Organisation*")
        
        submit_button = st.form_submit_button(label="Add New Entry")

    if submit_button:
        # Validation
        if not new_email or not new_team_name or not new_candidate_name or not new_org:
            st.error("Please fill in all required fields marked with *.")
        elif not st.session_state.df[st.session_state.df[email_column] == new_email].empty:
            st.error(f"An entry with the email {new_email} already exists.")
        else:
            # All good, create the new row as a dictionary
            new_entry = {
                "Team Name": new_team_name,
                "Candidate's Name": new_candidate_name,
                "Candidate's Email": new_email,
                "Candidate's Mobile": new_mobile,
                "Candidate's Location": new_location,
                "Candidate's Organisation": new_org,
                "Candidate role": "Team Leader" # Hardcode this as it's the Team Leader dashboard
            }
            
            # Create a single-row DataFrame from the new entry
            new_row_df = pd.DataFrame([new_entry])
            
            # Concatenate the new row to the existing dataframe in session state
            st.session_state.df = pd.concat([st.session_state.df, new_row_df], ignore_index=True)
            
            # Save the updated dataframe back to the Excel file
            if save_to_excel(input_file):
                st.success(f"Successfully added {new_candidate_name} from {new_team_name}.")
                st.balloons()
                st.rerun() # Refresh the app to show the new entry
st.divider()

# --- Filtering Logic ---
# Start with the full session state dataframe
filtered_df = st.session_state.df

if selected_orgs:
    filtered_df = filtered_df[filtered_df[org_column].isin(selected_orgs)]

if team_search_query:
    filtered_df = filtered_df[filtered_df[team_column].str.contains(team_search_query, case=False, na=False)]

if mobile_search_query:
    filtered_df = filtered_df[filtered_df[mobile_column].str.contains(mobile_search_query, na=False)]
    
# --- Display Logic ---
columns_to_display = [
    "Team Name",
    "Candidate's Name",
    "Candidate's Location",
    "Candidate's Organisation",
    "Candidate's Email",
    "Candidate's Mobile"
]

if not selected_orgs and not team_search_query and not mobile_search_query:
    st.info("Showing all entries. Use the filters above to narrow the results.")
    st.subheader("All Team Leader Registrations")
else:
    st.subheader("Filtered Results")

st.metric("Total Rows Found", len(filtered_df))

# --- Manual Table with Delete Buttons ---
# Prepare the dataframe with Sl. No.
table_df = filtered_df.copy()
table_df.reset_index(drop=True, inplace=True)
table_df.index = table_df.index + 1
table_df.index.name = "Sl. No."
table_df.reset_index(inplace=True) # 'Sl. No.' is now a column

# Define columns + 1 for Sl. No. + 1 for delete button
col_config = [0.5, 2, 3, 2, 3, 3, 2, 1] # Relative widths
headers = ["Sl. No."] + columns_to_display + ["Action"]
cols = st.columns(col_config)
for col, header in zip(cols, headers):
    col.markdown(f"**{header}**")

st.divider()

if table_df.empty:
    st.info("No matching entries found.")

# This function is now only for deletion
def delete_entry(email_to_delete):
    try:
        original_index = st.session_state.df[st.session_state.df[email_column] == email_to_delete].index
        
        if not original_index.empty:
            st.session_state.df.drop(original_index, inplace=True)
            if save_to_excel(input_file): # Call the save function
                st.success(f"Successfully deleted entry for {email_to_delete}.")
            # No rerun here, it's handled in the button click
        else:
            st.error("Could not find the entry to delete. It might have already been removed.")
            
    except Exception as e:
        st.error(f"An error occurred while deleting: {e}")

# Iterate over the filtered dataframe and display rows
for index, row in table_df.iterrows():
    cols = st.columns(col_config)
    cols[0].write(row["Sl. No."])
    cols[1].write(row["Team Name"])
    cols[2].write(row["Candidate's Name"])
    cols[3].write(row["Candidate's Location"])
    cols[4].write(row["Candidate's Organisation"])
    cols[5].write(row["Candidate's Email"])
    cols[6].write(row["Candidate's Mobile"])
    
    # Add the delete button in the last column
    button_key = f"delete_{row[email_column]}"
    if cols[7].button("Delete", key=button_key, type="primary"):
        st.warning(f"**Warning:** This action is permanent and will modify your `{input_file}` file.")
        email_to_delete = row[email_column]
        delete_entry(email_to_delete) # Call the updated delete function
        st.rerun() # Rerun the app to reflect the change immediately

