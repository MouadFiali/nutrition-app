"""
View Programs page for the Nutrition Planner application.

This page allows users to view existing meal programs and their scheduled meals,
edit specific meals, and view daily nutrition summaries.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.db_manager import NutritionDB
from utils.constants import MealTime, DAYS_PER_PAGE
from utils.nutrition import (
    calculate_meal_macros_from_record,
    calculate_all_metrics,
    calculate_macro_targets,
)
from utils.ui import (
    display_success_error, 
    set_success_message, 
    create_pagination_controls,
    display_macros_summary
)

# Initialize database
db = NutritionDB()

# Initialize session state variables
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

def on_previous_page():
    """Handler for previous page button"""
    if st.session_state.current_page > 0:
        st.session_state.current_page -= 1
        st.rerun()

def on_next_page(total_pages):
    """Handler for next page button"""
    if st.session_state.current_page < total_pages - 1:
        st.session_state.current_page += 1
        st.rerun()

def display_dates(program_data):
    """Display program dates in metrics format"""
    # Convert string dates to datetime
    start_date = pd.to_datetime(program_data['start_date'])
    end_date = pd.to_datetime(program_data['end_date'])
    
    # Program duration display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Start Date", start_date.strftime("%d-%m-%Y"))
    with col2:
        st.metric("End Date", end_date.strftime("%d-%m-%Y"))
    with col3:
        duration = (end_date - start_date).days + 1
        st.metric("Duration", f"{duration} days")

def calculate_daily_nutrition_totals(day_meals):
    """Calculate the total nutrition values for a day's meals"""
    if day_meals.empty:
        return {
            'calories': 0,
            'proteins': 0,
            'carbs': 0,
            'fats': 0
        }
    
    totals = {
        'calories': 0,
        'proteins': 0,
        'carbs': 0,
        'fats': 0
    }
    
    for _, meal in day_meals.iterrows():
        # Calculate macros for the meal
        macros = calculate_meal_macros_from_record(meal)
        
        # Add to daily totals
        totals['calories'] += macros['calories']
        totals['proteins'] += macros['proteins']
        totals['carbs'] += macros['carbs']
        totals['fats'] += macros['fats']
    
    # Round the values
    return {k: round(v, 1) for k, v in totals.items()}

@st.dialog("Daily Nutrition Summary", width="large")
def show_daily_nutrition_summary(day_meals, date_str, profile=None):
    """Display nutrition summary for an entire day"""
    # Format date for display
    date_display = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A, %B %d')
    st.subheader(f"Nutrition Summary for {date_display}")
    
    # Calculate daily totals
    daily_totals = calculate_daily_nutrition_totals(day_meals)
    
    # If profile exists, calculate targets
    target_calories, protein_target, carbs_target, fats_target = 0, 0, 0, 0
    
    if profile:
        # Calculate targets based on profile
        _, target_calories, protein_target, carbs_target, fats_target = profile
        
        # Display nutrition summary with targets
        display_macros_summary(
            daily_totals,
            target_calories,
            protein_target,
            carbs_target,
            fats_target,
            show_progress=True
        )
    else:
        # Display just the nutrition summary without targets
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Calories", f"{daily_totals['calories']:.0f} kcal")
        with col2:
            st.metric("Protein", f"{daily_totals['proteins']:.1f}g")
        with col3:
            st.metric("Carbs", f"{daily_totals['carbs']:.1f}g")
        with col4:
            st.metric("Fat", f"{daily_totals['fats']:.1f}g")
    
    # Display the meals in this day
    st.divider()
    st.subheader("Meals in this day")
    
    # Group by meal time
    for meal_time in MealTime.as_list():
        meals = day_meals[day_meals['meal_time'] == meal_time]
        if not meals.empty:
            for _, meal in meals.iterrows():
                with st.container(border=True):
                    st.write(f"**{meal_time}:** {meal['meal_name']}")
                    
                    # Calculate macros for this meal
                    macros = calculate_meal_macros_from_record(meal)
                    
                    # Create a readable macro display
                    st.caption(
                        f"Calories: {macros['calories']:.0f} kcal | "
                        f"Protein: {macros['proteins']:.1f}g | "
                        f"Carbs: {macros['carbs']:.1f}g | "
                        f"Fat: {macros['fats']:.1f}g"
                    )

@st.dialog("Nutrition Information", width="large")
def show_nutrition_info(meal_data):
    """Display nutrition information in a dialog"""
    # Get macros from the meal data
    macros = calculate_meal_macros_from_record(meal_data)
    
    # Meal Title and Category
    st.markdown(f"""
        <h2 style='margin-bottom: 0;'>{meal_data['meal_name']}</h2>
        <p style='color: #666; margin-bottom: 20px;'>{meal_data['category']}</p>
        """, unsafe_allow_html=True)
    
    # Macros display in columns with full number display
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    
    with col1:
        st.metric(
            "Calories",
            f"{macros['calories']:.0f} kcal",
            delta=None,
            help="Total calories per serving"
        )
    
    with col2:
        st.metric(
            "Protein",
            f"{macros['proteins']:.2f}g",
            delta=None,
            help="Total protein content"
        )
    
    with col3:
        st.metric(
            "Carbs",
            f"{macros['carbs']:.2f}g",
            delta=None,
            help="Total carbohydrate content"
        )
    
    with col4:
        st.metric(
            "Fat",
            f"{macros['fats']:.2f}g",
            delta=None,
            help="Total fat content"
        )
    
    # Calculate macro percentages
    total_cals = (macros['proteins'] * 4 + macros['carbs'] * 4 + macros['fats'] * 9)
    
    if total_cals > 0:
        st.divider()
        st.markdown("### Macro Distribution")
        
        # Display macro distribution as progress bars
        protein_pct = (macros['proteins'] * 4 / total_cals) * 100
        carbs_pct = (macros['carbs'] * 4 / total_cals) * 100
        fats_pct = (macros['fats'] * 9 / total_cals) * 100
        
        st.progress(protein_pct/100, text=f"Protein: {protein_pct:.1f}%")
        st.progress(carbs_pct/100, text=f"Carbs: {carbs_pct:.1f}%")
        st.progress(fats_pct/100, text=f"Fat: {fats_pct:.1f}%")
    
    # Ingredients Section for regular meals
    if meal_data['type'] == 'regular':
        st.divider()
        st.markdown("### 📝 Ingredients")
        
        # Get the food sources for the meal if not already in the data
        if 'foods' not in meal_data:
            meal_details = db.get_meal_with_foods(int(meal_data['meal_id']))
            food_sources = meal_details.get('foods', []) if meal_details else []
        else:
            food_sources = meal_data['foods']
        
        if food_sources:
            # Create a clean table for ingredients with full width
            ingredients_df = pd.DataFrame([
                {
                    "Ingredient": food['name'],
                    "Amount": f"{food['quantity']} {food['base_unit']}"
                }
                for food in food_sources
            ])
            
            # Display table with full width and no index
            st.dataframe(
                ingredients_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Ingredient": st.column_config.TextColumn(
                        "Ingredient",
                        width="auto"
                    ),
                    "Amount": st.column_config.TextColumn(
                        "Amount",
                        width="auto"
                    )
                }
            )
        else:
            st.info("This meal has no registered ingredients.", icon="🥺")

@st.dialog("Add Meal", width="large")
def show_meal_dialog(program_id, date_str, meal_time, existing_meal=None, is_edit_mode=False):
    """Display dialog for adding or editing a meal to a specific time slot"""
    # Format date and meal time for display
    date_display = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A, %B %d')
    
    # Set dialog title based on mode
    dialog_title = f"{'Edit' if is_edit_mode else 'Add'} a meal for {date_display} - {meal_time}"
    st.subheader(dialog_title)
    
    # Load all meals
    meals_df = db.get_all_meals()
    
    if meals_df.empty:
        st.warning("No meals available. Please create some meals first!")
        return
    
    # Define the initial selection index
    initial_index = 0
    if is_edit_mode and existing_meal is not None:
        # Find the index of the existing meal
        meal_names = meals_df['name'].tolist()
        if existing_meal['meal_name'] in meal_names:
            initial_index = meal_names.index(existing_meal['meal_name'])
    
    # Select a meal
    selected_meal = st.selectbox(
        "Choose a meal",
        meals_df['name'].tolist(),
        index=initial_index
    )
    
    # Get meal details for preview
    meal_data = meals_df[meals_df['name'] == selected_meal].iloc[0]
    
    # Show meal preview
    st.write("#### Meal Preview")
    
    # Display meal type and category
    st.caption(f"Type: {meal_data['type'].title()} | Category: {meal_data['category']}")
    
    # Calculate and display macros
    macros = calculate_meal_macros_from_record(meal_data)
    
    # Display macros in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Calories", f"{macros['calories']:.0f} kcal")
    with col2:
        st.metric("Protein", f"{macros['proteins']:.1f}g")
    with col3:
        st.metric("Carbs", f"{macros['carbs']:.1f}g")
    with col4:
        st.metric("Fat", f"{macros['fats']:.1f}g")
    
    # Add/Update button
    button_label = "Update Meal" if is_edit_mode else "Add Meal"
    if st.button(button_label, type="primary", use_container_width=True):
        meal_id = meal_data['id']
        if db.update_program_meal(int(program_id), int(meal_id), date_str, meal_time):
            action_text = "updated" if is_edit_mode else "added"
            set_success_message(f"{selected_meal} {action_text} for {date_display} - {meal_time}")
            st.rerun()
        else:
            st.error(f"Failed to {button_label.lower()}. Please try again.")

def delete_program_meal(program_id, date_str, meal_time):
    """Delete a meal from the program"""
    if db.delete_program_meal(program_id, date_str, meal_time):
        set_success_message("Meal removed!")
        st.rerun()

def display_meal_day(date, day_meals, program_id, profile=None):
    """Display meals for a specific day"""
    date_str = date.strftime('%Y-%m-%d')
    
    # Calculate daily nutrition totals
    daily_totals = calculate_daily_nutrition_totals(day_meals)
    
    # Create header with date and nutrition summary button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"### {date.strftime('%A, %B %d')}")
    
    with col2:
        nutrition_summary_button = st.button(
            "📊 Nutrition Summary", 
            key=f"summary_{date_str}",
            help="View day's nutrition totals",
            use_container_width=True
        )
        if nutrition_summary_button:
            show_daily_nutrition_summary(day_meals, date_str, profile)
    
    # Show a small inline summary
    st.caption(
        f"Daily Totals: {daily_totals['calories']:.0f} kcal | "
        f"Protein: {daily_totals['proteins']:.1f}g | "
        f"Carbs: {daily_totals['carbs']:.1f}g | "
        f"Fat: {daily_totals['fats']:.1f}g"
    )
    
    # Create columns for each meal time
    cols = st.columns(len(MealTime.as_list()))
    
    for col_idx, (col, meal_time) in enumerate(zip(cols, MealTime.as_list())):
        with col:
            st.write(f"**{meal_time}**")
            meal = day_meals[day_meals['meal_time'] == meal_time]
            
            if not meal.empty:
                meal_data = meal.iloc[0]
                
                # Generate a unique ID for this meal
                meal_unique_id = f"{date_str}_{meal_time}_{col_idx}"
                
                # Display meal in a container
                with st.container(border=True):
                    # Show the meal name
                    st.write(f"**{meal_data['meal_name']}**")
                    
                    # Show brief macros
                    macros = calculate_meal_macros_from_record(meal_data)
                    st.caption(f"{macros['calories']:.0f} kcal, P: {macros['proteins']:.1f}g")
                    
                    # Display meal actions with unique keys
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        if st.button("🔍", key=f"view_{meal_unique_id}", help="View nutrition info"):
                            show_nutrition_info(meal_data)
                    
                    with btn_col2:
                        if st.button("✏️", key=f"edit_{meal_unique_id}", help="Edit meal"):
                            show_meal_dialog(program_id, date_str, meal_time, existing_meal=meal_data, is_edit_mode=True)
                    
                    with btn_col3:
                        if st.button("🗑️", key=f"delete_{meal_unique_id}", help="Remove meal"):
                            delete_program_meal(program_id, date_str, meal_time)
            else:
                # Display "No meal assigned" with an Add button
                st.text("No meal assigned")
                if st.button("➕", key=f"add_{date_str}_{meal_time}", help="Add meal"):
                    show_meal_dialog(program_id, date_str, meal_time)

def load_profile_and_targets():
    """Load profile and calculate targets"""
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

def main():
    """Main function for the View Programs page"""
    st.title("📅 View Meal Programs")
    
    # Display any success/error messages
    display_success_error()
    
    # Get all programs
    programs = db.get_all_programs()
    if programs.empty:
        st.info("No meal programs created yet. Create a program in the 'Create Program' page.")
        return
    
    # Load profile and targets for nutrition comparison
    profile_targets = load_profile_and_targets()
    
    # Program selection
    st.subheader("Select Program")
    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    
    with col1:
        selected_program = st.selectbox(
            "Choose a program to view",
            programs['name'].tolist(),
            index=0,
            format_func=lambda x: f"{x}"
        )
    
    # Get program data
    program_data = programs[programs['name'] == selected_program].iloc[0]
    
    # Display delete button
    with col2:
        if st.button("🗑️ Delete Program", key="delete_program", use_container_width=True):
            if db.delete_program(int(program_data['id'])):
                set_success_message(f"Program '{selected_program}' deleted!")
                st.rerun()
    
    # Display program details
    st.divider()
    st.subheader("📆 Program Details")
    display_dates(program_data)
    
    # Get program meals
    program_id = int(program_data['id'])
    program_meals = db.get_program_meals(program_id)
    
    if program_meals.empty:
        st.info("This program has no meals assigned yet. Edit the program to add meals.")
        return
    
    # Prepare for paging through dates
    start_date = pd.to_datetime(program_data['start_date'])
    end_date = pd.to_datetime(program_data['end_date'])
    dates = pd.date_range(start_date, end_date)
    total_pages = len(dates) // DAYS_PER_PAGE + (1 if len(dates) % DAYS_PER_PAGE > 0 else 0)
    
    # Display pagination controls
    st.divider()
    create_pagination_controls(
        st.session_state.current_page,
        total_pages,
        on_previous_page,
        lambda: on_next_page(total_pages),
        suffix="top"
    )
    
    # Display daily meals for current page
    start_idx = st.session_state.current_page * DAYS_PER_PAGE
    end_idx = min(start_idx + DAYS_PER_PAGE, len(dates))
    current_dates = dates[start_idx:end_idx]
    
    for date in current_dates:
        date_str = date.strftime('%Y-%m-%d')
        day_meals = program_meals[program_meals['date'] == date_str]
        
        display_meal_day(date, day_meals, program_id, profile_targets)
        st.divider()
    
    # Bottom pagination controls for convenience
    create_pagination_controls(
        st.session_state.current_page,
        total_pages,
        on_previous_page,
        lambda: on_next_page(total_pages),
        suffix="bottom"
    )
    
    # Display some helpful tips
    with st.expander("💡 Program Viewing Tips"):
        st.markdown("""
        ### Understanding the Program View
        
        - Each row represents a day in your meal program
        - Each column represents a different meal time
        - Click the 🔍 icon to view detailed nutrition information for a meal
        - Click the ✏️ icon to edit a meal in a specific time slot
        - Click the 🗑️ icon to remove a meal from the program
        - Click the ➕ icon to quickly add a meal to an empty slot
        - Click the 📊 button to see the full nutrition summary for the day
        
        ### Meal Categories
        
        - **Breakfast**: Morning meals assigned to the Breakfast time slot
        - **Lunch**: Midday meals assigned to the Lunch time slot
        - **Dinner**: Evening meals assigned to the Dinner time slot
        - **Snacks**: Smaller meals assigned to Morning Snack or Afternoon Snack time slots
        
        ### Nutrition Tracking
        
        - Each day shows a brief summary of total calories and macros
        - Click the "Nutrition Summary" button to see detailed daily nutrition
        - Compare the daily nutrition totals to your personal targets
        
        ### Navigation
        
        - Use the pagination controls to navigate through days in your program
        - The current page number and total pages are shown in the center
        
        ### Program Management
        
        - To add or change meals in this program, use the "Edit Program" page
        - To create a new program, use the "Create Program" page
        """)

main()