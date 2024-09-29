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
        mongo_query["title"] = {"$regex": search_query, "$options": "i"}
    if ethnicity_filter != "All":
        mongo_query["preferred_ethnicity"] = ethnicity_filter
    if gender_filter != "All":
        mongo_query["preferred_gender"] = gender_filter
    if first_gen_filter:
        mongo_query["prefers_lgbt"] = True
    if merit_based_filter:
        mongo_query["is_merit_based"] = True
    if lgbtq_filter:
        mongo_query["prefers_lgbt"] = True
    mongo_query["reward"] = {"$gte": min_reward, "$lte": max_reward}

    # Essay filter
    if essay_filter == "Essay":
        mongo_query["extra_requirements"] = {"$regex": "essay", "$options": "i"}
    elif essay_filter == "No Essay":
        mongo_query["extra_requirements"] = {"$not": {"$regex": "essay", "$options": "i"}}

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
# Tab 1: All Scholarships
with tab1:
    st.write(f"Found {len(filtered_scholarships)} scholarships matching your filters and search query.")

    for scholarship in filtered_scholarships:
        scholarship_id = str(scholarship["_id"])

        # Safely access scholarship fields and display only available fields
        if "title" in scholarship:
            st.subheader(scholarship["title"])

        if "description" in scholarship:
            st.write(scholarship["description"])

        if "is_merit_based" in scholarship:
            st.write(f"**Merit-Based**: {'Yes' if scholarship['is_merit_based'] else 'No'}")

        if "preferred_ethnicity" in scholarship:
            st.write(f"**Preferred Ethnicity**: {scholarship['preferred_ethnicity']}")

        if "preferred_gender" in scholarship:
            st.write(f"**Preferred Gender**: {scholarship['preferred_gender']}")

        if "preferred_major" in scholarship:
            st.write(f"**Preferred Major**: {scholarship['preferred_major']}")

        if "prefers_lgbt" in scholarship:
            st.write(f"**Supports LGBTQ+**: {'Yes' if scholarship['prefers_lgbt'] else 'No'}")

        if "location" in scholarship:
            st.write(f"**Location**: {scholarship['location']}")

        # Handle reward amount with conditional logic
        if "reward" in scholarship:
            reward = scholarship['reward']
            if reward == 0:
                st.write("**Reward Amount**: Amount may vary")
            else:
                st.write(f"**Reward Amount**: ${reward}")

        if "is_essay_required" in scholarship:
            st.write(f"**Essay Required**: {'Yes' if scholarship['is_essay_required'] else 'No'}")

        if "extra_requirements" in scholarship:
            st.write(f"**Extra Requirements**: {scholarship['extra_requirements']}")

        if "due_date" in scholarship:
            due_date = scholarship["due_date"]
            st.write(f"**Due Date**: {due_date.strftime('%Y-%m-%d')}")

        # Save, Apply, and Favorite buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if scholarship_id not in st.session_state.saved_scholarships:
                if st.button(f"Save {scholarship['title']}", key=f"save-{scholarship_id}"):
                    st.session_state.saved_scholarships.add(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"saved": True}})
                    st.success(f"Scholarship '{scholarship['title']}' saved!")
            else:
                st.markdown(f"<button class='saved-button'>Saved</button>", unsafe_allow_html=True)

        with col2:
            if scholarship_id not in st.session_state.applied_scholarships:
                if st.button(f"Apply {scholarship['title']}", key=f"apply-{scholarship_id}"):
                    st.session_state.applied_scholarships.add(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"applied": True}})
                    st.success(f"Scholarship '{scholarship['title']}' marked as applied!")
            else:
                st.markdown(f"<button class='applied-button'>Applied</button>", unsafe_allow_html=True)

        with col3:
            if scholarship_id not in st.session_state.favorited_scholarships:
                if st.button(f"Favorite {scholarship['title']}", key=f"favorite-{scholarship_id}"):
                    st.session_state.favorited_scholarships.add(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"favorited": True}})
                    st.success(f"Scholarship '{scholarship['title']}' favorited!")
            else:
                st.markdown(f"<button class='favorited-button'>Favorited</button>", unsafe_allow_html=True)

# Tab 2: Saved Scholarships
with tab2:
    saved_ids = list(st.session_state.saved_scholarships)
    saved_scholarships = scholarships_collection.find({"_id": {"$in": [ObjectId(sid) for sid in saved_ids]}})
    st.write(f"You have saved {len(saved_ids)} scholarships.")

    # Track IDs to be removed after loop finishes
    scholarships_to_remove = []

    for scholarship in saved_scholarships:
        scholarship_id = str(scholarship["_id"])

        if "title" in scholarship:
            st.subheader(scholarship["title"])

        if "description" in scholarship:
            st.write(scholarship["description"])

        if "reward" in scholarship:
            reward = scholarship['reward']
            if reward == 0:
                st.write("**Reward Amount**: Amount may vary")
            else:
                st.write(f"**Reward Amount**: ${reward}")

        if "due_date" in scholarship:
            st.write(f"**Due Date**: {scholarship['due_date'].strftime('%Y-%m-%d')}")

        # Add a Remove button for Saved scholarships
        if st.button(f"Remove {scholarship['title']} from Saved", key=f"remove-saved-{scholarship_id}"):
            scholarships_to_remove.append(scholarship_id)
            st.success(f"Scholarship '{scholarship['title']}' removed from saved!")

    # Remove scholarships from session state and MongoDB after the loop
    for sid in scholarships_to_remove:
        st.session_state.saved_scholarships.remove(sid)
        scholarships_collection.update_one({"_id": ObjectId(sid)}, {"$set": {"saved": False}})


# Tab 3: Applied Scholarships
with tab3:
    applied_ids = list(st.session_state.applied_scholarships)
    applied_scholarships = scholarships_collection.find({"_id": {"$in": [ObjectId(sid) for sid in applied_ids]}})
    st.write(f"You have applied to {len(applied_ids)} scholarships.")

    scholarships_to_remove = []

    for scholarship in applied_scholarships:
        scholarship_id = str(scholarship["_id"])

        if "title" in scholarship:
            st.subheader(scholarship["title"])

        if "description" in scholarship:
            st.write(scholarship["description"])

        if "reward" in scholarship:
            reward = scholarship['reward']
            if reward == 0:
                st.write("**Reward Amount**: Amount may vary")
            else:
                st.write(f"**Reward Amount**: ${reward}")

        if "due_date" in scholarship:
            st.write(f"**Due Date**: {scholarship['due_date'].strftime('%Y-%m-%d')}")

        # Add a Remove button for Applied scholarships
        if st.button(f"Remove {scholarship['title']} from Applied", key=f"remove-applied-{scholarship_id}"):
            scholarships_to_remove.append(scholarship_id)
            st.success(f"Scholarship '{scholarship['title']}' removed from applied!")

    for sid in scholarships_to_remove:
        st.session_state.applied_scholarships.remove(sid)
        scholarships_collection.update_one({"_id": ObjectId(sid)}, {"$set": {"applied": False}})


# Tab 4: Favorited Scholarships
with tab4:
    favorited_ids = list(st.session_state.favorited_scholarships)
    favorited_scholarships = scholarships_collection.find({"_id": {"$in": [ObjectId(sid) for sid in favorited_ids]}})
    st.write(f"You have favorited {len(favorited_ids)} scholarships.")

    scholarships_to_remove = []

    for scholarship in favorited_scholarships:
        scholarship_id = str(scholarship["_id"])

        if "title" in scholarship:
            st.subheader(scholarship["title"])

        if "description" in scholarship:
            st.write(scholarship["description"])

        if "reward" in scholarship:
            reward = scholarship['reward']
            if reward == 0:
                st.write("**Reward Amount**: Amount may vary")
            else:
                st.write(f"**Reward Amount**: ${reward}")

        if "due_date" in scholarship:
            st.write(f"**Due Date**: {scholarship['due_date'].strftime('%Y-%m-%d')}")

        # Add a Remove button for Favorited scholarships
        if st.button(f"Remove {scholarship['title']} from Favorites", key=f"remove-favorite-{scholarship_id}"):
            scholarships_to_remove.append(scholarship_id)
            st.success(f"Scholarship '{scholarship['title']}' removed from favorites!")

    for sid in scholarships_to_remove:
        st.session_state.favorited_scholarships.remove(sid)
        scholarships_collection.update_one({"_id": ObjectId(sid)}, {"$set": {"favorited": False}})
