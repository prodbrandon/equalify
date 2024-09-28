import streamlit as st

# Title and description
st.set_page_config(layout="wide")  # Enables wide mode for better display when sidebar is minimized
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

# Sidebar filters with search and DEI categories
with st.sidebar:
    st.header("Filter Scholarships")

    # Search bar to find scholarships by name, location, or requirements
    search_query = st.text_input("Search for Scholarships", "")

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


# Search function to look for specific keywords in scholarships
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

# Display filtered results
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
    st.write(f"**Due Date**: {scholarship['due_date']}")
    st.write("---")

# Call to action in case no matching scholarships are found
if len(filtered_scholarships) == 0:
    st.write("## Don't see a scholarship that fits your needs?")
    st.write("We’re constantly updating our database. Keep checking for more opportunities!")
