"""
Edit Program page for the Nutrition Planner application.

This page allows users to edit existing meal programs by adding,
modifying, or removing scheduled meals.
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
    display_days_selection
)

# Initialize database
db = NutritionDB()

# Initialize session state variables
if 'selected_program_id' not in st.session_state:
    st.session_state.selected_program_id = None
if 'edit_meal_time' not in st.session_state:
    st.session_state.edit_meal_time = MealTime.as_list()[0]
if 'edit_meal_name' not in st.session_state:
    st.session_state.edit_meal_name = ""
if 'edit_start_date' not in st.session_state:
    st.session_state.edit_start_date = datetime.now().date()
if 'edit_end_date' not in st.session_state:
    st.session_state.edit_end_date = datetime.now().date()
if 'edit_selected_days' not in st.session_state:
    st.session_state.edit_selected_days = []

def load_meals():
    """Load all meals"""
    meals_df = db.get_all_meals()
    if meals_df.empty:
        return pd.DataFrame()
    return meals_df

def load_program_meals(program_id):
    """Load meals for a specific program"""
    return db.get_program_meals(program_id)

def program_selection_interface():
    """Display interface for selecting a program to edit"""
    # Get all programs
    programs = db.get_all_programs()
    if programs.empty:
        st.info("No meal programs exist yet. Create a program first!")
        return None
    
    # Program selection
    st.subheader("Select Program to Edit")
    selected_program = st.selectbox(
        "Choose a program",
        programs['name'].tolist(),
        index=programs.index[programs['id'] == st.session_state.selected_program_id].tolist()[0] if st.session_state.selected_program_id and st.session_state.selected_program_id in programs['id'].values else 0,
        key="edit_program_selector"
    )
    
    # Get program data
    program_data = programs[programs['name'] == selected_program].iloc[0]
    st.session_state.selected_program_id = program_data['id']
    
    return program_data

def meal_assignment_interface(program_data):
    """Display interface for assigning meals to an existing program without forms"""
    # Calculate date range
    start_date = pd.to_datetime(program_data['start_date']).date()
    end_date = pd.to_datetime(program_data['end_date']).date()
    
    # Initialize date values if needed
    if st.session_state.edit_start_date < start_date or st.session_state.edit_start_date > end_date:
        st.session_state.edit_start_date = start_date
    if st.session_state.edit_end_date < start_date or st.session_state.edit_end_date > end_date:
        st.session_state.edit_end_date = start_date
    
    # Display program dates
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
    st.subheader("🗓️ Add or Replace Meals")
    
    # Create the meal time to category mapping
    meal_categories = {
        meal_time: MealTime.get_category(meal_time)
        for meal_time in MealTime.as_list()
    }
    
    # Meal selection
    col1, col2 = st.columns(2, vertical_alignment="bottom")
    
    with col1:
        meal_time = st.selectbox(
            "Meal Time", 
            list(meal_categories.keys()),
            index=MealTime.as_list().index(st.session_state.edit_meal_time) if st.session_state.edit_meal_time in MealTime.as_list() else 0,
            key="edit_meal_time_selector"
        )
        st.session_state.edit_meal_time = meal_time
    
    # Filter meals by appropriate category
    category = meal_categories[meal_time]
    available_meals = meals_df[meals_df['category'] == category]
    
    with col2:
        if not available_meals.empty:
            # Check if previous selection is in available meals
            default_index = 0
            if st.session_state.edit_meal_name in available_meals['name'].values:
                default_index = available_meals['name'].tolist().index(st.session_state.edit_meal_name)
            
            meal = st.selectbox(
                "Select Meal", 
                available_meals['name'].tolist(),
                index=default_index,
                key="edit_meal_selector"
            )
            st.session_state.edit_meal_name = meal
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
        edit_start = st.date_input(
            "From Date",
            min_value=start_date,
            max_value=end_date,
            value=st.session_state.edit_start_date,
            key="edit_start_date_selector"
        )
        st.session_state.edit_start_date = edit_start
    
    with col2:
        edit_end = st.date_input(
            "To Date",
            min_value=start_date,
            max_value=end_date,
            value=st.session_state.edit_end_date,
            key="edit_end_date_selector"
        )
        st.session_state.edit_end_date = edit_end
    
    # Make sure dates are in order
    if edit_end < edit_start:
        st.session_state.edit_end_date = edit_start
        edit_end = edit_start
    
    # Days selection
    st.divider()
    st.subheader("📅 Select Days of the Week")
    selected_days = display_days_selection("edit_")
    st.session_state.edit_selected_days = selected_days
    
    # Update button
    if st.button("Update Meals", type="primary", disabled=not (meal and selected_days), key="update_meals_button"):
        meal_id = available_meals[available_meals['name'] == meal].iloc[0]['id']
        dates = pd.date_range(edit_start, edit_end)
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
            set_success_message(f"Updated meals for {updated_count} dates!")
            st.rerun()
        else:
            set_error_message("No meals were updated. Please check your selection.")
            st.rerun()

def main():
    """Main function for the Edit Program page"""
    st.title("✏️ Edit Meal Program")
    
    # Display any success/error messages
    display_success_error()
    
    # Select program to edit
    program_data = program_selection_interface()
    
    if program_data is not None:
        st.divider()
        
        # Display meal assignment interface
        meal_assignment_interface(program_data)
        
        # Display helpful tips
        with st.expander("💡 Program Editing Tips"):
            st.markdown("""
            ### Efficient Program Editing
            
            1. **Bulk Updates**: Use the date range and weekday selectors to quickly add the same meal to multiple days.
            
            2. **Replace Meals**: To replace a meal, simply add a new meal for the same meal time - it will replace the existing one.
            
            3. **Remove Meals**: Use the 🗑️ button next to each meal in the calendar to remove it.
            
            4. **Planning Ahead**: Consider your nutritional goals when planning each day, aiming for balanced macros.
            
            5. **Create Templates**: Set up a pattern for weekdays vs weekends to make meal planning easier.
            
            ### Using This Page
            
            - Use the top section to add or replace meals in your program
            - The calendar below shows all currently scheduled meals
            - You can add the same meal to multiple days at once
            - To completely replace a program, delete it and create a new one
            """)

# Run the main function when this page is loaded
main()