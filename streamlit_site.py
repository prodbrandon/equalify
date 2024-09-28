import streamlit as st

# Title and description
st.title("SB^3: Scholarship Search Engine")
st.write("Helping underrepresented communities find scholarships for Arizona and ASU")

# Sample static scholarship data
scholarships_data = [
    {
        "name": "Arizona Leadership Scholarship",
        "merit_based": True,
        "ethnicity": "All",
        "universities": ["Arizona State University"],
        "location": "Arizona",
        "reward_amount": 5000,
        "extra_requirements": "500-word essay",
    },
    {
        "name": "Native American Excellence Scholarship",
        "merit_based": False,
        "ethnicity": "Native American",
        "universities": ["University of Arizona", "Arizona State University"],
        "location": "Arizona",
        "reward_amount": 3000,
        "extra_requirements": "Must take at least one Native American Studies class",
    },
    {
        "name": "Hispanic Scholars Award",
        "merit_based": True,
        "ethnicity": "Hispanic",
        "universities": ["Northern Arizona University"],
        "location": "Arizona",
        "reward_amount": 2000,
        "extra_requirements": "GPA of 3.5+ required",
    }
]

# Sidebar filters
st.sidebar.header("Filter Scholarships")

ethnicity_filter = st.sidebar.selectbox("Required Ethnicity", ["All", "African American", "Hispanic", "Native American", "Other"])
university_filter = st.sidebar.selectbox("Applicable Universities", ["All", "Arizona State University", "University of Arizona", "Northern Arizona University"])
merit_based_filter = st.sidebar.checkbox("Merit-Based", value=False)
min_reward = st.sidebar.number_input("Minimum Reward Amount ($)", min_value=0, value=0)

# Filtering scholarships based on user input
filtered_scholarships = []
for scholarship in scholarships_data:
    if (ethnicity_filter == "All" or scholarship["ethnicity"] == ethnicity_filter) and \
       (university_filter == "All" or university_filter in scholarship["universities"]) and \
       (not merit_based_filter or scholarship["merit_based"]) and \
       scholarship["reward_amount"] >= min_reward:
        filtered_scholarships.append(scholarship)

# Display results
st.write(f"Found {len(filtered_scholarships)} scholarships matching your filters.")

for scholarship in filtered_scholarships:
    st.subheader(scholarship["name"])
    st.write(f"**Merit-Based**: {scholarship['merit_based']}")
    st.write(f"**Required Ethnicity**: {scholarship['ethnicity']}")
    st.write(f"**Applicable Universities**: {', '.join(scholarship['universities'])}")
    st.write(f"**Location**: {scholarship['location']}")
    st.write(f"**Reward Amount**: ${scholarship['reward_amount']}")
    st.write(f"**Extra Requirements**: {scholarship['extra_requirements']}")
    st.write("---")

# Footer or call to action
st.write("## Don't see a scholarship that fits your needs?")
st.write("We’re constantly updating our database. Keep checking for more opportunities!")
