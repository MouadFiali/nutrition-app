"""
Nutrition Planner - Main Application

This is the main entry point for the Nutrition Planner application.
It defines the navigation structure and common elements for all pages.
"""
import streamlit as st
from utils.db_manager import NutritionDB

# Initialize database
db = NutritionDB()

# Custom CSS for consistent styling across pages
CUSTOM_CSS = """
<style>
    /* Main container styling */
    .main > div {
        padding: 2rem 3rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Title styling */
    .stTitle {
        font-size: 2.5rem !important;
        padding-bottom: 1.5rem;
        color: #1f1f1f;
    }
    
    /* Text content styling */
    .stMarkdown {
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* Card styling */
    .stat-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
    }
    
    /* Info box styling */
    .stInfo {
        background-color: #f8f9fa !important;
        padding: 1.5rem !important;
    }
    
    /* Divider styling */
    .stDivider {
        margin: 1.5rem 0;
    }
</style>
"""

# Page configuration
st.set_page_config(
    page_title="Nutrition Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define all pages of the application
# Home page
home_page = st.Page("_pages/home.py", title="Home", icon="🏠")

# Account section
profile_edit_page = st.Page("_pages/account/profile/edit_profile.py", title="Edit Profile", icon="👤")
profile_summary_page = st.Page("_pages/account/profile/profile_summary.py", title="Profile Summary", icon="📊")

# Food section
food_add_page = st.Page("_pages/food/add_food.py", title="Add Food", icon="🍎")
food_manage_page = st.Page("_pages/food/manage_food.py", title="Manage Foods", icon="📋")

# Meals section
meal_create_page = st.Page("_pages/meals/create_meals.py", title="Create Meal", icon="🍽️")
meal_regular_page = st.Page("_pages/meals/regular_meals.py", title="Regular Meals", icon="🥗")
meal_custom_page = st.Page("_pages/meals/custom_meals.py", title="Custom Meals", icon="🎯")

# Programs section
program_view_page = st.Page("_pages/programs/view_programs.py", title="View Programs", icon="📅")
program_create_page = st.Page("_pages/programs/create_program.py", title="Create Program", icon="📝")
program_edit_page = st.Page("_pages/programs/edit_program.py", title="Edit Program", icon="✏️")

# Tracking section
tracking_log_page = st.Page("_pages/tracking/log.py", title="Log Meals", icon="📝")
tracking_progress_page = st.Page("_pages/tracking/progress.py", title="Track Progress", icon="📈")
program_adherence_page  = st.Page("_pages/tracking/program_adherence.py", title="Program Adherence", icon="📊")

# Set up navigation with sections
navigation = st.navigation({
    "Home": [home_page],
    "Account": [profile_edit_page, profile_summary_page],
    "Food Sources": [food_add_page, food_manage_page],
    "Meal Management": [meal_create_page, meal_regular_page, meal_custom_page],
    "Meal Programs": [program_view_page, program_create_page, program_edit_page],
    "Tracking": [tracking_log_page, tracking_progress_page, program_adherence_page ]
})

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Execute selected page
navigation.run()