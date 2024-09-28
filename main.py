import streamlit as st
from datetime import datetime
import bcrypt
from scholarship import Scholarship
from scholarshipList import ScholarshipList

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'saved_scholarships' not in st.session_state:
    st.session_state.saved_scholarships = ScholarshipList()
if 'applied_scholarships' not in st.session_state:
    st.session_state.applied_scholarships = ScholarshipList()

# In-memory user database (to be replaced with persistent storage later)
user_database = {}

# Helper function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Helper function to check passwords
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Function to create a new user
def create_user(username, password):
    if username in user_database:
        return False  # Username already exists
    hashed_password = hash_password(password)
    user_database[username] = hashed_password
    return True

# Function to authenticate a user
def authenticate_user(username, password):
    if username not in user_database:
        return False  # User not found
    stored_password = user_database[username]
    return check_password(password, stored_password)

# Login/Signup UI
def login_signup():
    st.title("Login / Signup")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # Login Tab
    with tab1:
        st.subheader("Login to your account")
        login_username = st.text_input("Login Username", key="login_username")
        login_password = st.text_input("Login Password", type="password", key="login_password")
        if st.button("Login"):
            if authenticate_user(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(f"Welcome back, {login_username}!")
            else:
                st.error("Invalid username or password")

    # Signup Tab
    with tab2:
        st.subheader("Create a new account")
        signup_username = st.text_input("Signup Username", key="signup_username")
        signup_password = st.text_input("Signup Password", type="password", key="signup_password")
        if st.button("Signup"):
            if create_user(signup_username, signup_password):
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Username already exists. Please choose a different username.")

# Main app function (scholarships page)
def main_app():
    st.title("Equalify 🎓")
    st.write(f"Empowering underrepresented communities with scholarships for students! Welcome, {st.session_state.username}")

    # Initialize the ScholarshipList
    scholarship_list = ScholarshipList()

    # Sample static scholarship data as `Scholarship` objects
    scholarships_data = [
        Scholarship(False, "Arizona Leadership Scholarship", "All", True, "All", "Arizona State University",
                    "Arizona", 5000, False, "500-word essay", datetime(2024, 12, 15)),
        Scholarship(False, "Native American Excellence Scholarship", "All", False, "Native American",
                    "Arizona State University", "Arizona", 3000, False, "Must take a Native American Studies class",
                    datetime(2024, 10, 1)),
        # Add more scholarships here...
    ]

    # Add all the scholarships to the ScholarshipList
    for scholarship in scholarships_data:
        scholarship_list.add_scholarship(scholarship)

    # Sidebar filters with search and DEI categories
    with st.sidebar:
        st.header("Filter Scholarships")

        # Search bar to find scholarships by name, location, or requirements
        search_query = st.text_input("Search for Scholarships", "")

        # Filter options
        ethnicity_filter = st.selectbox("Required Ethnicity",
                                        ["All", "African American", "Hispanic", "Native American", "Asian", "Other"])
        gender_filter = st.selectbox("Gender", ["All", "Female", "Male", "Non-binary", "Other"])
        first_gen_filter = st.checkbox("First-Generation College Student", value=False)
        merit_based_filter = st.checkbox("Merit-Based", value=False)
        lgbtq_filter = st.checkbox("LGBTQ+", value=False)
        university_filter = st.selectbox("Applicable Universities",
                                         ["All", "Arizona State University", "University of Arizona",
                                          "Northern Arizona University"])
        min_reward = st.number_input("Minimum Reward Amount ($)", min_value=0, value=0)
        max_reward = st.number_input("Maximum Reward Amount ($)", min_value=0, value=10000)

        sort_by_due_date = st.selectbox("Sort by Due Date", ["Ascending", "Descending"])

    # Filtering scholarships based on sidebar filters and search input
    def filter_scholarships(scholarship_list, query):
        """Filter scholarships based on the sidebar filters and search query."""
        filtered_list = scholarship_list.get_scholarships()

        if query:
            filtered_list = scholarship_list.search_by_name(query)

        filtered_list = [scholarship for scholarship in filtered_list if
                         (ethnicity_filter == "All" or scholarship.get_ethnicity() == ethnicity_filter) and
                         (gender_filter == "All" or scholarship.get_gender() == gender_filter) and
                         (not first_gen_filter or scholarship.get_LGBT()) and
                         (not lgbtq_filter or scholarship.get_LGBT()) and
                         (university_filter == "All" or university_filter == scholarship.get_university()) and
                         (min_reward <= scholarship.get_reward() <= max_reward)]

        # Sort scholarships by due date
        if sort_by_due_date == "Ascending":
            return sorted(filtered_list, key=lambda x: x.get_due_date())
        else:
            return sorted(filtered_list, key=lambda x: x.get_due_date(), reverse=True)

    filtered_scholarships = filter_scholarships(scholarship_list, search_query)

    # Tabs for viewing all scholarships, saved, and applied
    tab1, tab2, tab3 = st.tabs(["All Scholarships", "Saved Scholarships", "Applied Scholarships"])

    # Tab 1: All Scholarships
    with tab1:
        st.write(f"Found {len(filtered_scholarships)} scholarships matching your filters and search query.")

        for scholarship in filtered_scholarships:
            st.subheader(scholarship.get_name())

            # Highlight scholarships with upcoming deadlines (e.g., less than 30 days)
            days_until_due = (scholarship.get_due_date() - datetime.now()).days
            if days_until_due <= 30:
                st.write(f"**Deadline Approaching:** {days_until_due} days left! ⏰")

            st.write(f"**Merit-Based**: {scholarship.get_merit()}")
            st.write(f"**Required Ethnicity**: {scholarship.get_ethnicity()}")
            st.write(f"**Gender**: {scholarship.get_gender()}")
            st.write(f"**First-Generation College Student**: {'Yes' if scholarship.get_LGBT() else 'No'}")
            st.write(f"**LGBTQ+ Support**: {'Yes' if scholarship.get_LGBT() else 'No'}")
            st.write(f"**Applicable Universities**: {scholarship.get_university()}")
            st.write(f"**Location**: {scholarship.get_location()}")
            st.write(f"**Reward Amount**: ${scholarship.get_reward()}")
            st.write(f"**Extra Requirements**: {scholarship.get_extras()}")
            st.write(f"**Due Date**: {scholarship.get_due_date().strftime('%Y-%m-%d')}")

            # Save, apply buttons with marked state
            col1, col2 = st.columns(2)
            with col1:
                if scholarship not in st.session_state.saved_scholarships.get_scholarships():
                    if st.button(f"Save {scholarship.get_name()}", key=f"save-{scholarship.get_name()}"):
                        st.session_state.saved_scholarships.add_scholarship(scholarship)
                        st.success(f"Scholarship '{scholarship.get_name()}' saved! 💾")
                else:
                    st.markdown(f"<button class='saved-button'>Saved {scholarship.get_name()}</button>",
                                unsafe_allow_html=True)

            with col2:
                if scholarship not in st.session_state.applied_scholarships.get_scholarships():
                    if st.button(f"Apply to {scholarship.get_name()}", key=f"apply-{scholarship.get_name()}"):
                        st.session_state.applied_scholarships.add_scholarship(scholarship)
                        st.success(f"Scholarship '{scholarship.get_name()}' marked as applied! ✔️")
                else:
                    st.markdown(f"<button class='applied-button'>Applied {scholarship.get_name()}</button>",
                                unsafe_allow_html=True)

# Run either the login/signup page or the main app
if not st.session_state.logged_in:
    login_signup()
else:
    main_app()
