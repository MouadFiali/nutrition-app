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
    display_days_selection,
    get_flexible_meal_selection
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
if 'filter_by_meal_time' not in st.session_state:
    st.session_state.filter_by_meal_time = True

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
    
    # Meal selection
    col1, col2 = st.columns(2)
    
    with col1:
        meal_time = st.selectbox(
            "Meal Time", 
            MealTime.as_list(),
            index=MealTime.as_list().index(st.session_state.assign_meal_time) if st.session_state.assign_meal_time in MealTime.as_list() else 0,
            key="assign_meal_time_input"
        )
        st.session_state.assign_meal_time = meal_time
    
    with col2:
        filter_by_meal_time = st.checkbox(
            "Filter by meal time",
            value=st.session_state.filter_by_meal_time,
            help="When checked, only meals compatible with the selected meal time will be shown",
            key="filter_by_meal_time_input"
        )
        st.session_state.filter_by_meal_time = filter_by_meal_time
    
    # Use the new flexible meal selection function
    meal, available_meals = get_flexible_meal_selection(
        meals_df,
        meal_time,
        filter_by_meal_time,
        key_prefix="assign_"
    )
    
    if meal is None:
        return
    
    st.session_state.assign_meal_name = meal
    
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
        
        4. **Using the Lunch/Dinner Category**: Meals categorized as "Lunch/Dinner" can be assigned to either lunch or dinner time slots.
        
        5. **Flexible Filtering**: You can uncheck "Filter by meal time" to see all available meals regardless of their category.
        
        6. **Batch Cook**: Schedule similar meals on consecutive days to make batch cooking easier.
        
        7. **Balance Your Macros**: Ensure each day has a good balance of proteins, carbs, and fats according to your goals.
        """)

# Run the main function when this page is loaded
main()