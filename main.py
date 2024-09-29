import streamlit as st
from datetime import datetime
from scholarship import Scholarship
from scholarshipList import ScholarshipList

# Ensure page configuration is set before any other Streamlit code
st.set_page_config(layout="wide")

# Inject custom CSS to style the buttons as "Saved" and "Applied"
st.markdown("""
    <style>
    .saved-button, .applied-button {
        background-color: green;
        color: white;
        border: none;
        padding: 6px 12px;
        text-align: center;
        font-size: 16px;
        border-radius: 8px;
        cursor: not-allowed;
        margin: 4px 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("Equalify 🎓")
st.write("Empowering underrepresented communities with scholarships for students!")

# Initialize the ScholarshipList
scholarship_list = ScholarshipList()

# Sample static scholarship data as `Scholarship` objects
scholarships_data = [
    Scholarship(1, "Arizona Leadership Scholarship", "All", True, "All", "Arizona State University",
                "Arizona", 5000, False, "500-word essay", datetime(2024, 12, 15), True, "Leadership-based scholarship."),
    Scholarship(2, "Native American Excellence Scholarship", "All", False, "Native American",
                "Arizona State University", "Arizona", 3000, False, "Must take a Native American Studies class",
                datetime(2024, 10, 1), False, "Scholarship for Native American students."),
    # Add more scholarships here...
]

# Add all the scholarships to the ScholarshipList
for scholarship in scholarships_data:
    scholarship_list.add_scholarship(scholarship)

# Initialize session state for saved and applied scholarships (using ScholarshipList objects)
if 'saved_scholarships' not in st.session_state:
    st.session_state.saved_scholarships = ScholarshipList()
if 'applied_scholarships' not in st.session_state:
    st.session_state.applied_scholarships = ScholarshipList()

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
        st.write(f"**Essay Required**: {'Yes' if scholarship.get_essay_required() else 'No'}")
        st.write(f"**Description**: {scholarship.get_description()}")
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
                if st.button(f"Apply {scholarship.get_name()}", key=f"apply-{scholarship.get_name()}"):
                    st.session_state.applied_scholarships.add_scholarship(scholarship)
                    st.success(f"Scholarship '{scholarship.get_name()}' marked as applied! ✔️")
            else:
                st.markdown(f"<button class='applied-button'>Applied {scholarship.get_name()}</button>",
                            unsafe_allow_html=True)

# Tab 2: Saved Scholarships
with tab2:
    st.write(f"You have saved {len(st.session_state.saved_scholarships.get_scholarships())} scholarships.")
    saved_scholarships_copy = st.session_state.saved_scholarships.get_scholarships().copy()
    for scholarship in saved_scholarships_copy:
        st.subheader(scholarship.get_name())
        st.write(f"**Reward Amount**: ${scholarship.get_reward()}")
        st.write(f"**Due Date**: {scholarship.get_due_date().strftime('%Y-%m-%d')}")
        if st.button(f"Remove from Saved {scholarship.get_name()}", key=f"remove-saved-{scholarship.get_name()}"):
            st.session_state.saved_scholarships.remove_scholarship(scholarship)
            st.info(f"Scholarship '{scholarship.get_name()}' removed from saved.")

# Tab 3: Applied Scholarships
with tab3:
    st.write(f"You have applied to {len(st.session_state.applied_scholarships.get_scholarships())} scholarships.")
    applied_scholarships_copy = st.session_state.applied_scholarships.get_scholarships().copy()
    for scholarship in applied_scholarships_copy:
        st.subheader(scholarship.get_name())
        st.write(f"**Reward Amount**: ${scholarship.get_reward()}")
        st.write(f"**Due Date**: {scholarship.get_due_date().strftime('%Y-%m-%d')}")
        if st.button(f"Remove from Applied {scholarship.get_name()}", key=f"remove-applied-{scholarship.get_name()}"):
            st.session_state.applied_scholarships.remove_scholarship(scholarship)
            st.info(f"Scholarship '{scholarship.get_name()}' removed from applied.")
