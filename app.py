import streamlit as st

st.set_page_config(
    page_title="Portfolio Tracker & Analysis",
    page_icon="📊",
    layout="wide"
)

st.sidebar.success("Select a page above.")

# Initialize session state variables if they don't exist
# We'll use session state to store portfolio data, login status etc.
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False # Basic login status placeholder
if 'portfolio_transactions' not in st.session_state:
    # For now, we'll manage transactions in memory via session state.
    # Later, we can load/save from a file or database.
    st.session_state.portfolio_transactions = [] # List to hold transaction dicts


# --- Basic Login Placeholder ---
# This is NOT secure, for demonstration only.
# Replace with a proper authentication method (e.g., streamlit-authenticator) for real use.
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("PASSWORD", "test"): # Use secrets or a default
            st.session_state.logged_in = True
            del st.session_state["password"]  # Don't store password.
        else:
            st.session_state.logged_in = False
            st.error("😕 Password incorrect")

    if st.session_state.get("logged_in", False):
        return True

    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    return False

# --- Main App Logic ---
st.title("Welcome to the Portfolio Tracker & Analysis App")
st.write("Please log in using the sidebar password or select a page.")

# Uncomment the following line to enable the basic password check
# if not check_password():
#    st.stop() # Stop execution if not logged in

st.info("**Note:** Login is currently disabled for easier development. Select a page from the sidebar.")

# The rest of the app structure is handled by files in the 'pages/' directory.
# Streamlit automatically creates the sidebar navigation based on those files.

