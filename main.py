import streamlit as st
from datetime import datetime

# Ensure page configuration is set before any other Streamlit code
st.set_page_config(layout="wide")  # Enables wide mode for better display when sidebar is minimized

# Inject custom CSS to change the font to Helvetica
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Helvetica:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Helvetica', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("Equalify")
st.write("Empowering underrepresented communities with scholarships for students")

# Expanded sample static scholarship data with more DEI focus, including due dates
scholarships_data = [
    {
        "name": "Arizona Leadership Scholarship",
        "merit_based": True,
        "ethnicity": "All",
        "gender": "All",
        "first_gen": False,
        "lgbtq": False,
        "universities": ["Arizona State University"],
        "location": "Arizona",
        "reward_amount": 5000,
        "extra_requirements": "500-word essay",
        "due_date": "2024-12-15"
    },
    {
        "name": "Native American Excellence Scholarship",
        "merit_based": False,
        "ethnicity": "Native American",
        "gender": "All",
        "first_gen": False,
        "lgbtq": False,
        "universities": ["University of Arizona", "Arizona State University"],
        "location": "Arizona",
        "reward_amount": 3000,
        "extra_requirements": "Must take at least one Native American Studies class",
        "due_date": "2024-10-01"
    },
    {
        "name": "Hispanic Scholars Award",
        "merit_based": True,
        "ethnicity": "Hispanic",
        "gender": "All",
        "first_gen": False,
        "lgbtq": False,
        "universities": ["Northern Arizona University"],
        "location": "Arizona",
        "reward_amount": 2000,
        "extra_requirements": "GPA of 3.5+ required",
        "due_date": "2024-11-20"
    },
    {
        "name": "LGBTQ+ Advocacy Scholarship",
        "merit_based": False,
        "ethnicity": "All",
        "gender": "All",
        "first_gen": False,
        "lgbtq": True,
        "universities": ["Arizona State University", "University of Arizona"],
        "location": "Arizona",
        "reward_amount": 4000,
        "extra_requirements": "Must demonstrate involvement in LGBTQ+ advocacy",
        "due_date": "2024-09-30"
    },
    {
        "name": "First-Generation College Student Award",
        "merit_based": False,
        "ethnicity": "All",
        "gender": "All",
        "first_gen": True,
        "lgbtq": False,
        "universities": ["Arizona State University"],
        "location": "Arizona",
        "reward_amount": 2500,
        "extra_requirements": "Must be the first in family to attend college",
        "due_date": "2024-12-01"
    },
    {
        "name": "Women in STEM Scholarship",
        "merit_based": True,
        "ethnicity": "All",
        "gender": "Female",
        "first_gen": False,
        "lgbtq": False,
        "universities": ["Arizona State University", "Northern Arizona University"],
        "location": "Arizona",
        "reward_amount": 3500,
        "extra_requirements": "Must be pursuing a degree in STEM",
        "due_date": "2024-10-15"
    }
]

# Convert due_date strings to datetime objects for sorting
for scholarship in scholarships_data:
    scholarship['due_date'] = datetime.strptime(scholarship['due_date'], "%Y-%m-%d")

# Initialize session state for saved, applied, and pending scholarships if not already present
if 'saved_scholarships' not in st.session_state:
    st.session_state.saved_scholarships = []
if 'applied_scholarships' not in st.session_state:
    st.session_state.applied_scholarships = []
if 'pending_scholarships' not in st.session_state:
    st.session_state.pending_scholarships = []

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
    lgbtq_filter = st.checkbox("LGBTQ+", value=False)
    university_filter = st.selectbox("Applicable Universities",
                                     ["All", "Arizona State University", "University of Arizona",
                                      "Northern Arizona University"])
    merit_based_filter = st.checkbox("Merit-Based", value=False)
    min_reward = st.number_input("Minimum Reward Amount ($)", min_value=0, value=0)
    max_reward = st.number_input("Maximum Reward Amount ($)", min_value=0, value=10000)

    sort_by_due_date = st.selectbox("Sort by Due Date", ["Ascending", "Descending"])


# Function to filter scholarships based on search and filters
def search_scholarships(scholarship_list, query):
    if query == "":
        return scholarship_list
    return [scholarship for scholarship in scholarship_list if query.lower() in scholarship["name"].lower()
            or query.lower() in scholarship["location"].lower()
            or query.lower() in scholarship["extra_requirements"].lower()]


# Filtering scholarships based on sidebar filters and search input
filtered_scholarships = search_scholarships(scholarships_data, search_query)
filtered_scholarships = [scholarship for scholarship in filtered_scholarships if
                         (ethnicity_filter == "All" or scholarship["ethnicity"] == ethnicity_filter) and
                         (gender_filter == "All" or scholarship["gender"] == gender_filter) and
                         (not first_gen_filter or scholarship["first_gen"]) and
                         (not lgbtq_filter or scholarship["lgbtq"]) and
                         (university_filter == "All" or university_filter in scholarship["universities"]) and
                         (not merit_based_filter or scholarship["merit_based"]) and
                         (min_reward <= scholarship["reward_amount"] <= max_reward)]

# Sort scholarships by due date
if sort_by_due_date == "Ascending":
    filtered_scholarships = sorted(filtered_scholarships, key=lambda x: x['due_date'])
else:
    filtered_scholarships = sorted(filtered_scholarships, key=lambda x: x['due_date'], reverse=True)

# Tabs for viewing all scholarships, saved, and applied
tab1, tab2, tab3 = st.tabs(["All Scholarships", "Saved Scholarships", "Applied Scholarships"])

with tab1:
    st.write(f"Found {len(filtered_scholarships)} scholarships matching your filters and search query.")
    for scholarship in filtered_scholarships:
        st.subheader(scholarship["name"])
        st.write(f"**Merit-Based**: {scholarship['merit_based']}")
        st.write(f"**Required Ethnicity**: {scholarship['ethnicity']}")
        st.write(f"**Gender**: {scholarship['gender']}")
        st.write(f"**First-Generation College Student**: {'Yes' if scholarship['first_gen'] else 'No'}")
        st.write(f"**LGBTQ+ Support**: {'Yes' if scholarship['lgbtq'] else 'No'}")
        st.write(f"**Applicable Universities**: {', '.join(scholarship['universities'])}")
        st.write(f"**Location**: {scholarship['location']}")
        st.write(f"**Reward Amount**: ${scholarship['reward_amount']}")
        st.write(f"**Extra Requirements**: {scholarship['extra_requirements']}")
        st.write(f"**Due Date**: {scholarship['due_date'].strftime('%Y-%m-%d')}")

        # Save, apply, pending buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if scholarship not in st.session_state.saved_scholarships:
                if st.button(f"Save {scholarship['name']}", key=f"save-{scholarship['name']}"):
                    st.session_state.saved_scholarships.append(scholarship)
        with col2:
            if scholarship not in st.session_state.applied_scholarships:
                if st.button(f"Apply {scholarship['name']}", key=f"apply-{scholarship['name']}"):
                    st.session_state.applied_scholarships.append(scholarship)
        with col3:
            if scholarship not in st.session_state.pending_scholarships:
                if st.button(f"Pending {scholarship['name']}", key=f"pending-{scholarship['name']}"):
                    st.session_state.pending_scholarships.append(scholarship)

with tab2:
    st.write(f"You have saved {len(st.session_state.saved_scholarships)} scholarships.")
    for scholarship in st.session_state.saved_scholarships:
        st.subheader(scholarship["name"])
        st.write(f"**Reward Amount**: ${scholarship['reward_amount']}")
        st.write(f"**Due Date**: {scholarship['due_date'].strftime('%Y-%m-%d')}")
        if st.button(f"Remove from Saved {scholarship['name']}", key=f"remove-saved-{scholarship['name']}"):
            st.session_state.saved_scholarships.remove(scholarship)

with tab3:
    st.write(f"You have applied to {len(st.session_state.applied_scholarships)} scholarships.")
    for scholarship in st.session_state.applied_scholarships:
        st.subheader(scholarship["name"])
        st.write(f"**Reward Amount**: ${scholarship['reward_amount']}")
        st.write(f"**Due Date**: {scholarship['due_date'].strftime('%Y-%m-%d')}")
        if st.button(f"Remove from Applied {scholarship['name']}", key=f"remove-applied-{scholarship['name']}"):
            st.session_state.applied_scholarships.remove(scholarship)
