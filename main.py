import streamlit as st
import pandas as pd

# Set the page configuration for a wider, more modern layout
st.set_page_config(layout="wide")

st.title("🎓 Team Leader Registrations Dashboard")
st.write("Select an organisation from the dropdown menu below to view the registered team leaders.")

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
    # Check if the required column for filtering exists in the file
    required_column = "Candidate's Organisation"
    if required_column in df.columns:
        
        # Get a unique, sorted list of organisations for the dropdown
        # .dropna() removes any empty cells before creating the list
        organisations = sorted(df[required_column].dropna().unique())
        
        # Add a placeholder option at the beginning of the list
        options = ["Select an organisation..."] + organisations

        # Create the interactive dropdown menu
        selected_org = st.selectbox(
            label="Filter by Organisation:",
            options=options
        )
        
        # Define the specific columns to display in the table
        columns_to_display = [
            "Team Name",
            "Candidate's Name",
            "Candidate's Location",
            "Candidate's Organisation",
            "Candidate's Email",
            "Candidate's Mobile"
        ]
        
        # Check if all the requested columns actually exist in the file
        if all(col in df.columns for col in columns_to_display):
            # Display the data table based on the user's selection
            if selected_org != "Select an organisation...":
                st.subheader(f"Displaying Team Leaders from: {selected_org}")
                # Filter the dataframe to show only rows for the selected organisation
                filtered_df = df[df[required_column] == selected_org]
                # Display only the selected columns
                st.dataframe(filtered_df[columns_to_display])
            else:
                # Show an initial message and the full table before a selection is made
                st.info("Showing all entries. Select an organisation from the list above to filter the results.")
                st.subheader("All Team Leader Registrations")
                # Display only the selected columns from the full dataframe
                st.dataframe(df[columns_to_display])
        else:
            # Find which columns are missing and show a helpful error
            missing_cols = [col for col in columns_to_display if col not in df.columns]
            st.error(f"Error: The following required columns are missing from the Excel file: {', '.join(missing_cols)}")

    else:
        st.error(f"Error: The required column '{required_column}' was not found in the Excel file.")

