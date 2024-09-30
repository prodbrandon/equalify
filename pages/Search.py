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
st.title('''🔎 :rainbow[Equalify Search]''')

# Initialize session state for saved, applied, and favorited scholarships
if 'saved_scholarships' not in st.session_state:
    st.session_state.saved_scholarships = set()
if 'applied_scholarships' not in st.session_state:
    st.session_state.applied_scholarships = set()
if 'favorited_scholarships' not in st.session_state:
    st.session_state.favorited_scholarships = set()

# Pagination settings
page_size = 5  # Number of scholarships to display per page
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1
def change_page(change):
    st.session_state.page_number += change


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
    major_filter = st.text_input("Preferred Major", "")
    min_reward = st.number_input("Minimum Reward Amount ($)", min_value=0, value=0)
    max_reward = st.number_input("Maximum Reward Amount ($)", min_value=0, value=1000000)

    # Checkboxes for additional filters
    lgbtq_filter = st.checkbox("Supports LGBTQ+", value=False)
    merit_based_filter = st.checkbox("Merit-Based", value=False)
    essay_required_filter = st.checkbox("Essay Required", value=False)
    women_in_stem_filter = st.checkbox("Women in STEM", value=False)
    disabilities_filter = st.checkbox("Supports Disabilities", value=False)
    rural_filter = st.checkbox("Rural Student", value=False)
    immigrant_or_refugee_filter = st.checkbox("Immigrant or Refugee", value=False)
    neurodiversity_filter = st.checkbox("Supports Neurodiversity", value=False)
    low_income_filter = st.checkbox("Low Income", value=False)
    first_gen_filter = st.checkbox("First Generation College Student", value=False)


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
    if major_filter:
        mongo_query["preferred_major"] = {"$regex": major_filter, "$options": "i"}
    if lgbtq_filter:
        mongo_query["prefers_lgbt"] = True
    if merit_based_filter:
        mongo_query["is_merit_based"] = True
    if essay_required_filter:
        mongo_query["is_essay_required"] = True
    if women_in_stem_filter:
        mongo_query["women_in_stem"] = True
    if disabilities_filter:
        mongo_query["disabilities"] = True
    if rural_filter:
        mongo_query["rural"] = True
    if immigrant_or_refugee_filter:
        mongo_query["immigrant_or_refugee"] = True
    if neurodiversity_filter:
        mongo_query["neurodiversity"] = True
    if low_income_filter:
        mongo_query["low_income"] = True
    if first_gen_filter:
        mongo_query["first_generation"] = True

    mongo_query["reward"] = {"$gte": min_reward, "$lte": max_reward}

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

# Pagination calculations
total_scholarships = len(filtered_scholarships)
total_pages = (total_scholarships // page_size) + (1 if total_scholarships % page_size > 0 else 0)

# Determine scholarships for the current page
start_idx = (st.session_state.page_number - 1) * page_size
end_idx = start_idx + page_size
current_page_scholarships = filtered_scholarships[start_idx:end_idx]

# Function to display scholarships with buttons
def display_scholarship_list(scholarships, tab_prefix):
    for scholarship in scholarships:
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

        if "extra_requirements" in scholarship:
            st.write(f"**Extra Requirements**: {scholarship['extra_requirements']}")

        if "due_date" in scholarship:
            due_date = scholarship["due_date"]
            st.write(f"**Due Date**: {due_date.strftime('%Y-%m-%d')}")

        # Save, Apply, Favorite, and Remove buttons with unique keys per tab
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if scholarship_id not in st.session_state.saved_scholarships:
                if st.button(f"Save {scholarship['title']}", key=f"{tab_prefix}-save-{scholarship_id}"):
                    st.session_state.saved_scholarships.add(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"saved": True}})
                    st.success(f"Scholarship '{scholarship['title']}' saved!")
            else:
                st.markdown(f"<button class='saved-button'>Saved</button>", unsafe_allow_html=True)

        with col2:
            if scholarship_id not in st.session_state.applied_scholarships:
                if st.button(f"Mark {scholarship['title']} as applied", key=f"{tab_prefix}-apply-{scholarship_id}"):
                    st.session_state.applied_scholarships.add(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"applied": True}})
                    st.success(f"Scholarship '{scholarship['title']}' marked as applied!")
            else:
                st.markdown(f"<button class='applied-button'>Applied</button>", unsafe_allow_html=True)

        with col3:
            if scholarship_id not in st.session_state.favorited_scholarships:
                if st.button(f"Favorite {scholarship['title']}", key=f"{tab_prefix}-favorite-{scholarship_id}"):
                    st.session_state.favorited_scholarships.add(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"favorited": True}})
                    st.success(f"Scholarship '{scholarship['title']}' favorited!")
            else:
                st.markdown(f"<button class='favorited-button'>Favorited</button>", unsafe_allow_html=True)

        # Remove button for saved, applied, or favorited
        with col4:
            if tab_prefix == "saved":
                if st.button(f"Remove from Saved", key=f"{tab_prefix}-remove-{scholarship_id}"):
                    st.session_state.saved_scholarships.remove(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"saved": False}})
                    st.success(f"Scholarship '{scholarship['title']}' removed from saved!")
            elif tab_prefix == "applied":
                if st.button(f"Remove from Applied", key=f"{tab_prefix}-remove-{scholarship_id}"):
                    st.session_state.applied_scholarships.remove(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"applied": False}})
                    st.success(f"Scholarship '{scholarship['title']}' removed from applied!")
            elif tab_prefix == "favorited":
                if st.button(f"Remove from Favorites", key=f"{tab_prefix}-remove-{scholarship_id}"):
                    st.session_state.favorited_scholarships.remove(scholarship_id)
                    scholarships_collection.update_one({"_id": ObjectId(scholarship_id)}, {"$set": {"favorited": False}})
                    st.success(f"Scholarship '{scholarship['title']}' removed from favorites!")

        # Add a horizontal line to separate scholarships
        st.markdown("---")


# Tabs for viewing all scholarships, saved, applied, and favorited
tab1, tab2, tab3, tab4 = st.tabs(
    ["All Scholarships", "Saved Scholarships", "Applied Scholarships", "Favorited Scholarships"])

# Tab 1: All Scholarships
with tab1:
    st.write(f"Found {total_scholarships} scholarships matching your filters and search query.")
    display_scholarship_list(current_page_scholarships, tab_prefix="all")

    # Pagination controls
    col_prev, col_page, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.session_state.page_number > 1:
            st.button("Previous", on_click=change_page, args=(-1,))

    with col_page:
        st.write(f"Page {st.session_state.page_number} of {total_pages}")

    with col_next:
        if st.session_state.page_number < total_pages:
            st.button("Next", on_click=change_page, args=(1,))

# Tab 2: Saved Scholarships
with tab2:
    saved_ids = list(st.session_state.saved_scholarships)
    saved_scholarships = scholarships_collection.find({"_id": {"$in": [ObjectId(sid) for sid in saved_ids]}})
    st.write(f"You have saved {len(saved_ids)} scholarships.")
    display_scholarship_list(saved_scholarships, tab_prefix="saved")

    # Track IDs to be removed after loop finishes
    scholarships_to_remove = []
    for scholarship in saved_scholarships:
        scholarship_id = str(scholarship["_id"])
        if "title" in scholarship:
            st.subheader(scholarship["title"])
        # Add a horizontal line to separate scholarships
        st.markdown("---")

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
    display_scholarship_list(applied_scholarships, tab_prefix="applied")

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
    display_scholarship_list(favorited_scholarships, tab_prefix="favorited")

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

