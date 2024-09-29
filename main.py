import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables (MongoDB URI)
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["scholarship_db"]
scholarships_collection = db["scholarships"]

# Ensure page configuration is set before any other Streamlit code
st.set_page_config(layout="wide")

# Inject custom CSS to style the buttons as "Saved", "Applied", and "Favorited"
st.markdown("""
    <style>
    .saved-button, .applied-button, .favorited-button {
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
st.title("Equalify🎓")
st.write("Empowering underrepresented communities with scholarships for students!")

# Initialize session state for saved, applied, and favorited scholarships
if 'saved_scholarships' not in st.session_state:
    st.session_state.saved_scholarships = set()
if 'applied_scholarships' not in st.session_state:
    st.session_state.applied_scholarships = set()
if 'favorited_scholarships' not in st.session_state:
    st.session_state.favorited_scholarships = set()

# Sidebar filters
with st.sidebar:
    st.header("Filter Scholarships")

    # Search bar to find scholarships by name, location, or requirements
    search_query = st.text_input("Search for Scholarships", "")

    # Filter options
    sort_by_due_date = st.selectbox("Sort by Due Date", ["Ascending", "Descending"])
    ethnicity_filter = st.selectbox("Required Ethnicity",
                                    ["All", "African American", "Hispanic", "Native American", "Asian", "Other"])
    gender_filter = st.selectbox("Gender", ["All", "Female", "Male", "Non-binary", "Other"])
    first_gen_filter = st.checkbox("First-Generation College Student", value=False)
    merit_based_filter = st.checkbox("Merit-Based", value=False)
    lgbtq_filter = st.checkbox("LGBTQ+", value=False)
    min_reward = st.number_input("Minimum Reward Amount ($)", min_value=0, value=0)
    max_reward = st.number_input("Maximum Reward Amount ($)", min_value=0, value=10000)

    # Filter based on "Essay" or "No Essay"
    essay_filter = st.radio("Essay Requirement", options=["All", "Essay", "No Essay"])

# Fetch scholarships from MongoDB and apply filters
def fetch_and_filter_scholarships():
    mongo_query = {}

    # Apply filters from sidebar
    if search_query:
        mongo_query["name"] = {"$regex": search_query, "$options": "i"}
    if ethnicity_filter != "All":
        mongo_query["ethnicity"] = ethnicity_filter
    if gender_filter != "All":
        mongo_query["gender"] = gender_filter
    if first_gen_filter:
        mongo_query["first_gen"] = True
    if merit_based_filter:
        mongo_query["merit_based"] = True
    if lgbtq_filter:
        mongo_query["LGBTQ"] = True
    mongo_query["reward"] = {"$gte": min_reward, "$lte": max_reward}

    # Essay filter
    if essay_filter == "Essay":
        mongo_query["extras"] = {"$regex": "essay", "$options": "i"}
    elif essay_filter == "No Essay":
        mongo_query["extras"] = {"$not": {"$regex": "essay", "$options": "i"}}

    # Fetch scholarships from MongoDB
    scholarships = list(scholarships_collection.find(mongo_query))

    # Sort scholarships by due date
    if sort_by_due_date == "Ascending":
        scholarships = sorted(scholarships, key=lambda x: x.get('due_date', datetime.max))
    else:
        scholarships = sorted(scholarships, key=lambda x: x.get('due_date', datetime.max), reverse=True)

    return scholarships


# Fetch filtered scholarships
filtered_scholarships = fetch_and_filter_scholarships()

# Tabs for viewing all scholarships, saved, applied, and favorited
tab1, tab2, tab3, tab4 = st.tabs(
    ["All Scholarships", "Saved Scholarships", "Applied Scholarships", "Favorited Scholarships"])

# Tab 1: All Scholarships
with tab1:
    st.write(f"Found {len(filtered_scholarships)} scholarships matching your filters and search query.")

    for scholarship in filtered_scholarships:
        scholarship_id = str(scholarship["_id"])

        # Safely access scholarship fields with defaults
        name = scholarship.get('name', 'Unnamed Scholarship')
        merit_based = scholarship.get('merit_based', 'Unknown')
        ethnicity = scholarship.get('ethnicity', 'All')
        gender = scholarship.get('gender', 'All')
        first_gen = scholarship.get('first_gen', False)
        lgbtq = scholarship.get('LGBTQ', False)
        location = scholarship.get('location', 'Unknown')
        reward = scholarship.get('reward', 0)
        extras = scholarship.get('extras', 'None')
        due_date = scholarship.get('due_date', None)

        st.subheader(name)

        # Highlight scholarships with upcoming deadlines (e.g., less than 30 days)
        if due_date:
            days_until_due = (due_date - datetime.now()).days
            if days_until_due <= 30:
                st.write(f"**Deadline Approaching:** {days_until_due} days left! ⏰")

        st.write(f"**Merit-Based**: {merit_based}")
        st.write(f"**Required Ethnicity**: {ethnicity}")
        st.write(f"**Gender**: {gender}")
        st.write(f"**First-Generation College Student**: {'Yes' if first_gen else 'No'}")
        st.write(f"**LGBTQ+ Support**: {'Yes' if lgbtq else 'No'}")
        st.write(f"**Location**: {location}")
        st.write(f"**Reward Amount**: ${reward}")
        st.write(f"**Extra Requirements**: {extras}")
        if due_date:
            st.write(f"**Due Date**: {due_date.strftime('%Y-%m-%d')}")

        # Save, Apply, and Favorite buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if scholarship_id not in st.session_state.saved_scholarships:
                if st.button(f"Save {name}", key=f"save-{scholarship_id}"):
                    st.session_state.saved_scholarships.add(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"saved": True}})
                    st.success(f"Scholarship '{name}' saved!")
            else:
                st.markdown(f"<button class='saved-button'>Saved</button>", unsafe_allow_html=True)

        with col2:
            if scholarship_id not in st.session_state.applied_scholarships:
                if st.button(f"Apply {name}", key=f"apply-{scholarship_id}"):
                    st.session_state.applied_scholarships.add(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"applied": True}})
                    st.success(f"Scholarship '{name}' marked as applied!")
            else:
                st.markdown(f"<button class='applied-button'>Applied</button>", unsafe_allow_html=True)

        with col3:
            if scholarship_id not in st.session_state.favorited_scholarships:
                if st.button(f"Favorite {name}", key=f"favorite-{scholarship_id}"):
                    st.session_state.favorited_scholarships.add(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"favorited": True}})
                    st.success(f"Scholarship '{name}' favorited!")
            else:
                st.markdown(f"<button class='favorited-button'>Favorited</button>", unsafe_allow_html=True)

# Tab 2: Saved Scholarships
with tab2:
    saved_ids = list(st.session_state.saved_scholarships)
    saved_scholarships = scholarships_collection.find({"_id": {"$in": [ObjectId(sid) for sid in saved_ids]}})
    st.write(f"You have saved {len(saved_ids)} scholarships.")
    for scholarship in saved_scholarships:
        name = scholarship.get('name', 'Unnamed Scholarship')
        st.subheader(name)
        st.write(f"**Reward Amount**: ${scholarship.get('reward', 0)}")
        st.write(f"**Due Date**: {scholarship.get('due_date', datetime.now()).strftime('%Y-%m-%d')}")

# The rest of the tabs for applied and favorited scholarships follow the same structure as saved.
