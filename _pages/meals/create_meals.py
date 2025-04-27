"""
Create Meal page for the Nutrition Planner application.

This page allows users to create new regular or custom meals.
"""
import streamlit as st
from utils.db_manager import NutritionDB
from utils.constants import MealCategory
from utils.nutrition import calculate_meal_macros, calculate_all_metrics, calculate_macro_targets
from utils.ui import (
    display_success_error, 
    set_success_message, 
    set_error_message,
    create_food_slot, 
    display_macros_summary
)

# Initialize database
db = NutritionDB()

# Initialize session state variables
if 'food_slots' not in st.session_state:
    st.session_state.food_slots = 3

def add_food_slot():
    """Add a new food slot"""
    st.session_state.food_slots += 1
    st.rerun()

def remove_food_slot(prefix=""):
    """Remove a food slot if more than 2 remain"""
    if st.session_state.food_slots > 2:
        st.session_state.food_slots -= 1
        st.rerun()

def load_food_sources():
    """Load food sources without caching"""
    return db.load_food_sources()

def load_profile_and_targets():
    """Load profile and calculate targets without caching"""
    profile = db.load_profile()
    if not profile:
        return None, None, None, None, None
    
    # Calculate all metrics
    bmr, tdee, target_calories = calculate_all_metrics(
        profile[1], profile[2], profile[3], profile[5],
        profile[4], profile[6], profile[7]
    )
    
    # Calculate macro targets
    macros = calculate_macro_targets(profile[1], target_calories)
    
    return profile, target_calories, macros['protein'], macros['carbs'], macros['fats']

def create_regular_meal(foods_df, profile_targets):
    """Interface for creating a regular meal"""
    if foods_df.empty:
        st.warning("Please add some food sources first in the Food Sources section!")
        return
    
    _, target_calories, protein_target, carbs_target, fats_target = profile_targets
    
    col1, col2 = st.columns([2, 1])
    with col1:
        meal_name = st.text_input("Meal Name", placeholder="e.g., High Protein Breakfast")
    with col2:
        category = st.selectbox("Category", MealCategory.as_list())
    
    st.divider()
    st.subheader("🍽️ Select Foods and Quantities")
    
    quantities = {}
    # Use the UI utility function to create food slots
    for i in range(st.session_state.food_slots):
        food_name, data = create_food_slot(
            i, 
            foods_df, 
            quantities,
            can_remove=st.session_state.food_slots > 2,
            remove_callback=remove_food_slot
        )
        if food_name and data:
            quantities[food_name] = data

    if st.button("➕ Add Another Food"):
        add_food_slot()
    
    if quantities:
        st.divider()
        st.subheader("📊 Meal Summary")
        # Calculate macros
        macros = calculate_meal_macros(foods_df, quantities)
        # Display macros summary
        display_macros_summary(
            macros,
            target_calories, 
            protein_target, 
            carbs_target, 
            fats_target
        )
        
        if st.button("💾 Save Meal", disabled=not (meal_name and quantities), type="primary"):
            if db.save_meal(meal_name, category, "regular", quantities, macros):
                st.session_state.food_slots = 3  # Reset slots
                set_success_message(f"Meal '{meal_name}' saved successfully!")
                st.rerun()
            else:
                set_error_message("A meal with this name already exists")
                st.rerun()
    else:
        st.info("Select foods and quantities to see meal summary")

def create_custom_meal(profile_targets):
    """Interface for creating a custom meal"""
    _, target_calories, protein_target, carbs_target, fats_target = profile_targets
    
    col1, col2 = st.columns([2, 1])
    with col1:
        meal_name = st.text_input("Meal Name", placeholder="e.g., Restaurant Lunch", key="custom_meal_name")
    with col2:
        category = st.selectbox("Category", MealCategory.as_list(), key="custom_category")
    
    st.divider()
    st.subheader("📊 Enter Macros")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        calories = st.number_input("Calories", min_value=0.0, step=10.0)
    with col2:
        proteins = st.number_input("Proteins (g)", min_value=0.0, step=1.0)
    with col3:
        carbs = st.number_input("Carbs (g)", min_value=0.0, step=1.0)
    with col4:
        fats = st.number_input("Fats (g)", min_value=0.0, step=1.0)
    
    if any([calories, proteins, carbs, fats]):
        st.divider()
        st.subheader("📊 Meal Summary")
        custom_macros = {
            'calories': calories,
            'proteins': proteins,
            'carbs': carbs,
            'fats': fats
        }
        # Display macros summary
        display_macros_summary(
            custom_macros,
            target_calories, 
            protein_target, 
            carbs_target, 
            fats_target
        )
        
        if st.button("💾 Save Custom Meal", disabled=not meal_name, type="primary"):
            if db.save_meal(meal_name, category, "custom", custom_macros=custom_macros):                
                set_success_message(f"Custom meal '{meal_name}' saved successfully!")
                st.rerun()
            else:
                set_error_message("A meal with this name already exists")
                st.rerun()

def main():
    """Main function for the Create Meal page"""
    st.title("🍽️ Create Meal")
    
    # Display any success/error messages
    display_success_error()
    
    # Load profile and calculate targets
    profile_targets = load_profile_and_targets()
    
    if not profile_targets[0]:
        st.warning("Please set up your profile first!")
        if st.button("Go to Profile Setup"):
            # Find the page for profile editing
            for page in st.session_state.pages:
                if "Edit Profile" in page.get("label", ""):
                    st.session_state.page = page
                    st.rerun()
        return
    
    # Create tabs for the different meal types
    meal_type = st.radio(
        "Meal Type",
        ["Regular Meal", "Custom Meal"],
        horizontal=True,
        help="Regular meals are built from food sources, custom meals have manually entered macros"
    )
    
    st.divider()
    
    # Load food sources for regular meals
    foods_df = load_food_sources() if meal_type == "Regular Meal" else None
    
    if meal_type == "Regular Meal":
        create_regular_meal(foods_df, profile_targets)
    else:
        create_custom_meal(profile_targets)
    
    # Show helpful information
    with st.expander("💡 Meal Creation Tips"):
        st.markdown("""
        ### Regular Meals vs Custom Meals
        
        **Regular Meals**
        - Built from food sources in your database
        - Nutrition calculated automatically based on ingredients
        - Great for meals you prepare yourself
        
        **Custom Meals**
        - Manually enter macro information
        - Useful for restaurant meals or packaged foods
        - When you know the nutrition facts but not the exact ingredients
        
        ### Tips for Good Meal Planning
        
        - Try to balance your macros according to your goals
        - For weight loss, focus on protein-rich, filling foods
        - For muscle gain, ensure adequate protein and total calories
        - Create template meals that you can reuse in your meal programs
        """)

main()