"""
Create Program page for the Nutrition Planner application.

This page allows users to create new meal programs.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.db_manager import NutritionDB
from utils.constants import MealTime, MealCategory
from utils.ui import (
    display_success_error,
    set_success_message,
    set_error_message,
    get_meal_selection,
    display_days_selection
)

# Initialize database
db = NutritionDB()

# Initialize session state variables
if 'program_name' not in st.session_state:
    st.session_state.program_name = ""
if 'program_start_date' not in st.session_state:
    st.session_state.program_start_date = datetime.now().date()
if 'program_duration' not in st.session_state:
    st.session_state.program_duration = 7
if 'current_program_id' not in st.session_state:
    st.session_state.current_program_id = None
if 'create_program_tab' not in st.session_state:
    st.session_state.create_program_tab = "details"  # "details" or "assign"

def load_meals():
    """Load all meals"""
    meals_df = db.get_all_meals()
    if meals_df.empty:
        return pd.DataFrame()
    return meals_df

def create_program_interface():
    """Display interface for creating a new program without forms"""
    st.subheader("📝 Create New Program")
    
    # Program details
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        program_name = st.text_input(
            "Program Name", 
            value=st.session_state.program_name,
            placeholder="e.g., Weekly Cutting Plan",
            key="program_name_input"
        )
        st.session_state.program_name = program_name
    
    with col2:
        start_date = st.date_input(
            "Start Date",
            value=st.session_state.program_start_date,
            key="program_start_date_input"
        )
        st.session_state.program_start_date = start_date
    
    with col3:
        duration = st.number_input(
            "Duration (days)", 
            min_value=1, 
            max_value=90, 
            value=st.session_state.program_duration,
            key="program_duration_input"
        )
        st.session_state.program_duration = duration
    
    # Calculate end date
    end_date = start_date + timedelta(days=duration-1)
    
    # Create program button
    if st.button("Create Program", type="primary", disabled=not program_name, key="create_program_button"):
        program_id = db.save_meal_program(program_name, start_date, end_date)
        if program_id:
            st.session_state.current_program_id = program_id
            st.session_state.create_program_tab = "assign"
            set_success_message("Program created! Now you can assign meals.")
            st.rerun()
        else:
            set_error_message("Failed to create program!")
            st.rerun()

def meal_assignment_interface():
    """Display interface for assigning meals to the new program without forms"""
    # Make sure we have a current program
    if 'current_program_id' not in st.session_state or not st.session_state.current_program_id:
        st.info("No active program. Please create a program first.")
        return
    
    # Load all programs to get current program info
    programs = db.get_all_programs()
    program_data = programs[programs['id'] == st.session_state.current_program_id].iloc[0]
    
    # Display program info
    st.subheader(f"🍽️ Assign Meals to: {program_data['name']}")
    
    # Calculate date range
    start_date = pd.to_datetime(program_data['start_date']).date()
    end_date = pd.to_datetime(program_data['end_date']).date()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Start Date", start_date.strftime("%d-%m-%Y"))
    with col2:
        st.metric("End Date", end_date.strftime("%d-%m-%Y"))
    
    # Load meals
    meals_df = load_meals()
    if meals_df.empty:
        st.warning("No meals available. Please create some meals first!")
        return
    
    st.divider()
    st.subheader("📆 Add Meals to Program")
    
    # Initialize session state variables for meal assignment
    if 'assign_meal_time' not in st.session_state:
        st.session_state.assign_meal_time = MealTime.as_list()[0]
    if 'assign_meal_name' not in st.session_state:
        st.session_state.assign_meal_name = ""
    if 'assign_start_date' not in st.session_state:
        st.session_state.assign_start_date = start_date
    if 'assign_end_date' not in st.session_state:
        st.session_state.assign_end_date = start_date
    if 'assign_days' not in st.session_state:
        st.session_state.assign_days = []
    
    # Create the meal time to category mapping
    meal_categories = {
        meal_time: MealTime.get_category(meal_time)
        for meal_time in MealTime.as_list()
    }
    
    # Meal selection
    col1, col2 = st.columns(2)
    
    with col1:
        meal_time = st.selectbox(
            "Meal Time", 
            list(meal_categories.keys()),
            index=MealTime.as_list().index(st.session_state.assign_meal_time) if st.session_state.assign_meal_time in MealTime.as_list() else 0,
            key="assign_meal_time_input"
        )
        st.session_state.assign_meal_time = meal_time
    
    # Filter meals by category
    category = meal_categories[meal_time]
    available_meals = meals_df[meals_df['category'] == category]
    
    with col2:
        if not available_meals.empty:
            meal = st.selectbox(
                "Select Meal", 
                available_meals['name'].tolist(),
                index=available_meals['name'].tolist().index(st.session_state.assign_meal_name) if st.session_state.assign_meal_name in available_meals['name'].tolist() else 0,
                key="assign_meal_input"
            )
            st.session_state.assign_meal_name = meal
        else:
            st.warning(f"No meals available for category: {category}")
            meal = None
    
    if meal is None:
        return
    
    # Date range selection
    st.divider()
    st.subheader("📅 Select Date Range")
    
    col1, col2 = st.columns(2)
    with col1:
        assign_start = st.date_input(
            "From Date",
            min_value=start_date,
            max_value=end_date,
            value=st.session_state.assign_start_date,
            key="assign_start_date_input"
        )
        st.session_state.assign_start_date = assign_start
    
    with col2:
        assign_end = st.date_input(
            "To Date",
            min_value=start_date,
            max_value=end_date,
            value=st.session_state.assign_end_date,
            key="assign_end_date_input"
        )
        st.session_state.assign_end_date = assign_end
    
    # Correct date order
    if assign_end < assign_start:
        assign_end = assign_start
        st.session_state.assign_end_date = assign_end
    
    # Days selection
    st.divider()
    st.subheader("📅 Select Days of the Week")
    
    # Get selected days
    selected_days = display_days_selection("assign_")
    st.session_state.assign_days = selected_days
    
    # Add meals button
    if st.button("Add Meals to Program", type="primary", disabled=not (meal and selected_days), key="assign_meals_button"):
        meal_id = available_meals[available_meals['name'] == meal].iloc[0]['id']
        dates = pd.date_range(assign_start, assign_end)
        updated_count = 0
        
        for date in dates:
            if date.weekday() in selected_days:
                if db.update_program_meal(
                    int(program_data['id']),
                    int(meal_id),
                    date.strftime('%Y-%m-%d'),
                    meal_time
                ):
                    updated_count += 1
        
        if updated_count > 0:
            set_success_message(f"Added {meal} for {meal_time} to {updated_count} days!")
            st.rerun()
        else:
            set_error_message("No meals were added. Please check your selection.")
            st.rerun()

def main():
    """Main function for the Create Program page"""
    st.title("📝 Create Meal Program")
    
    # Display any success/error messages
    display_success_error()
    
    # Choose appropriate interface based on state
    if st.session_state.create_program_tab == "details" or not st.session_state.current_program_id:
        # Show program creation interface
        create_program_interface()
        
        # If a program exists, show a button to switch to meal assignment
        if st.session_state.current_program_id:
            st.divider()
            if st.button("➡️ Proceed to Meal Assignment", use_container_width=True):
                st.session_state.create_program_tab = "assign"
                st.rerun()
    else:
        # Show tabs to switch between interfaces
        tab1, tab2 = st.tabs(["Program Details", "Assign Meals"])
        
        with tab1:
            create_program_interface()
            
            # Button to reset current program
            if st.button("✨ Create Another Program", use_container_width=True):
                st.session_state.current_program_id = None
                st.session_state.create_program_tab = "details"
                st.session_state.program_name = ""
                st.rerun()
        
        with tab2:
            meal_assignment_interface()
    
    # Show helpful information
    with st.expander("💡 Program Creation Tips"):
        st.markdown("""
        ### Creating Effective Meal Programs
        
        1. **Plan Ahead**: Create a program a few days before you want to start it so you have time to shop for ingredients.
        
        2. **Be Realistic**: Don't schedule meals that are too complex for busy days.
        
        3. **Variety is Key**: Include different meals across the week to prevent boredom and ensure nutritional diversity.
        
        4. **Batch Cook**: Schedule similar meals on consecutive days to make batch cooking easier.
        
        5. **Balance Your Macros**: Ensure each day has a good balance of proteins, carbs, and fats according to your goals.
        
        ### Using This Page
        
        - First, create a program by giving it a name, start date, and duration
        - Then, assign meals to specific days and meal times
        - You can apply meals to multiple days at once by selecting a date range and days of the week
        - To create a new program, click "Create Another Program"
        """)

# Run the main function when this page is loaded
main()