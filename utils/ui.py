"""
UI utilities for the Nutrition Planner application.

This module provides common UI functions and components used across multiple pages:
- Displaying metrics and summaries
- Formatting data for display
- Common UI patterns like food selection slots
- Progress bar displays
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from utils.nutrition import get_macro_distribution, get_macro_compliance

def apply_page_setup(title: str, icon: str = "🥗", wide_layout: bool = True):
    """
    Apply consistent page setup with title and icon.
    
    Args:
        title: The page title
        icon: Icon to display next to the title
        wide_layout: Whether to use wide layout
    """
    # Set page title and icon
    if wide_layout:
        st.set_page_config(
            page_title=f"{title} - Nutrition Planner",
            page_icon=icon,
            layout="wide"
        )
    else:
        st.set_page_config(
            page_title=f"{title} - Nutrition Planner",
            page_icon=icon
        )
    
    # Display the title
    st.title(f"{icon} {title}")
    
    return

def display_success_error():
    """Display success or error messages if present in session state"""
    if 'success_message' in st.session_state and st.session_state.success_message:
        st.success(st.session_state.success_message)
        st.session_state.success_message = None
        
    if 'error_message' in st.session_state and st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = None

def set_success_message(message: str):
    """Set a success message in session state"""
    st.session_state.success_message = message

def set_error_message(message: str):
    """Set an error message in session state"""
    st.session_state.error_message = message

def display_metrics(
    metrics: Dict[str, Union[float, int, str]],
    columns: int = 3,
    formatter: Optional[Dict[str, str]] = None
) -> None:
    """
    Display metrics in evenly spaced columns.
    
    Args:
        metrics: Dict mapping metric names to values
        columns: Number of columns to display
        formatter: Optional dict mapping metric names to format strings
    """
    cols = st.columns(columns)
    
    for i, (label, value) in enumerate(metrics.items()):
        format_str = "{:.0f}" if isinstance(value, (int, float)) else "{}"
        if formatter and label in formatter:
            format_str = formatter[label]
            
        formatted_value = format_str.format(value)
        with cols[i % columns]:
            st.metric(label, formatted_value)

def display_macros_summary(
    macros: Dict[str, float],
    target_calories: float = 0,
    protein_target: float = 0,
    carbs_target: float = 0,
    fats_target: float = 0,
    show_progress: bool = True
) -> None:
    """
    Display macros summary with optional progress bars.
    
    Args:
        macros: Dict with keys 'calories', 'proteins', 'carbs', 'fats'
        target_calories: Target calories per day
        protein_target: Target protein in grams per day
        carbs_target: Target carbs in grams per day
        fats_target: Target fats in grams per day
        show_progress: Whether to show progress bars
    """
    # First display the macro values
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Calories", 
            f"{macros['calories']:.0f} kcal",
            f"{(macros['calories']/target_calories*100):.1f}% of target" if target_calories > 0 else None
        )
    
    with col2:
        st.metric(
            "Protein", 
            f"{macros['proteins']:.1f}g",
            f"{(macros['proteins']/protein_target*100):.1f}% of target" if protein_target > 0 else None
        )
        
    with col3:
        st.metric(
            "Carbs", 
            f"{macros['carbs']:.1f}g",
            f"{(macros['carbs']/carbs_target*100):.1f}% of target" if carbs_target > 0 else None
        )
        
    with col4:
        st.metric(
            "Fats", 
            f"{macros['fats']:.1f}g",
            f"{(macros['fats']/fats_target*100):.1f}% of target" if fats_target > 0 else None
        )
    
    # If targets are provided and progress display is requested, show progress bars
    if show_progress and all([target_calories, protein_target, carbs_target, fats_target]):
        st.divider()
        st.subheader("Macro Progress")
        
        # Get macro distribution
        distribution = get_macro_distribution(macros)
        
        # Display progress bars
        st.progress(min(macros['calories'] / target_calories, 1.0) if target_calories else 0,
                    text=f"Calories: {macros['calories']:.0f} / {target_calories:.0f} kcal ({min(macros['calories'] / target_calories * 100 if target_calories else 0, 100):.1f}%)")
        
        st.progress(min(macros['proteins'] / protein_target, 1.0) if protein_target else 0,
                    text=f"Protein: {macros['proteins']:.1f}g / {protein_target:.0f}g ({min(macros['proteins'] / protein_target * 100 if protein_target else 0, 100):.1f}%) - {distribution['proteins_pct']:.1f}% of calories")
        
        st.progress(min(macros['carbs'] / carbs_target, 1.0) if carbs_target else 0,
                    text=f"Carbs: {macros['carbs']:.1f}g / {carbs_target:.0f}g ({min(macros['carbs'] / carbs_target * 100 if carbs_target else 0, 100):.1f}%) - {distribution['carbs_pct']:.1f}% of calories")
        
        st.progress(min(macros['fats'] / fats_target, 1.0) if fats_target else 0,
                    text=f"Fats: {macros['fats']:.1f}g / {fats_target:.0f}g ({min(macros['fats'] / fats_target * 100 if fats_target else 0, 100):.1f}%) - {distribution['fats_pct']:.1f}% of calories")

def create_macro_charts(
    macros: Dict[str, float],
    targets: Dict[str, float] = None
) -> Tuple[go.Figure, go.Figure]:
    """
    Create macro distribution and target comparison charts.
    
    Args:
        macros: Dict with keys 'calories', 'proteins', 'carbs', 'fats'
        targets: Optional dict with keys 'protein', 'carbs', 'fats'
        
    Returns:
        Tuple of (distribution_chart, comparison_chart)
    """
    # Create distribution pie chart
    distribution = get_macro_distribution(macros)
    
    dist_fig = px.pie(
        names=['Protein', 'Carbs', 'Fat'],
        values=[distribution['proteins_pct'], distribution['carbs_pct'], distribution['fats_pct']],
        title="Macro Distribution",
        color_discrete_sequence=['#636EFA', '#00CC96', '#EF553B']
    )
    
    dist_fig.update_traces(textinfo='percent+label', hole=.3)
    
    # Create comparison chart if targets are provided
    comp_fig = go.Figure()
    
    if targets:
        # Get compliance percentages
        compliance = get_macro_compliance(macros, targets)
        
        comp_fig.add_trace(go.Bar(
            x=['Calories', 'Protein', 'Carbs', 'Fat'],
            y=[compliance['calories_pct'], compliance['proteins_pct'], 
               compliance['carbs_pct'], compliance['fats_pct']],
            text=[f"{p:.1f}%" for p in [compliance['calories_pct'], compliance['proteins_pct'], 
                                      compliance['carbs_pct'], compliance['fats_pct']]],
            textposition='auto',
            marker_color=['#636EFA', '#636EFA', '#00CC96', '#EF553B']
        ))
        
        comp_fig.update_layout(
            title="Macro Target Compliance",
            yaxis=dict(
                title="% of Target",
                range=[0, 100]
            ),
            xaxis=dict(title="")
        )
    
    return dist_fig, comp_fig

def create_food_slot(
    index: int, 
    foods_df: pd.DataFrame, 
    quantities: Dict[str, Dict],
    prefix: str = "",
    can_remove: bool = True,
    remove_callback: Optional[Callable] = None
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Create a food selection slot with unit handling and optional remove button.
    
    Args:
        index: Index number for this food slot
        foods_df: DataFrame containing food sources data
        quantities: Dict of existing quantities by food name
        prefix: Optional prefix for the streamlit keys
        can_remove: Whether to display a remove button
        remove_callback: Function to call when remove button is clicked
        
    Returns:
        Tuple of (food_name, data_dict) or (None, None) if no food selected
    """
    if can_remove:
        food_col, quantity_col, remove_col = st.columns([3, 2, 0.5], vertical_alignment="bottom")
    else:
        food_col, quantity_col = st.columns([3, 2])
    
    # Get existing food for this slot from quantities
    existing_foods = list(quantities.keys())
    current_food = existing_foods[index] if index < len(existing_foods) else None
    
    with food_col:
        food_name = st.selectbox(
            f"Food {index+1}",
            ["None"] + foods_df['name'].tolist(),
            index=0 if not current_food else foods_df['name'].tolist().index(current_food) + 1,
            key=f"{prefix}food_{index}"
        )
    
    quantity = 0
    
    if food_name and food_name != "None":
        food_data = foods_df[foods_df['name'] == food_name].iloc[0]
        base_unit = food_data['base_unit']
        step = 10.0 if base_unit in ['g', 'ml'] else 1.0
        
        with quantity_col:
            quantity = st.number_input(
                f"Quantity ({base_unit})",
                min_value=0.0,
                value=quantities.get(food_name, {}).get('quantity', 0.0),
                step=step,
                key=f"{prefix}quantity_{index}"
            )
        
        if can_remove and remove_callback:
            with remove_col:
                if st.button("🗑️", key=f"{prefix}remove_{index}"):
                    remove_callback(prefix)
                    return None, None
            
        if quantity > 0:
            return food_name, {
                'quantity': quantity,
                'id': int(food_data['id']),
                'base_unit': base_unit
            }
    
    return None, None

def format_datetime(dt: Union[str, datetime], format_str: str = "%d/%m/%Y %H:%M:%S") -> str:
    """
    Format a datetime object or string to a display string.
    
    Args:
        dt: Datetime object or string
        format_str: Format string for strftime
        
    Returns:
        Formatted datetime string
    """
    if isinstance(dt, str):
        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")
    return dt.strftime(format_str)

def get_meal_selection(
    meals_df: pd.DataFrame,
    meal_categories: Dict[str, str],
    key_prefix: str = ""
) -> Tuple[Optional[str], Optional[str], Optional[pd.DataFrame]]:
    """
    Handle meal time and meal selection.
    
    Args:
        meals_df: DataFrame containing all meals
        meal_categories: Dict mapping meal times to meal categories
        key_prefix: Optional prefix for streamlit keys
        
    Returns:
        Tuple of (meal_time, meal_name, available_meals_df) or (None, None, None) if no meals available
    """
    col1, col2 = st.columns(2)
    
    with col1:
        meal_time = st.selectbox(
            "Meal Time", 
            list(meal_categories.keys()),
            key=f"{key_prefix}meal_time"
        )
    
    # Filter meals by appropriate category
    category = meal_categories[meal_time]
    available_meals = meals_df[meals_df['category'] == category]
    
    with col2:
        if not available_meals.empty:
            meal = st.selectbox(
                "Select Meal", 
                available_meals['name'].tolist(),
                key=f"{key_prefix}selected_meal"
            )
            return meal_time, meal, available_meals
        else:
            st.warning(f"No meals available for category: {category}")
            return None, None, None

def display_date_selection(
    min_date: datetime,
    max_date: datetime, 
    default_start: Optional[datetime] = None,
    default_end: Optional[datetime] = None
) -> Tuple[datetime, datetime]:
    """
    Display date range selection widgets.
    
    Args:
        min_date: Minimum allowed date
        max_date: Maximum allowed date
        default_start: Default start date (defaults to min_date)
        default_end: Default end date (defaults to min_date)
        
    Returns:
        Tuple of (start_date, end_date)
    """
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input(
            "From Date",
            min_value=min_date,
            max_value=max_date,
            value=default_start or min_date
        )
    with col2:
        end = st.date_input(
            "To Date",
            min_value=min_date,
            max_value=max_date,
            value=default_end or min_date
        )
    
    return start, end

def display_meal_info_card(
    meal: Dict[str, Any],
    show_buttons: bool = False,
    delete_callback: Optional[Callable] = None,
    view_callback: Optional[Callable] = None
) -> None:
    """
    Display a meal information card with optional action buttons.
    
    Args:
        meal: Dictionary containing meal data
        show_buttons: Whether to display action buttons
        delete_callback: Function to call when delete button is clicked
        view_callback: Function to call when view button is clicked
    """
    with st.container(border=True):
        st.subheader(meal['meal_name'])
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Display meal category and type
            st.caption(f"Category: {meal['category']} | Type: {meal['type'].capitalize()}")
            
            # Display macros in a compact format
            macros_text = (
                f"**Calories:** {meal.get('calories', 0):.0f} kcal | "
                f"**Protein:** {meal.get('proteins', 0):.1f}g | "
                f"**Carbs:** {meal.get('carbs', 0):.1f}g | "
                f"**Fat:** {meal.get('fats', 0):.1f}g"
            )
            st.markdown(macros_text)
            
            # For regular meals, show ingredients
            if meal['type'] == 'regular' and 'foods' in meal and meal['foods']:
                st.caption("Ingredients:")
                ingredients = ", ".join([
                    f"{food['name']} ({food['quantity']} {food['base_unit']})" 
                    for food in meal['foods']
                ])
                st.text(ingredients)
        
        # Display action buttons if requested
        if show_buttons and (delete_callback or view_callback):
            with col2:
                button_cols = st.columns(2)
                
                with button_cols[0]:
                    if view_callback and st.button("🔍", key=f"view_{meal['id']}"):
                        view_callback(meal)
                
                with button_cols[1]:
                    if delete_callback and st.button("🗑️", key=f"delete_{meal['id']}"):
                        delete_callback(meal['id'])

def create_donut_chart(
    values: List[float], 
    labels: List[str], 
    title: str = "Distribution", 
    colors: Optional[List[str]] = None
) -> go.Figure:
    """
    Create a donut chart with Plotly.
    
    Args:
        values: List of values for the chart
        labels: List of labels for each value
        title: Chart title
        colors: Optional list of colors for each segment
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        textinfo='percent+label'
    )])
    
    fig.update_layout(
        title_text=title,
        showlegend=False,
        height=300
    )
    
    if colors:
        fig.update_traces(marker=dict(colors=colors))
    
    return fig

def display_days_selection(key_prefix: str = "") -> List[int]:
    """
    Display weekday selection checkboxes and return selected days.
    
    Args:
        key_prefix: Prefix for session state keys
        
    Returns:
        List of selected day indices (0=Monday, 6=Sunday)
    """
    st.write("Apply to:")
    col1, col2, col3 = st.columns(3)
    with col1:
        monday = st.checkbox("Monday", key=f"{key_prefix}monday")
    with col2:
        tuesday = st.checkbox("Tuesday", key=f"{key_prefix}tuesday")
    with col3:
        wednesday = st.checkbox("Wednesday", key=f"{key_prefix}wednesday")
    col1, col2, col3 = st.columns(3)
    with col1:
        thursday = st.checkbox("Thursday", key=f"{key_prefix}thursday")
    with col2:
        friday = st.checkbox("Friday", key=f"{key_prefix}friday")
    with col3:
        weekend = st.checkbox("Weekend", key=f"{key_prefix}weekend")
        
    selected_days = []
    if monday: selected_days.append(0)
    if tuesday: selected_days.append(1)
    if wednesday: selected_days.append(2)
    if thursday: selected_days.append(3)
    if friday: selected_days.append(4)
    if weekend: selected_days.extend([5,6])
    
    return selected_days

def display_profile_card(profile: Tuple) -> None:
    """
    Display a profile information card.
    
    Args:
        profile: Profile tuple from database
    """
    if not profile:
        return
    
    with st.container(border=True):
        cols = st.columns([1, 1, 1])
        
        with cols[0]:
            st.metric("Weight", f"{profile[1]} kg")
        
        with cols[1]:
            st.metric("Height", f"{profile[2]} m")
            
        with cols[2]:
            st.metric("Age - Gender", f"{profile[3]} - {profile[5]}")
        
        # Second row with activity level and goal info
        cols = st.columns([1, 1, 1])
        
        with cols[0]:
            st.metric("Activity Level", profile[4])
            
        with cols[1]:
            st.metric("Goal Type", profile[6])
            
        with cols[2]:
            goal_label = "Deficit" if profile[6] == "Weight Loss" else "Surplus" if profile[6] == "Weight Gain" else "Maintenance"
            st.metric(f"{goal_label}", f"{profile[7]}%" if profile[7] else "0%")
            
        st.caption(f"Last updated: {format_datetime(profile[8], '%d %b %Y, %H:%M')}")

def create_pagination_controls(
    current_page: int,
    total_pages: int,
    on_previous: Callable,
    on_next: Callable,
    suffix: str = ""
) -> None:
    """
    Create pagination controls.
    
    Args:
        current_page: Current page index (0-based)
        total_pages: Total number of pages
        on_previous: Function to call when previous button is clicked
        on_next: Function to call when next button is clicked
    """
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("◀️ Previous", 
                   disabled=current_page == 0, 
                   key=f"previous_button_{suffix}",
                   use_container_width=True):
            on_previous()
    
    with col2:
        st.markdown(
            f"<div style='text-align: center;'><strong>Page {current_page + 1} of {total_pages}</strong></div>", 
            unsafe_allow_html=True
        )
    
    with col3:
        if st.button("Next ▶️", 
                   disabled=current_page >= total_pages - 1, 
                     key=f"next_button_{suffix}",
                   use_container_width=True):
            on_next()