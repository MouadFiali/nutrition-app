"""
Meal Tracking Log page for the Nutrition App.

This page allows users to log meals they've eaten and add optional notes.
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from utils.db_manager import NutritionDB
from utils.constants import MealTime
from utils.nutrition import (
    calculate_meal_macros_from_record, 
    calculate_all_metrics, 
    calculate_macro_targets
)
from utils.ui import (
    display_success_error,
    set_success_message,
    set_error_message,
    display_macros_summary
)

# Initialize database
db = NutritionDB()

def load_profile_and_targets():
    """Load profile and calculate targets without caching"""
    profile = db.load_profile()
    if not profile:
        return None, None, None, None, None
    
    # Calculate metrics
    bmr, tdee, target_calories = calculate_all_metrics(
        profile[1], profile[2], profile[3], profile[5],
        profile[4], profile[6], profile[7]
    )
    
    # Calculate macro targets
    macros = calculate_macro_targets(profile[1], target_calories)
    
    return profile, target_calories, macros['protein'], macros['carbs'], macros['fats']

def load_meals():
    """Load all meals"""
    meals_df = db.get_all_meals()
    if meals_df.empty:
        return pd.DataFrame()
    return meals_df

def load_tracked_meals(date):
    """Load tracked meals for a specific date"""
    return db.get_tracked_meals(date)

def calculate_daily_totals(tracked_meals):
    """Calculate total macros from tracked meals"""
    if tracked_meals.empty:
        return {
            'calories': 0,
            'proteins': 0,
            'carbs': 0,
            'fats': 0
        }
    
    total_calories = 0
    total_proteins = 0
    total_carbs = 0
    total_fats = 0
    
    for _, meal in tracked_meals.iterrows():
        if meal['type'] == 'custom':
            total_calories += meal['calories']
            total_proteins += meal['proteins']
            total_carbs += meal['carbs']
            total_fats += meal['fats']
        elif meal['type'] == 'regular' and 'foods' in meal and meal['foods']:
            macros = calculate_meal_macros_from_record(meal)
            total_calories += macros['calories']
            total_proteins += macros['proteins']
            total_carbs += macros['carbs']
            total_fats += macros['fats']
    
    return {
        'calories': round(total_calories, 1),
        'proteins': round(total_proteins, 1),
        'carbs': round(total_carbs, 1),
        'fats': round(total_fats, 1)
    }

def track_meal_form(tracking_date, meals_df):
    """Display form for tracking a new meal"""
    with st.form("track_meal_form"):
        st.subheader("🍽️ Log a Meal")
        
        # Meal selection
        if meals_df.empty:
            st.warning("No meals available to track. Please create some meals first.")
            st.form_submit_button("Track Meal", disabled=True)
            return
        
        col1, col2 = st.columns([2, 1])
        with col1:
            meal = st.selectbox(
                "Select meal", 
                meals_df['name'].tolist(),
                help="Choose the meal you've eaten"
            )
        with col2:
            meal_time = st.selectbox(
                "Meal time",
                MealTime.as_list(),
                help="When you ate this meal"
            )
        
        notes = st.text_area(
            "Notes (optional)",
            placeholder="e.g., Added extra salad, Felt good after eating, etc.",
            help="Add any notes about this meal or how you felt"
        )
        
        # Submit button
        submitted = st.form_submit_button("Track Meal", type="primary", use_container_width=True)
        
        if submitted:
            meal_id = meals_df[meals_df['name'] == meal].iloc[0]['id']
            if db.track_meal(
                tracking_date,
                meal_id,
                meal_time,
                datetime.now(),
                notes
            ):
                set_success_message("Meal tracked successfully!")
                st.rerun()
            else:
                set_error_message("Failed to track meal!")
                st.rerun()

def display_daily_summary(tracked_meals, target_calories, protein_target, carbs_target, fats_target):
    """Display summary of tracked meals and daily targets"""
    if tracked_meals.empty:
        st.info("No meals tracked for this day yet.")
        return
    
    st.subheader("📊 Daily Nutrition Summary")
    
    # Calculate totals
    totals = calculate_daily_totals(tracked_meals)
    
    # Display macros summary
    display_macros_summary(
        totals,
        target_calories,
        protein_target,
        carbs_target,
        fats_target,
        show_progress=True
    )

def display_tracked_meals(tracked_meals, tracking_date):
    """Display tracked meals for the selected date"""
    if tracked_meals.empty:
        return
    
    st.subheader("🍽️ Tracked Meals")
    
    # Sort meals by actual time
    sorted_meals = tracked_meals.sort_values(by='actual_time')
    
    for _, meal in sorted_meals.iterrows():
        # Create a container for each meal
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"{meal['meal_name']}")
                st.caption(f"{meal['meal_time']} | Logged at: {pd.to_datetime(meal['actual_time']).strftime('%H:%M')}")
                
                # Display macros
                if meal['type'] == 'custom':
                    macros_text = (
                        f"**Calories:** {meal['calories']:.0f} kcal | "
                        f"**Protein:** {meal['proteins']:.1f}g | "
                        f"**Carbs:** {meal['carbs']:.1f}g | "
                        f"**Fat:** {meal['fats']:.1f}g"
                    )
                    st.markdown(macros_text)
                elif meal['type'] == 'regular' and 'foods' in meal and meal['foods']:
                    macros = calculate_meal_macros_from_record(meal)
                    macros_text = (
                        f"**Calories:** {macros['calories']:.0f} kcal | "
                        f"**Protein:** {macros['proteins']:.1f}g | "
                        f"**Carbs:** {macros['carbs']:.1f}g | "
                        f"**Fat:** {macros['fats']:.1f}g"
                    )
                    st.markdown(macros_text)
                
                # Display notes if any
                if meal['notes']:
                    st.info(f"Notes: {meal['notes']}")
            
            # Delete button
            with col2:
                if st.button("🗑️", key=f"delete_{meal['id']}"):
                    # Option to delete the meal tracking entry
                    if db.delete_tracked_meal(meal['id']):
                        set_success_message(f"Removed {meal['meal_name']} from tracking")
                    else:
                        set_error_message(f"Failed to remove {meal['meal_name']} from tracking")
                    st.rerun()

def main():
    """Main function for the Meal Tracking page"""
    st.title("📝 Track Meals")
    
    # Display any success/error messages
    display_success_error()
    
    # Load profile and targets
    profile_targets = load_profile_and_targets()
    
    if not profile_targets[0]:
        st.warning("Please set up your profile first!")
        return
    
    # Unpack targets
    _, target_calories, protein_target, carbs_target, fats_target = profile_targets
    
    # Date selection (defaults to today)
    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        tracking_date = st.date_input(
            "📅 Select Date", 
            datetime.now().date(),
            help="The date you want to track meals for"
        )
    
    with col2:
        # Option to view program meals for this date
        if st.button("View Meal Programs", use_container_width=True):
            # Redirect to the program view page
            st.switch_page("_pages/programs/view_programs.py")
    
    # Load meals and tracked meals
    meals_df = load_meals()
    tracked_meals = load_tracked_meals(tracking_date)
    
    # Display daily summary
    if not tracked_meals.empty:
        display_daily_summary(tracked_meals, target_calories, protein_target, carbs_target, fats_target)
    
    # Display form for tracking a new meal
    st.divider()
    track_meal_form(tracking_date, meals_df)
    
    # Display tracked meals
    st.divider()
    display_tracked_meals(tracked_meals, tracking_date)
    
    # Show helpful information
    with st.expander("💡 Meal Tracking Tips"):
        st.markdown("""
        ### Benefits of Tracking Your Meals
        
        1. **Awareness**: Tracking helps you become aware of what and how much you're eating.
        
        2. **Accountability**: It helps you stay accountable to your nutrition goals.
        
        3. **Pattern Recognition**: Over time, you can identify eating patterns and make adjustments.
        
        4. **Progress Monitoring**: Track how your food choices affect your progress toward your goals.
        
        ### Best Practices
        
        - **Be Consistent**: Try to track all your meals, not just some of them.
        
        - **Add Notes**: Use the notes field to record how you felt after eating, hunger levels, etc.
        
        - **Track in Real-Time**: Log meals as soon as possible after eating for better accuracy.
        
        - **Use Pre-Planned Meals**: Create meal programs to make tracking easier.
        """)

main()