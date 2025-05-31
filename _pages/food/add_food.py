"""
Add Food page for the Nutrition App.

This page allows users to add new food sources with their nutritional information.
"""
import streamlit as st
from utils.db_manager import NutritionDB
from utils.constants import FoodCategory, BaseUnit
from utils.ui import display_success_error, set_success_message, set_error_message

# Initialize database
db = NutritionDB()

def add_food_source(name, category, calories, proteins, carbs, fats,
                    base_unit, conversion_factor):
    """Add a new food source and handle success/error messages"""
    if not name:
        set_error_message("Please enter a food name")
        return False

    if db.save_food_source(
        name, category, calories, proteins, carbs, fats,
        base_unit, conversion_factor
    ):
        set_success_message(f"Food '{name}' added successfully!")
        return True
    else:
        set_error_message(f"A food with the name '{name}' already exists!")
        return False

def add_food_interface():
    """Display the interface for adding a new food source without forms"""
    st.subheader("🍎 Add New Food Source")
    
    # Initialize session state for base unit if needed
    if 'add_food_base_unit' not in st.session_state:
        st.session_state.add_food_base_unit = BaseUnit.GRAMS.value
    
    if 'food_name' not in st.session_state:
        st.session_state.food_name = ""
    if 'food_category' not in st.session_state:
        st.session_state.food_category = FoodCategory.as_list()[0]
    if 'food_calories' not in st.session_state:
        st.session_state.food_calories = 0.0
    if 'food_proteins' not in st.session_state:
        st.session_state.food_proteins = 0.0
    if 'food_carbs' not in st.session_state:
        st.session_state.food_carbs = 0.0
    if 'food_fats' not in st.session_state:
        st.session_state.food_fats = 0.0
    if 'food_conversion' not in st.session_state:
        st.session_state.food_conversion = 50.0
    
    # Food name and category
    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input(
            "Food Name", 
            value=st.session_state.food_name,
            placeholder="e.g., Chicken Breast",
            help="Enter a unique name for this food",
            key="food_name_input"
        )
    with col2:
        category = st.selectbox(
            "Category", 
            FoodCategory.as_list(),
            index=FoodCategory.as_list().index(st.session_state.food_category) if st.session_state.food_category in FoodCategory.as_list() else 0,
            help="Select the food category",
            key="food_category_input"
        )
    
    st.divider()
    
    # Macros input
    st.subheader("📊 Nutritional Information")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        calories = st.number_input(
            "Calories (per 100g/ml)", 
            min_value=0.0, 
            value=st.session_state.food_calories,
            format="%.1f", 
            step=10.0,
            help="Energy content per 100g/ml",
            key="food_calories_input"
        )
        proteins = st.number_input(
            "Proteins (g)", 
            min_value=0.0,
            value=st.session_state.food_proteins,
            format="%.1f", 
            step=1.0,
            help="Protein content per 100g/ml",
            key="food_proteins_input"
        )
    with col2:
        carbs = st.number_input(
            "Carbs (g)", 
            min_value=0.0,
            value=st.session_state.food_carbs,
            format="%.1f", 
            step=1.0,
            help="Carbohydrate content per 100g/ml",
            key="food_carbs_input"
        )
        fats = st.number_input(
            "Fats (g)", 
            min_value=0.0,
            value=st.session_state.food_fats,
            format="%.1f", 
            step=1.0,
            help="Fat content per 100g/ml",
            key="food_fats_input"
        )
    with col3:
        # Base unit selection
        base_unit = st.selectbox(
            "Base Unit", 
            BaseUnit.as_list(),
            index=BaseUnit.as_list().index(st.session_state.add_food_base_unit) if st.session_state.add_food_base_unit in BaseUnit.as_list() else 0,
            help="Select the unit of measurement",
            key="base_unit_input"
        )
        
        # When base unit changes, update session state
        if base_unit != st.session_state.add_food_base_unit:
            st.session_state.add_food_base_unit = base_unit
        
        # Get step & value based on base unit
        is_unit_based = base_unit == BaseUnit.UNIT.value
        
        # Initialize conversion factor
        conversion_factor = 1.0
        
        # Only show conversion factor field for unit-based foods
        if is_unit_based:
            conversion_factor = st.number_input(
                "Grams per Unit",
                min_value=0.1,
                value=st.session_state.food_conversion,
                help="Weight in grams for one unit (e.g., 50g for a medium egg)",
                format="%.1f",
                step=5.0,
                key="food_conversion_input"
            )
    
    # Add button
    if st.button("Add Food", type="primary", use_container_width=True):
        # Save current values to session state
        st.session_state.food_name = name
        st.session_state.food_category = category
        st.session_state.food_calories = calories
        st.session_state.food_proteins = proteins
        st.session_state.food_carbs = carbs
        st.session_state.food_fats = fats
        st.session_state.food_conversion = conversion_factor if is_unit_based else 1.0
        
        success = add_food_source(
            name, category, calories, proteins, carbs, fats,
            base_unit, conversion_factor if is_unit_based else 1.0
        )
        
        if success:
            # Reset form values after successful submission
            st.session_state.food_name = ""
            st.session_state.food_calories = 0.0
            st.session_state.food_proteins = 0.0
            st.session_state.food_carbs = 0.0
            st.session_state.food_fats = 0.0
            st.session_state.food_conversion = 50.0
            st.rerun()

# Main function for the Add Food page
st.title("🍎 Add Food Source")

# Display any success/error messages
display_success_error()

# Display the add food interface
add_food_interface()

# Display information about units and examples
with st.expander("💡 Food Entry Tips"):
    st.markdown("""
    ### Unit Types Explained
    - **Grams (g)**: Use for solid foods (meats, grains, etc.)
    - **Milliliters (ml)**: Use for liquids (milk, oil, etc.)
    - **Unit**: Use for countable foods (eggs, fruits, etc.)
    
    ### Tips for Accuracy
    - For unit-based foods, set the "Grams per Unit" to the average weight of one item.
    - Nutritional information should be per 100g/ml for weight/volume-based foods.
    - For unit-based foods, nutritional information should be per single unit.
    
    ### Examples
    1. **Chicken Breast (per 100g)**
       - Calories: 165 kcal
       - Protein: 31g
       - Carbs: 0g
       - Fat: 3.6g
       - Base Unit: g
       
    2. **Egg (per unit)**
       - Calories: 72 kcal
       - Protein: 6.3g
       - Carbs: 0.4g
       - Fat: 5g
       - Base Unit: unit
       - Grams per Unit: 50g (medium egg)
    """)