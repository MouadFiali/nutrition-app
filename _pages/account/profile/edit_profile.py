"""
Profile edit page for the Nutrition Planner application.

This page allows users to create or update their profile information,
including personal details and nutritional goals.
"""
import streamlit as st
from utils.db_manager import NutritionDB
from utils.constants import ActivityLevel, GoalType
from utils.ui import display_success_error, set_success_message

# Initialize database
db = NutritionDB()

def profile_input_form(profile):
    """Handle profile input form with validation and submission."""
    with st.form("profile_form", clear_on_submit=True):
        st.subheader("📝 Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input(
                "Weight (kg)",
                min_value=30.0,
                max_value=250.0,
                value=profile[1] if profile else 70.0,
                help="Your current weight in kilograms"
            )
            height = st.number_input(
                "Height (m)",
                min_value=1.0,
                max_value=2.5,
                value=profile[2] if profile else 1.70,
                help="Your height in meters"
            )
            age = st.number_input(
                "Age (years)",
                min_value=15,
                max_value=100,
                value=profile[3] if profile else 25,
                help="Your current age in years"
            )
        
        with col2:
            gender = st.radio(
                "Gender",
                ["Male", "Female"],
                index=0 if not profile or profile[5] == "Male" else 1,
                help="Your biological gender (used for BMR calculation)"
            )
            activity_level = st.select_slider(
                "Activity Level",
                options=ActivityLevel.as_list(),
                value=profile[4] if profile else ActivityLevel.LIGHTLY_ACTIVE.value,
                help="Select your typical daily activity level"
            )
        
        st.divider()
        st.subheader("🎯 Goal Setting")
        
        goal_types = GoalType.as_list()
        goal_type = st.radio(
            "Goal Type",
            goal_types,
            index=goal_types.index(profile[6]) if profile and profile[6] in goal_types else 0,
            horizontal=True,
            help="Select your nutritional goal"
        )
        
        goal_percentage = 0
        if goal_type != GoalType.MAINTENANCE.value:
            label = "Deficit" if goal_type == GoalType.WEIGHT_LOSS.value else "Surplus"
            goal_percentage = st.slider(
                f"{label} Percentage (%)",
                min_value=5,
                max_value=30,
                value=int(profile[7]) if profile and profile[7] else 20,
                help=f"Percentage {label.lower()} from your maintenance calories"
            )
        
        submit = st.form_submit_button("Save Profile", use_container_width=True)
        if submit:
            db.save_profile(
                weight, height, age, activity_level, gender,
                goal_type, goal_percentage
            )
            set_success_message("Profile saved successfully!")
            st.rerun()

def main():
    """Main function for the Profile Edit page."""
    st.title("👤 Edit Profile")
    
    # Display any success/error messages
    display_success_error()
    
    # Load existing profile 
    profile = db.load_profile()
    
    if profile:
        st.info("Your profile data is already set up. You can update it below.")
    else:
        st.info("Welcome! Please set up your profile to get started with meal planning.")
    
    # Display the profile input form
    profile_input_form(profile)
    
    # Add helpful tips at the bottom
    with st.expander("Tips for accurate calculations"):
        st.markdown("""
        - **Weight & Height**: Enter your current measurements for the most accurate calculations.
        - **Activity Level**:
            - **Sedentary**: Little or no exercise, desk job
            - **Lightly Active**: Light exercise 1-3 days/week
            - **Very Active**: Moderate exercise 3-5 days/week
            - **Extremely Active**: Heavy exercise 6-7 days/week
        - **Goal Setting**: A moderate deficit of 15-20% is generally recommended for sustainable weight loss.
        """)

main()