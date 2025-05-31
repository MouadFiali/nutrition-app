"""
Food Management page for the Nutrition App.

This page allows users to view, edit, and delete food sources.
"""
import streamlit as st
import pandas as pd
from utils.db_manager import NutritionDB
from utils.constants import FoodCategory, BaseUnit
from utils.nutrition import calculate_macro_percentages
from utils.ui import display_success_error, set_success_message, set_error_message

# Initialize database
db = NutritionDB()

# Initialize session state variables if not already present
if 'food_editor_key' not in st.session_state:
    st.session_state.food_editor_key = 0

if 'confirm_delete_foods' not in st.session_state:
    st.session_state.confirm_delete_foods = False

if 'foods_to_delete' not in st.session_state:
    st.session_state.foods_to_delete = []

if 'delete_food_info' not in st.session_state:
    st.session_state.delete_food_info = {}

def load_food_sources():
    """Load food sources without caching"""
    return db.load_food_sources()

def refresh_food_editor():
    """Increment the food editor key to force a refresh"""
    st.session_state.food_editor_key += 1

def update_food_source(food_id, name, category, calories, proteins, carbs, fats,
                     base_unit, conversion_factor=1.0):
    """Update an existing food source and handle the refresh"""
    if db.update_food_source(
        food_id, name, category, calories, proteins, carbs, fats,
        base_unit, conversion_factor
    ):
        refresh_food_editor()
        set_success_message("Food updates saved successfully!")
    else:
        set_error_message("Update failed! The name may already be in use.")

    st.rerun()

def check_food_in_meals(food_names):
    """Check if food sources are used in any meals."""
    return db.check_food_in_meals(food_names)

def check_meals_in_programs(meal_ids):
    """Check if any meals are used in programs."""
    return db.check_meals_in_programs(meal_ids)

def delete_food_sources(food_names):
    """Delete food sources with confirmation if they are used in meals"""
    if not food_names:
        return False
    
    # Store deletion information
    st.session_state.confirm_delete_foods = False
    st.session_state.foods_to_delete = food_names
    
    # Check if foods are used in meals
    meal_info = check_food_in_meals(food_names)
    
    if meal_info:
        # Get which programs these meals are used in
        meal_ids = [meal['meal_id'] for food_meals in meal_info['foods_in_meals'].values() 
                   for meal in food_meals]
        program_info = check_meals_in_programs(meal_ids)
        
        st.session_state.delete_food_info = {
            'meal_info': meal_info,
            'program_info': program_info,
            'food_names': food_names
        }
        st.session_state.confirm_delete_foods = True
        st.rerun()
    else:
        # No meals use these foods, delete directly
        db.delete_multiple_food_sources(food_names)
        refresh_food_editor()
        set_success_message(f"Deleted {len(food_names)} foods successfully")
        st.rerun()
    
    return True

def show_delete_confirmation():
    """Display delete confirmation dialog"""
    if not st.session_state.confirm_delete_foods:
        return
    
    info = st.session_state.delete_food_info
    meal_info = info['meal_info']
    program_info = info['program_info']
    food_count = len(st.session_state.foods_to_delete)
    
    warning_text = (f"⚠️ {food_count} food{'s' if food_count > 1 else ''} you are trying to delete "
                   f"{'are' if food_count > 1 else 'is'} used in {meal_info['total_meals']} meals!")
    
    if program_info:
        warning_text += f"\n\nThese meals are also used in {program_info['total_programs']} meal programs!"
    
    st.warning(warning_text)
    
    # Show details about which meals are affected
    with st.expander("View affected meals"):
        for food_name, meals in meal_info['foods_in_meals'].items():
            st.markdown(f"**{food_name}** is used in:")
            for meal in meals:
                st.markdown(f"• **{meal['meal_name']}** (quantity: {meal['quantity']})")
    
    # Show details about which programs are affected if any
    if program_info:
        with st.expander("View affected programs"):
            for program in program_info['programs']:
                st.markdown(f"• **{program[1]}**")
    
    st.markdown("**Deleting these foods will make them unavailable for future meal planning.**")
    if meal_info['total_meals'] > 0:
        st.markdown("**⚠️ Warning: Existing meals will be affected and may have incorrect nutritional values!**")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancel", use_container_width=True):
            # Reset confirmation state
            st.session_state.confirm_delete_foods = False
            st.session_state.foods_to_delete = []
            st.session_state.delete_food_info = {}
            st.rerun()
    
    with col2:
        if st.button("Confirm Delete", type="primary", use_container_width=True):
            # Proceed with deletion
            db.delete_multiple_food_sources(st.session_state.foods_to_delete)
            
            # Create success message
            message = f"Deleted {len(st.session_state.foods_to_delete)} foods"
            if meal_info['total_meals'] > 0:
                message += f" that were used in {meal_info['total_meals']} meals"
            set_success_message(message)
            
            # Reset confirmation state
            st.session_state.confirm_delete_foods = False
            st.session_state.foods_to_delete = []
            st.session_state.delete_food_info = {}
            
            refresh_food_editor()
            st.rerun()

def display_food_editor(foods_df):
    """Display the editable food sources table"""
    if foods_df.empty:
        st.info("No food sources registered. Add some foods using the 'Add Food' page.")
        return
    
    # Category filter
    all_categories = foods_df['category'].unique()
    selected_categories = st.multiselect(
        "Filter by Categories",
        options=all_categories,
        default=all_categories,
        placeholder="Select categories..."
    )
    
    if selected_categories:
        filtered_df = foods_df[foods_df['category'].isin(selected_categories)]
    else:
        filtered_df = foods_df.copy()
        
    if filtered_df.empty:
        st.info("No foods matching the selected categories.")
        return
        
    # Add macro percentages and selection checkbox
    filtered_df = calculate_macro_percentages(filtered_df)
    filtered_df['select'] = False
    
    # Create the editable dataframe with a key based on our session state counter
    # to force re-rendering when data changes
    edited_df = st.data_editor(
        filtered_df,
        key=f'food_editor_{st.session_state.food_editor_key}',
        use_container_width=True,
        hide_index=True,
        column_config={
            "select": st.column_config.CheckboxColumn(
                "Select",
                help="Select for deletion"
            ),
            "name": st.column_config.TextColumn(
                "Name",
                required=True,
            ),
            "category": st.column_config.SelectboxColumn(
                "Category",
                options=FoodCategory.as_list(),
                required=True
            ),
            "calories": st.column_config.NumberColumn(
                "Calories",
                help="Per 100g/ml",
                min_value=0,
                format="%.1f"
            ),
            "proteins": st.column_config.NumberColumn(
                "Proteins (g)",
                help="Protein content",
                min_value=0,
                format="%.1f"
            ),
            "carbs": st.column_config.NumberColumn(
                "Carbs (g)",
                help="Carbohydrate content",
                min_value=0,
                format="%.1f"
            ),
            "fats": st.column_config.NumberColumn(
                "Fats (g)",
                help="Fat content",
                min_value=0,
                format="%.1f"
            ),
            "base_unit": st.column_config.SelectboxColumn(
                "Unit",
                options=BaseUnit.as_list()
            ),
            "conversion_factor": st.column_config.NumberColumn(
                "g/Unit",
                help="Grams per unit (for unit-based foods)",
                min_value=0,
                format="%.2f"
            ),
            # Hide unused columns
            "id": None,
            "proteins_pct": None,
            "carbs_pct": None,
            "fats_pct": None,
            "portion_size": None
        }
    )
    
    # Help text for conversion factor
    st.caption("Note: The 'g/Unit' column only applies when 'Unit' is selected as the base unit.")
    
    # Handle updates
    if not edited_df.equals(filtered_df):
        changed_mask = ~(edited_df.drop('select', axis=1) == 
                       filtered_df.drop('select', axis=1)).all(axis=1)
        changed_rows = edited_df[changed_mask]
        
        updates_made = False
        for idx, row in changed_rows.iterrows():
            if not row['select']:  # Don't update rows marked for deletion
                # For non-unit foods, ensure conversion_factor is set to 1.0
                conv_factor = row['conversion_factor']
                if row['base_unit'] != BaseUnit.UNIT.value:
                    conv_factor = 1.0
                    
                update_food_source(
                    row['id'], row['name'], row['category'],
                    row['calories'], row['proteins'], row['carbs'],
                    row['fats'], row['base_unit'],
                    conv_factor
                )
    
    # Handle deletions - use columns to center the button
    selected_foods = edited_df[edited_df['select']]['name'].tolist()
    if selected_foods:
        col1, col2, col3 = st.columns([2,1,2])
        with col2:
            if st.button(f"Delete {len(selected_foods)} selected foods", 
                       type="primary"):
                delete_food_sources(selected_foods)

def main():
    """Main function for the Food Sources Management page"""
    st.title("📋 Manage Food Sources")
    
    # Check if we need to show the delete confirmation dialog
    if st.session_state.confirm_delete_foods:
        show_delete_confirmation()
        return
    
    # Display any success/error messages
    display_success_error()
    
    # Load food sources
    foods_df = load_food_sources()
    
    st.subheader("📊 Food Sources Database")
    display_food_editor(foods_df)
    
    # Helpful information
    with st.expander("💡 Food Management Tips"):
        st.markdown("""
        ### Editing Foods
        - Click directly on any cell to edit its value
        - Changes are saved automatically when you click outside the cell
        - For unit-based foods (like eggs or fruits), set the "g/Unit" value to the weight in grams of one unit
        
        ### Deleting Foods
        - Select foods using the checkboxes in the "Select" column
        - Click the "Delete" button to remove selected foods
        - **Note:** Deleting foods used in meals may cause nutrition calculations to be incorrect for those meals
        
        ### Filtering
        - Use the "Filter by Categories" dropdown to show only foods from specific categories
        """)

main()