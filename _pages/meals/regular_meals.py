"""
Regular Meals Management page for the Nutrition Planner application.

This page allows users to view, edit, and delete regular meals.
"""
import streamlit as st
import pandas as pd
from utils.db_manager import NutritionDB
from utils.constants import MealCategory
from utils.nutrition import (
    calculate_all_metrics, 
    calculate_macro_targets, 
    calculate_meal_macros
)
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
if 'edit_slots' not in st.session_state:
    st.session_state.edit_slots = 3

if 'current_edit_meal' not in st.session_state:
    st.session_state.current_edit_meal = None

if 'confirm_delete_meals' not in st.session_state:
    st.session_state.confirm_delete_meals = False

if 'meals_to_delete' not in st.session_state:
    st.session_state.meals_to_delete = []

if 'delete_info' not in st.session_state:
    st.session_state.delete_info = {}

if 'selected_meal_id' not in st.session_state:
    st.session_state.selected_meal_id = None

def add_edit_slot():
    """Add a new food slot in the edit interface"""
    st.session_state.edit_slots += 1
    st.rerun()

def remove_edit_slot(prefix=""):
    """Remove a food slot from the edit interface"""
    if st.session_state.edit_slots > 2:
        st.session_state.edit_slots -= 1
        st.rerun()

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

def load_food_sources():
    """Load food sources without caching"""
    return db.load_food_sources()

def load_regular_meals():
    """Load regular meals without caching and process each one individually to avoid DataFrame issues"""
    meals = db.get_regular_meals()
    if meals.empty:
        return meals
    
    # Process the meals data to calculate macros for each meal
    for idx, meal in meals.iterrows():
        if meal['type'] == 'regular' and 'foods' in meal and meal['foods']:
            macros = calculate_meal_macros(meal['foods'])
            meals.at[idx, 'calories'] = macros['calories']
            meals.at[idx, 'proteins'] = macros['proteins']
            meals.at[idx, 'carbs'] = macros['carbs']
            meals.at[idx, 'fats'] = macros['fats']
    
    return meals

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
        for meal_id in meal_ids:
            db.delete_meal(meal_id)
        
        set_success_message(f"Deleted {len(meal_ids)} meals")
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

def show_meal_details(meal_data):
    """Display detailed meal information"""
    # Display meal category and type
    st.caption(f"Category: {meal_data['category']} | Type: {meal_data['type'].capitalize()}")
    
    # Display macros if available
    if meal_data['type'] == 'regular' and 'foods' in meal_data and meal_data['foods']:
        # Calculate macros from foods
        macros = calculate_meal_macros(meal_data['foods'])
        
        # Display macros
        st.subheader("📊 Nutritional Information")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Calories", f"{macros['calories']:.0f} kcal")
        with col2:
            st.metric("Proteins", f"{macros['proteins']:.1f}g")
        with col3:
            st.metric("Carbs", f"{macros['carbs']:.1f}g")
        with col4:
            st.metric("Fats", f"{macros['fats']:.1f}g")
        
        # Display ingredients
        st.subheader("🍲 Ingredients")
        
        # Create a DataFrame for better display
        ingredients_df = pd.DataFrame([
            {
                "Food": food['name'],
                "Quantity": f"{food['quantity']} {food['base_unit']}",
                "Calories": f"{food['calories'] * food['quantity'] / 100:.0f} kcal",
                "Protein": f"{food['proteins'] * food['quantity'] / 100:.1f}g",
                "Carbs": f"{food['carbs'] * food['quantity'] / 100:.1f}g",
                "Fat": f"{food['fats'] * food['quantity'] / 100:.1f}g"
            }
            for food in meal_data['foods']
        ])
        
        st.dataframe(ingredients_df, hide_index=True, use_container_width=True)

def handle_meal_edit(meal_to_edit, foods_df, target_calories, protein_target, carbs_target, fats_target):
    """Handle meal editing with state management"""
    # Clear edit slots when meal changes
    edit_meal_key = f"edit_meal_{meal_to_edit['id']}"
    if 'current_edit_meal' not in st.session_state or st.session_state.current_edit_meal != edit_meal_key:
        if 'edit_slots' in st.session_state:
            del st.session_state.edit_slots
        st.session_state.current_edit_meal = edit_meal_key

    # Initialize session state variables for editing
    if 'edit_meal_name' not in st.session_state:
        st.session_state.edit_meal_name = meal_to_edit['name']
    if 'edit_meal_category' not in st.session_state:
        st.session_state.edit_meal_category = meal_to_edit['category']

    # Get current meal food quantities
    meal_data = db.get_meal_with_foods(meal_to_edit['id'])
    if not meal_data or ('foods' not in meal_data and meal_data['type'] == 'regular'):
        return None, None, None, None
        
    meal_foods = meal_data['foods']
    current_quantities = {
        food['name']: {
            'quantity': food['quantity'],
            'id': food['id'],
            'base_unit': food['base_unit']
        } for food in meal_foods
    }
    
    # Initialize edit slots with current foods
    if 'edit_slots' not in st.session_state:
        st.session_state.edit_slots = max(3, len(current_quantities))
    
    col1, col2 = st.columns([2, 1])
    with col1:
        new_name = st.text_input(
            "Meal Name", 
            value=st.session_state.edit_meal_name,
            key="edit_meal_name_input"
        )
        st.session_state.edit_meal_name = new_name
    with col2:
        # Include the new Lunch/Dinner category in the dropdown
        new_category = st.selectbox(
            "Category", 
            MealCategory.as_list(),
            index=MealCategory.as_list().index(st.session_state.edit_meal_category) if st.session_state.edit_meal_category in MealCategory.as_list() else 0,
            key="edit_meal_category_input",
            help="Select 'Lunch/Dinner' for meals that can be used for either lunch or dinner"
        )
        st.session_state.edit_meal_category = new_category
    
    st.divider()
    st.subheader("Edit Foods and Quantities")
    new_quantities = {}
    
    # Create food slots using the UI utility function
    for i in range(st.session_state.edit_slots):
        food_name, data = create_food_slot(
            i, 
            foods_df, 
            current_quantities,
            prefix=f"edit_{meal_to_edit['id']}_",
            can_remove=st.session_state.edit_slots > 2,
            remove_callback=remove_edit_slot
        )
        if food_name and data:
            new_quantities[food_name] = data
    
    # Add food slot button
    if st.button("➕ Add Another Food", key=f"edit_add_food_{meal_to_edit['id']}"):
        add_edit_slot()
    
    # Show updated macros
    if new_quantities:
        st.divider()
        st.subheader("Updated Meal Summary")
        # Calculate macros for regular meal
        macros = calculate_meal_macros(foods_df, new_quantities)
        # Display macros summary
        display_macros_summary(macros, target_calories, protein_target, carbs_target, fats_target)
        
        return new_name, new_category, new_quantities, macros
    
    return None, None, None, None

def main():
    """Main function for the Regular Meals page"""
    st.title("🥗 Regular Meals Management")
    
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
    
    # Load food sources and meals
    foods_df = load_food_sources()
    
    try:
        meals_df = load_regular_meals()
    except Exception as e:
        st.error(f"Error loading meals: {str(e)}")
        meals_df = pd.DataFrame()
    
    if meals_df.empty:
        st.info("No regular meals saved yet. Create some using the 'Create Meal' page.")
        return
    
    # Display meals
    st.subheader("📋 Your Regular Meals")
    
    # Filter by category if needed
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
    
    # Display meals in a table with checkbox column
    meal_table = []
    for _, meal in filtered_meals.iterrows():
        # Calculate macros if needed
        if 'foods' in meal and meal['foods'] and ('calories' not in meal or meal['calories'] == 0):
            macros = calculate_meal_macros(meal['foods'])
            calories = macros['calories']
            proteins = macros['proteins']
            carbs = macros['carbs']
            fats = macros['fats']
        else:
            calories = meal.get('calories', 0)
            proteins = meal.get('proteins', 0)
            carbs = meal.get('carbs', 0)
            fats = meal.get('fats', 0)
            
        meal_table.append({
            'id': meal['id'],
            'select': False,
            'name': meal['name'],
            'category': meal['category'],
            'calories': calories,
            'proteins': proteins,
            'carbs': carbs,
            'fats': fats,
        })
    
    # Convert to DataFrame for display
    if meal_table:
        meal_table_df = pd.DataFrame(meal_table)
        
        # Display as dataframe with checkbox column
        edited_df = st.data_editor(
            meal_table_df,
            column_config={
                "id": None,
                "select": st.column_config.CheckboxColumn("Select"),
                "name": "Name",
                "category": "Category",
                "calories": st.column_config.NumberColumn("Calories", format="%.0f kcal"),
                "proteins": st.column_config.NumberColumn("Protein", format="%.1f g"),
                "carbs": st.column_config.NumberColumn("Carbs", format="%.1f g"),
                "fats": st.column_config.NumberColumn("Fat", format="%.1f g"),
            },
            hide_index=True,
            use_container_width=True,
            disabled=["name", "category", "calories", "proteins", "carbs", "fats"],
            key="meal_table_editor"
        )
        
        # Get the selected meal rows
        selected_meals = edited_df[edited_df['select']]
        
        # Display selected meal details if any
        # Different handling based on number of selected meals
        if len(selected_meals) > 1:
            # Multiple meals selected - show just a delete button
            with st.container(border=True):
                st.info(f"{len(selected_meals)} meals selected")
                
                # Add delete button for all selected meals
                if st.button(f"🗑️ Delete {len(selected_meals)} Selected Meals", type="secondary", use_container_width=True):
                    meal_ids = selected_meals['id'].tolist()
                    meal_names = selected_meals['name'].tolist()
                    delete_meals_with_confirmation(meal_ids, meal_names)
        
        # Display details and actions for single meal selection
        elif len(selected_meals) == 1:
            # Use the single selected meal
            selected_meal = selected_meals.iloc[0]
            meal_id = selected_meal['id']
            
            # Store the selected meal id in session state
            st.session_state.selected_meal_id = meal_id
            
            # Get the full meal data from the original dataframe
            meal_data = db.get_meal_with_foods(meal_id)
            
            # Display meal details in a container with border
            with st.container(border=True):
                st.subheader(f"🍽️ {meal_data['name']}")
                
                # Display meal details
                show_meal_details(meal_data)
                
                # Display action buttons
                st.divider()
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✏️ Edit Meal", type="primary", use_container_width=True):
                        st.session_state.editing_meal = meal_id
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete Meal", type="secondary", use_container_width=True):
                        delete_meals_with_confirmation([meal_id], [meal_data['name']])
        
        else:
        # No meals selected - show a message
            st.info("Select meals to view details or edit/delete them.")
    
    # Handle meal editing if a meal was selected
    if 'editing_meal' in st.session_state:
        meal_id = st.session_state.editing_meal
        meal_to_edit = filtered_meals[filtered_meals['id'] == meal_id].iloc[0]
        
        st.divider()
        with st.container(border=True):
            st.subheader(f"✏️ Editing: {meal_to_edit['name']}")
            
            new_name, new_category, new_quantities, macros = handle_meal_edit(
                meal_to_edit, foods_df, target_calories, protein_target, carbs_target, fats_target
            )
            
            if new_quantities or macros:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 Save Changes", type="primary", disabled=not (new_name and new_quantities), use_container_width=True):
                        if db.update_meal(
                            meal_to_edit['id'],
                            new_name,
                            new_category,
                            foods_quantities=new_quantities
                        ):
                            # Clear edit state
                            st.session_state.edit_slots = 3
                            st.session_state.current_edit_meal = None
                            if 'editing_meal' in st.session_state:
                                del st.session_state.editing_meal
                            if 'edit_meal_name' in st.session_state:
                                del st.session_state.edit_meal_name
                            if 'edit_meal_category' in st.session_state:
                                del st.session_state.edit_meal_category
                            set_success_message("Meal updated successfully!")
                            st.rerun()
                        else:
                            set_error_message("Failed to update meal. Name may already exist.")
                            st.rerun()
                
                with col2:
                    if st.button("❌ Cancel Editing", type="secondary", use_container_width=True):
                        # Clear edit state
                        if 'editing_meal' in st.session_state:
                            del st.session_state.editing_meal
                        if 'edit_meal_name' in st.session_state:
                            del st.session_state.edit_meal_name
                        if 'edit_meal_category' in st.session_state:
                            del st.session_state.edit_meal_category
                        st.rerun()

# Run the main function when the script is executed
main()