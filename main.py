import streamlit as st
from datetime import datetime, date

# Scholarship class definition
class Scholarship:
    def __init__(self, favorited: bool, name: str, gender: str, merit_based: bool,
                 ethnicity: str, university: str, location: str, reward: float, 
                 LGBT: bool, extras: str, due_date: date):
        self.__favorited = favorited
        self.__name = name
        self.__gender = gender
        self.__merit_based = merit_based
        self.__ethnicity = ethnicity
        self.__university = university
        self.__location = location
        self.__reward = reward
        self.__LGBT = LGBT
        self.__extras = extras
        self.__due_date = due_date

    def __hash__(self) -> int:
        return hash((self.__favorited, self.__name, self.__merit_based, 
                     self.__gender, self.__ethnicity, self.__university, 
                     self.__location, self.__reward, self.__LGBT, 
                     self.__extras, self.__due_date))

    def __eq__(self, other: 'Scholarship') -> bool:
        if not isinstance(other, Scholarship):
            return NotImplemented
        return (
            self.__favorited == other.__favorited and
            self.__name == other.__name and
            self.__merit_based == other.__merit_based and
            self.__gender == other.__gender and
            self.__ethnicity == other.__ethnicity and
            self.__university == other.__university and
            self.__location == other.__location and
            self.__reward == other.__reward and
            self.__LGBT == other.__LGBT and
            self.__extras == other.__extras and
            self.__due_date == other.__due_date 
        )

    # Getters and setters
    # ...

# ScholarshipList class definition
class ScholarshipList:
    def __init__(self):
        self.__data = set()

    def add_scholarship(self, new_scholarship: Scholarship) -> None:
        self.__data.add(new_scholarship)

    def remove_scholarship(self, target: Scholarship) -> bool:
        if target in self.__data:
            self.__data.remove(target)
            return True
        return False

    def get_scholarships(self) -> set:
        return self.__data

# Streamlit app starts here
st.set_page_config(layout="wide")

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
st.title("Equalify 🎓")
st.write("Empowering underrepresented communities with scholarships for students!")

# Initialize a ScholarshipList instance
scholarship_list = ScholarshipList()

# Sample static scholarship data
scholarships_data = [
    Scholarship(False, "Arizona Leadership Scholarship", "All", True, "All", "Arizona State University", "Arizona", 5000, False, "500-word essay", date(2024, 12, 15)),
    Scholarship(False, "Native American Excellence Scholarship", "All", False, "Native American", "University of Arizona", "Arizona", 3000, False, "Must take at least one Native American Studies class", date(2024, 10, 1)),
    Scholarship(False, "Hispanic Scholars Award", "All", True, "Hispanic", "Northern Arizona University", "Arizona", 2000, False, "GPA of 3.5+ required", date(2024, 11, 20)),
    Scholarship(False, "LGBTQ+ Advocacy Scholarship", "All", False, "All", "Arizona State University", "Arizona", 4000, True, "Must demonstrate involvement in LGBTQ+ advocacy", date(2024, 9, 30)),
    Scholarship(False, "First-Generation College Student Award", "All", False, "All", "Arizona State University", "Arizona", 2500, False, "Must be the first in family to attend college", date(2024, 12, 1)),
    Scholarship(False, "Women in STEM Scholarship", "Female", True, "All", "Arizona State University", "Arizona", 3500, False, "Must be pursuing a degree in STEM", date(2024, 10, 15))
]

# Add sample scholarships to the scholarship list
for scholarship in scholarships_data:
    scholarship_list.add_scholarship(scholarship)

# Initialize session state for saved, applied, and pending scholarships if not already present
if 'saved_scholarships' not in st.session_state:
    st.session_state.saved_scholarships = []
if 'applied_scholarships' not in st.session_state:
    st.session_state.applied_scholarships = []
if 'pending_scholarships' not in st.session_state:
    st.session_state.pending_scholarships = []

# Sidebar filters
with st.sidebar:
    st.header("Filter Scholarships")
    search_query = st.text_input("Search for Scholarships", "")
    ethnicity_filter = st.selectbox("Required Ethnicity", ["All", "African American", "Hispanic", "Native American", "Asian", "Other"])
    gender_filter = st.selectbox("Gender", ["All", "Female", "Male", "Non-binary", "Other"])
    first_gen_filter = st.checkbox("First-Generation College Student", value=False)
    merit_based_filter = st.checkbox("Merit-Based", value=False)
    lgbtq_filter = st.checkbox("LGBTQ+", value=False)
    university_filter = st.selectbox("Applicable Universities", ["All", "Arizona State University", "University of Arizona", "Northern Arizona University"])
    min_reward = st.number_input("Minimum Reward Amount ($)", min_value=0, value=0)
    max_reward = st.number_input("Maximum Reward Amount ($)", min_value=0, value=10000)
    sort_by_due_date = st.selectbox("Sort by Due Date", ["Ascending", "Descending"])

# Function to filter scholarships
def search_scholarships(scholarship_list, query):
    scholarships = scholarship_list.get_scholarships()
    if query == "":
        return scholarships
    return {scholarship for scholarship in scholarships if query.lower() in scholarship.get_name().lower()
            or query.lower() in scholarship.get_location().lower()
            or query.lower() in scholarship.get_extras().lower()}

# Filtering scholarships based on filters
filtered_scholarships = search_scholarships(scholarship_list, search_query)
filtered_scholarships = {scholarship for scholarship in filtered_scholarships if
                         (ethnicity_filter == "All" or scholarship.get_ethnicity() == ethnicity_filter) and
                         (gender_filter == "All" or scholarship.get_gender() == gender_filter) and
                         (not first_gen_filter or scholarship.get_favorited()) and
                         (not lgbtq_filter or scholarship.get_LGBT()) and
                         (university_filter == "All" or university_filter == scholarship.get_university()) and
                         (not merit_based_filter or scholarship.get_merit()) and
                         (min_reward <= scholarship.get_reward() <= max_reward)}

# Sort scholarships by due date
if sort_by_due_date == "Ascending":
    filtered_scholarships = sorted(filtered_scholarships, key=lambda x: x.get_due_date())
else:
    filtered_scholarships = sorted(filtered_scholarships, key=lambda x: x.get_due_date(), reverse=True)

# Tabs for viewing scholarships
tab1, tab2, tab3 = st.tabs(["All Scholarships", "Saved Scholarships", "Applied Scholarships"])

with tab1:
    st.write(f"Found {len(filtered_scholarships)} scholarships matching your filters and search query.")
    for scholarship in filtered_scholarships:
        st.subheader(scholarship.get_name())
        st.write(f"**Merit-Based**: {scholarship.get_merit()}")    
        st.write(f"**Required Ethnicity**: {scholarship.get_ethnicity()}")
        st.write(f"**Gender**: {scholarship.get_gender()}")
        st.write(f"**LGBTQ+ Support**: {'Yes' if scholarship.get_LGBT() else 'No'}")
        st.write(f"**Applicable Universities**: {scholarship.get_university()}")
        st.write(f"**Location**: {scholarship.get_location()}")
        st.write(f"**Reward Amount**: ${scholarship.get_reward()}")
        st.write(f"**Extra Requirements**: {scholarship.get_extras()}")
        st.write(f"**Due Date**: {scholarship.get_due_date()}")

        # Save, apply, pending buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if scholarship not in st.session_state.saved_scholarships:
                if st.button(f"Save {scholarship.get_name()}", key=scholarship.get_name() + "_save"):
                    st.session_state.saved_scholarships.append(scholarship)
                    st.success(f"{scholarship.get_name()} has been saved!")
            else:
                st.success(f"{scholarship.get_name()} is already saved!")

        with col2:
            if scholarship not in st.session_state.applied_scholarships:
                if st.button(f"Apply for {scholarship.get_name()}", key=scholarship.get_name() + "_apply"):
                    st.session_state.applied_scholarships.append(scholarship)
                    st.success(f"Applied for {scholarship.get_name()}!")
            else:
                st.success(f"You have already applied for {scholarship.get_name()}!")

        with col3:
            if scholarship not in st.session_state.pending_scholarships:
                if st.button(f"Mark {scholarship.get_name()} as Pending", key=scholarship.get_name() + "_pending"):
                    st.session_state.pending_scholarships.append(scholarship)
                    st.success(f"Marked {scholarship.get_name()} as pending!")
            else:
                st.success(f"{scholarship.get_name()} is already marked as pending!")

with tab2:
    st.write("Your Saved Scholarships:")
    for scholarship in st.session_state.saved_scholarships:
        st.subheader(scholarship.get_name())

with tab3:
    st.write("Your Applied Scholarships:")
    for scholarship in st.session_state.applied_scholarships:
        st.subheader(scholarship.get_name())

# Optional: Add a footer or other components here
st.write("### Thank you for using Equalify!")
