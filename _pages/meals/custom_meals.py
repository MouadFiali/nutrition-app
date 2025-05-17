"""
Custom Meals Management page for the Nutrition App.

This page allows users to view, edit, and delete custom meals.
"""
import streamlit as st
import pandas as pd
from utils.db_manager import NutritionDB
from utils.constants import MealCategory
from utils.nutrition import (
    calculate_all_metrics, 
    calculate_macro_targets
)
from utils.ui import (
    display_success_error, 
    set_success_message, 
    set_error_message,
    display_macros_summary,
    create_macro_charts
)

# Initialize database
db = NutritionDB()

# Initialize session state variables
if 'confirm_delete_meals' not in st.session_state:
    st.session_state.confirm_delete_meals = False

if 'meals_to_delete' not in st.session_state:
    st.session_state.meals_to_delete = []

if 'delete_info' not in st.session_state:
    st.session_state.delete_info = {}

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

def load_custom_meals():
    """Load custom meals without caching"""
    return db.get_custom_meals()

def delete_meals_with_confirmation(meal_ids, meal_names):
    """
    Delete meals with confirmation if they are used in programs.
    
    Args:
        meal_ids: List of meal IDs to delete
        meal_names: List of meal names (for display)
    """
    # Store the deletion information in session state
    st.session_state.confirm_delete_meals = False
    st.session_state.meals_to_delete = meal_ids
    
    # Check if any meals are used in programs
    meals_in_programs = {}
    total_programs_affected = 0
    total_occurrences = 0
    
    for meal_id in meal_ids:
        program_info = db.check_meal_in_programs(meal_id)
        if program_info:
            meals_in_programs[meal_id] = program_info
            total_programs_affected = max(total_programs_affected, program_info['total_programs'])
            total_occurrences += program_info['total_occurrences']
    
    # If any meals are in programs, show warning and confirm
    if meals_in_programs:
        st.session_state.delete_info = {
            'meals_in_programs': meals_in_programs,
            'total_programs_affected': total_programs_affected,
            'total_occurrences': total_occurrences,
            'meal_names': meal_names
        }
        st.session_state.confirm_delete_meals = True
        st.rerun()
    else:
        # No meals in programs, delete directly
        deleted_meals = 0
        for meal_id in meal_ids:
            if db.delete_meal(meal_id):
                deleted_meals += 1
        
        if deleted_meals == len(meal_ids):
            set_success_message(f"Deleted {deleted_meals} meals")
        else:
            set_error_message(f"Failed to delete {len(meal_ids) - deleted_meals} meals")
        st.rerun()

def show_delete_confirmation():
    """Display delete confirmation dialog"""
    if not st.session_state.confirm_delete_meals:
        return
    
    info = st.session_state.delete_info
    meal_count = len(st.session_state.meals_to_delete)
    
    st.warning(
        f"⚠️ {meal_count} meal{'s' if meal_count > 1 else ''} you are trying to delete "
        f"{'are' if meal_count > 1 else 'is'} used in meal programs!\n\n"
        f"• {info['total_occurrences']} occurrences across {info['total_programs_affected']} programs will be affected."
    )
    
    # Show details about which programs are affected
    with st.expander("View affected programs"):
        for meal_id, program_info in info['meals_in_programs'].items():
            meal_idx = st.session_state.meals_to_delete.index(meal_id)
            meal_name = info['meal_names'][meal_idx]
            
            st.markdown(f"**{meal_name}** is used in:")
            for program_name, occurrences in program_info['programs'].items():
                st.markdown(f"• **{program_name}**: {occurrences} occurrences")
    
    st.markdown("**Deleting these meals will also remove them from all meal programs.**")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.session_state.confirm_delete_meals = False
            st.session_state.meals_to_delete = []
            st.session_state.delete_info = {}
            st.rerun()
    
    with col2:
        if st.button("Confirm Delete", type="primary", use_container_width=True):
            # Proceed with deletion
            for meal_id in st.session_state.meals_to_delete:
                db.delete_meal(meal_id)
            
            set_success_message(f"Deleted {len(st.session_state.meals_to_delete)} meals and removed them from {info['total_programs_affected']} meal programs")
            
            # Reset confirmation state
            st.session_state.confirm_delete_meals = False
            st.session_state.meals_to_delete = []
            st.session_state.delete_info = {}
            st.rerun()

def show_meal_details(meal):
    """Display detailed meal information"""
    with st.expander(f"📊 {meal['name']} Details", expanded=True):
        # Display meal category
        st.caption(f"Category: {meal['category']}")
        
        # Display macros
        st.subheader("Nutritional Information")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Calories", f"{meal['calories']:.0f} kcal")
        with col2:
            st.metric("Proteins", f"{meal['proteins']:.1f}g")
        with col3:
            st.metric("Carbs", f"{meal['carbs']:.1f}g")
        with col4:
            st.metric("Fats", f"{meal['fats']:.1f}g")
        
        # Display macro distribution chart
        st.divider()
        st.subheader("Macro Distribution")
        
        # Create macro charts
        dist_fig, _ = create_macro_charts({
            'calories': meal['calories'],
            'proteins': meal['proteins'],
            'carbs': meal['carbs'],
            'fats': meal['fats']
        })
        
        st.plotly_chart(dist_fig, use_container_width=True)

def main():
    """Main function for the Custom Meals page"""
    st.title("🎯 Custom Meals Management")
    
    # Check if we need to show the delete confirmation dialog
    if st.session_state.confirm_delete_meals:
        show_delete_confirmation()
        return
    
    # Display any success/error messages
    display_success_error()
    
    # Load profile and calculate targets
    profile_targets = load_profile_and_targets()
    
    if not profile_targets[0]:
        st.warning("Please set up your profile first!")
        return
    
    # Unpack targets
    _, target_calories, protein_target, carbs_target, fats_target = profile_targets
    
    # Load custom meals
    meals_df = load_custom_meals()
    
    if meals_df.empty:
        st.info("No custom meals saved yet. Create some using the 'Create Meal' page.")
        return
    
    # Filter by category if needed
    st.subheader("📋 Your Custom Meals")
    
    categories = sorted(meals_df['category'].unique().tolist())
    selected_cats = st.multiselect(
        "Filter by Category", 
        options=categories,
        default=categories
    )
    
    if selected_cats:
        filtered_meals = meals_df[meals_df['category'].isin(selected_cats)]
    else:
        filtered_meals = meals_df
    
    if filtered_meals.empty:
        st.info("No meals in the selected categories.")
        return
    
    # Sort by category and name
    filtered_meals = filtered_meals.sort_values(by=['category', 'name'])
    
    # Create a clean DataFrame for display, dropping unused columns
    display_df = filtered_meals.copy()
    
    # Add checkbox column
    display_df['select'] = False
    
    # Reorder and select only the columns we want to display
    display_df = display_df[['select', 'name', 'category', 'calories', 'proteins', 'carbs', 'fats', 'id']]
    
    # Use a default unique key for the editor to avoid issues
    editor_key = "custom_meals_editor"
    
    # Display as directly editable dataframe
    edited_df = st.data_editor(
        display_df,
        column_config={
            "select": st.column_config.CheckboxColumn("Select"),
            "name": st.column_config.TextColumn("Name", required=True),
            "category": st.column_config.SelectboxColumn(
                "Category", 
                options=MealCategory.as_list(), 
                required=True,
                help="Select 'Lunch/Dinner' for meals that can be used for either lunch or dinner"
            ),
            "calories": st.column_config.NumberColumn(
                "Calories", 
                format="%.0f kcal", 
                min_value=0, 
                step=10
            ),
            "proteins": st.column_config.NumberColumn(
                "Protein", 
                format="%.1f g", 
                min_value=0, 
                step=1
            ),
            "carbs": st.column_config.NumberColumn(
                "Carbs", 
                format="%.1f g", 
                min_value=0, 
                step=1
            ),
            "fats": st.column_config.NumberColumn(
                "Fat", 
                format="%.1f g", 
                min_value=0, 
                step=1
            ),
            "id": None  # Hide ID column
        },
        hide_index=True,
        use_container_width=True,
        key=editor_key,
        num_rows="fixed"  # No adding rows
    )

    st.caption("The meal details can be edited directly in the table above.")
    
    # Process any edits in the dataframe
    if not edited_df.equals(display_df):
        # Handle edited rows (excluding the 'select' column)
        edited_mask = ~(edited_df.drop('select', axis=1) == display_df.drop('select', axis=1)).all(axis=1)
        edited_rows = edited_df[edited_mask]
        
        for _, row in edited_rows.iterrows():
            # Update the meal in the database
            custom_macros = {
                'calories': row['calories'],
                'proteins': row['proteins'],
                'carbs': row['carbs'],
                'fats': row['fats']
            }
            
            if db.update_meal(
                row['id'],
                row['name'],
                row['category'],
                custom_macros=custom_macros
            ):
                set_success_message(f"Updated meal: {row['name']}")
                st.rerun()
            else:
                set_error_message(f"Failed to update meal: {row['name']}. Name may already exist.")
                st.rerun()
        
    
    # Get selected meals for deletion
    # Get selected meals for deletion
    selected_meals = edited_df[edited_df['select']]
    
    # Display based on number of selected meals
    if len(selected_meals) > 1:
        # Multiple meals selected - show just a delete button
        with st.container(border=True):
            st.info(f"{len(selected_meals)} meals selected")
            
            # Add delete button for the selected meals
            if st.button(f"🗑️ Delete {len(selected_meals)} Selected Meals", type="secondary", use_container_width=True):
                meal_ids = selected_meals['id'].tolist()
                meal_names = selected_meals['name'].tolist()
                delete_meals_with_confirmation(meal_ids, meal_names)
    
    # Display selected meal details if exactly one is selected
    elif len(selected_meals) == 1:
        # Display meal details for the single selected meal
        selected_meal = selected_meals.iloc[0]
        
        with st.container(border=True):
            show_meal_details(selected_meal)
            
            # Add delete button for the selected meal
            if st.button("🗑️ Delete Selected Meal", type="secondary", use_container_width=True):
                delete_meals_with_confirmation(
                    [selected_meal['id']], 
                    [selected_meal['name']]
                )
    
    else:
        # No meals selected - show a message
        st.info("Select meals to view details or delete them.")
# Run the main function when the script is executed
main()