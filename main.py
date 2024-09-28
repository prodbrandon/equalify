import streamlit as st
from datetime import datetime, timedelta

# Ensure page configuration is set before any other Streamlit code
st.set_page_config(layout="wide")  # Enables wide mode for better display when sidebar is minimized

# Inject custom CSS to change the font to Helvetica and enhance buttons visually
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Helvetica:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Helvetica', sans-serif;
    }
    .saved-button, .applied-button {
        color: white;
        background-color: green;
        border: none;
        padding: 6px 12px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        cursor: not-allowed;
        margin: 4px 2px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("Equalify 🎓")
st.write("Empowering underrepresented communities with scholarships for students!")

# Expanded sample static scholarship data with more DEI focus, including due dates
scholarships_data = [
    # Same data as before (no changes to the data)
]

# Convert due_date strings to datetime objects for sorting
for scholarship in scholarships_data:
    scholarship['due_date'] = datetime.strptime(scholarship['due_date'], "%Y-%m-%d")

# Initialize session state for saved, applied scholarships
if 'saved_scholarships' not in st.session_state:
    st.session_state.saved_scholarships = []
if 'applied_scholarships' not in st.session_state:
    st.session_state.applied_scholarships = []

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


# Enhanced search function
def search_scholarships(scholarship_list, query):
    if query == "":
        return scholarship_list
    keywords = query.lower().split()
    return [scholarship for scholarship in scholarship_list if any(keyword in scholarship["name"].lower()
                                                                   or keyword in scholarship["location"].lower()
                                                                   or keyword in scholarship[
                                                                       "extra_requirements"].lower()
                                                                   for keyword in keywords)]


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

        # Highlight scholarships with upcoming deadlines (e.g., less than 30 days)
        days_until_due = (scholarship['due_date'] - datetime.now()).days
        if days_until_due <= 30:
            st.write(f"**Deadline Approaching:** {days_until_due} days left! ⏰")

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

        # Save, apply buttons with marked state
        col1, col2 = st.columns(2)
        with col1:
            if scholarship not in st.session_state.saved_scholarships:
                if st.button(f"Save {scholarship['name']}", key=f"save-{scholarship['name']}"):
                    st.session_state.saved_scholarships.append(scholarship)
                    st.success(f"Scholarship '{scholarship['name']}' saved! 💾")
            else:
                st.button(f"Saved {scholarship['name']}", disabled=True, key=f"saved-{scholarship['name']}",
                          class_="saved-button")

        with col2:
            if scholarship not in st.session_state.applied_scholarships:
                if st.button(f"Apply {scholarship['name']}", key=f"apply-{scholarship['name']}"):
                    st.session_state.applied_scholarships.append(scholarship)
                    st.success(f"Scholarship '{scholarship['name']}' marked as applied! ✔️")
            else:
                st.button(f"Applied {scholarship['name']}", disabled=True, key=f"applied-{scholarship['name']}",
                          class_="applied-button")

with tab2:
    st.write(f"You have saved {len(st.session_state.saved_scholarships)} scholarships.")
    for scholarship in st.session_state.saved_scholarships:
        st.subheader(scholarship["name"])
        st.write(f"**Reward Amount**: ${scholarship['reward_amount']}")
        st.write(f"**Due Date**: {scholarship['due_date'].strftime('%Y-%m-%d')}")
        if st.button(f"Remove from Saved {scholarship['name']}", key=f"remove-saved-{scholarship['name']}"):
            st.session_state.saved_scholarships.remove(scholarship)
            st.info(f"Scholarship '{scholarship['name']}' removed from saved.")

with tab3:
    st.write(f"You have applied to {len(st.session_state.applied_scholarships)} scholarships.")
    for scholarship in st.session_state.applied_scholarships:
        st.subheader(scholarship["name"])
        st.write(f"**Reward Amount**: ${scholarship['reward_amount']}")
        st.write(f"**Due Date**: {scholarship['due_date'].strftime('%Y-%m-%d')}")
        if st.button(f"Remove from Applied {scholarship['name']}", key=f"remove-applied-{scholarship['name']}"):
            st.session_state.applied_scholarships.remove(scholarship)
            st.info(f"Scholarship '{scholarship['name']}' removed from applied.")
