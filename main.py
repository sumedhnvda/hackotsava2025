import streamlit as st
import pandas as pd

# Set the page configuration for a wider, more modern layout
st.set_page_config(layout="wide")

st.title("🎓 Team Leader Registrations Dashboard")
st.write("Use the filters below to search by organisation, team name, or both.")

# Use st.cache_data for better performance by loading and cleaning the data only once
@st.cache_data
def load_data(file_path):
    """Loads and cleans data from the specified Excel file."""
    try:
        df = pd.read_excel(file_path)
        
        # --- Data Cleaning Step for Mobile Numbers ---
        mobile_col = "Candidate's Mobile"
        if mobile_col in df.columns:
            # Ensure the column is treated as a string, handling potential missing values and whitespace
            df[mobile_col] = df[mobile_col].astype(str).str.strip()
            
            # Create a boolean mask for numbers that start with '91' and are long enough
            # to be a standard mobile number with a country code.
            mask = df[mobile_col].str.startswith('91') & (df[mobile_col].str.len() > 10)
            
            # Use the mask to apply the slicing operation, removing '91' only where appropriate
            df.loc[mask, mobile_col] = df.loc[mask, mobile_col].str[2:]
        # --- End of Cleaning Step ---
            
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please make sure it is in the same directory as the script.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the Excel file: {e}")
        return None

# --- Main App Logic ---
input_file = 'team_leaders.xlsx'
df = load_data(input_file)

if df is not None:
    # Check if the required columns for filtering exist in the file
    org_column = "Candidate's Organisation"
    team_column = "Team Name"
    if org_column in df.columns and team_column in df.columns:
        
        # --- Filter Widgets ---
        organisations = sorted(df[org_column].dropna().unique())
        
        selected_orgs = st.multiselect(
            label="Filter by Organisation(s):",
            options=organisations,
            placeholder="Select one or more organisations"
        )

        team_search_query = st.text_input(
            label="Search by Team Name:",
            placeholder="Enter a team name to search"
        ).strip()
        
        # --- Filtering Logic ---
        # Start with the full dataframe and apply filters sequentially
        filtered_df = df

        if selected_orgs:
            filtered_df = filtered_df[filtered_df[org_column].isin(selected_orgs)]
        
        if team_search_query:
            # Use .str.contains() for a case-insensitive search
            filtered_df = filtered_df[filtered_df[team_column].str.contains(team_search_query, case=False, na=False)]
        
        # --- Display Logic ---
        columns_to_display = [
            "Team Name",
            "Candidate's Name",
            "Candidate's Location",
            "Candidate's Organisation",
            "Candidate's Email",
            "Candidate's Mobile"
        ]
        
        if all(col in df.columns for col in columns_to_display):
            # Display the data table based on whether any filters have been applied
            if not selected_orgs and not team_search_query:
                # Show an initial message and the full table before a selection is made
                st.info("Showing all entries. Use the filters above to narrow the results.")
                st.subheader("All Team Leader Registrations")
                st.metric("Total Rows", len(df))

                display_df = df[columns_to_display].copy()
                display_df.reset_index(drop=True, inplace=True)
                display_df.index = display_df.index + 1
                display_df.index.name = "Sl. No."

                st.dataframe(display_df)
            else:
                st.subheader("Filtered Results")
                st.metric("Total Rows Found", len(filtered_df))
                
                display_df = filtered_df[columns_to_display].copy()
                display_df.reset_index(drop=True, inplace=True)
                display_df.index = display_df.index + 1
                display_df.index.name = "Sl. No."
                
                st.dataframe(display_df)
        else:
            missing_cols = [col for col in columns_to_display if col not in df.columns]
            st.error(f"Error: The following required columns are missing from the Excel file: {', '.join(missing_cols)}")

    else:
        missing = []
        if org_column not in df.columns:
            missing.append(f"'{org_column}'")
        if team_column not in df.columns:
            missing.append(f"'{team_column}'")
        st.error(f"Error: The required column(s) {', '.join(missing)} were not found in the Excel file.")

