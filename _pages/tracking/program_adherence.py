"""
Program Adherence page for the Nutrition App.

This page allows users to compare their planned meals from programs
with the actual meals they logged, showing compliance and nutrition differences.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.db_manager import NutritionDB
from utils.constants import MealTime
from utils.nutrition import (
    calculate_meal_macros_from_record, 
    calculate_all_metrics, 
    calculate_macro_targets
)
from utils.ui import (
    display_success_error,
    display_date_selection
)

# Initialize database
db = NutritionDB()

def apply_custom_tab_styling():
    """Apply custom CSS to make tabs larger, full-width, with more neutral colors and no content border"""
    custom_css = """
    <style>
        /* Make tabs container take full width */
        .stTabs {
            width: 100%;
        }
        
        /* Style the tab list to be full width */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            margin-bottom: 16px;
            width: 100%;
            display: flex;
        }
        
        /* Make each tab grow to fill the space */
        .stTabs [data-baseweb="tab"] {
            flex-grow: 1;
            height: 60px;
            white-space: pre-wrap;
            border-radius: 8px 8px 0px 0px;
            padding: 10px 16px;
            font-size: 16px;
            font-weight: 500;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            /* Adaptive colors based on theme */
            background-color: var(--background-color, #f0f2f6);
            border: 1px solid var(--border-color, #ced4da);
            border-bottom: none;
            color: var(--text-color, #262730);
        }
        
        /* Style for the active tab - theme adaptive with more neutral color */
        .stTabs [aria-selected="true"] {
            background-color: var(--primary-color, #4A6FFF) !important;
            color: white !important;
            font-weight: bold;
            border: 1px solid var(--primary-color, #4A6FFF);
            border-bottom: none;
            box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
        }
        
        /* Style the content container - removing border */
        .stTabs [data-baseweb="tab-panel"] {
            padding: 20px 0px 0px 0px;
            /* Removed borders */
            border: none;
            border-top: 2px solid var(--primary-color, #4A6FFF);
            border-radius: 0;
            background-color: transparent;
        }
        
        /* Adjust for light theme */
        [data-theme="light"] {
            --background-color: #f0f2f6;
            --border-color: #ced4da;
            --text-color: #262730;
            --primary-color: #4A6FFF; /* Blue instead of green */
        }
        
        /* Adjust for dark theme */
        [data-theme="dark"] {
            --background-color: #262730;
            --border-color: #555555;
            --text-color: #ffffff;
            --primary-color: #3D5BD9; /* Darker blue for dark mode */
        }
        
        /* Add hover effect for better user experience */
        .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
            background-color: var(--hover-color, #e6e6e6);
            cursor: pointer;
        }
        
        /* Ensure content in tabs is properly visible */
        .stTabs [data-baseweb="tab-panel"] > div {
            padding: 0;
        }
        
        /* Make text centered with any icons */
        .stTabs [data-baseweb="tab"] span {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def get_program_for_date_range(start_date, end_date):
    """Find a program that covers the given date range"""
    programs = db.get_all_programs()
    if programs.empty:
        return None
    
    # Convert dates to ensure consistent comparison
    if not isinstance(start_date, pd.Timestamp):
        start_date = pd.to_datetime(start_date)
    if not isinstance(end_date, pd.Timestamp):
        end_date = pd.to_datetime(end_date)
    
    # Convert program dates to datetime
    programs['start_date'] = pd.to_datetime(programs['start_date'])
    programs['end_date'] = pd.to_datetime(programs['end_date'])
    
    # Find programs that fully cover the date range
    covering_programs = programs[
        (programs['start_date'] <= start_date) & 
        (programs['end_date'] >= end_date)
    ]
    
    if covering_programs.empty:
        return None
    
    # Return the most recent program if multiple exist
    return covering_programs.sort_values('created_at', ascending=False).iloc[0]

def get_planned_meals(program_id, start_date, end_date):
    """
    Get planned meals for a specific program within a date range
    
    Args:
        program_id: The ID of the program
        start_date: Start date for the comparison
        end_date: End date for the comparison
        
    Returns:
        DataFrame with planned meals
    """
    program_meals = db.get_program_meals(program_id)
    if program_meals.empty:
        return pd.DataFrame()
    
    # Convert dates to ensure consistent comparison
    if not isinstance(start_date, pd.Timestamp):
        start_date = pd.to_datetime(start_date)
    if not isinstance(end_date, pd.Timestamp):
        end_date = pd.to_datetime(end_date)
    
    # Convert program meal dates to datetime
    program_meals['date'] = pd.to_datetime(program_meals['date'])
    
    # Filter by date range
    date_filtered = program_meals[
        (program_meals['date'] >= start_date) & 
        (program_meals['date'] <= end_date)
    ]
    
    return date_filtered

def get_tracked_meals(start_date, end_date):
    """
    Get tracked meals within a date range
    
    Args:
        start_date: Start date for the comparison
        end_date: End date for the comparison
        
    Returns:
        DataFrame with tracked meals
    """
    # Create date range
    date_range = pd.date_range(start_date, end_date)
    all_tracked_meals = []
    
    # Get tracked meals for each date
    for date in date_range:
        tracked_meals = db.get_tracked_meals(date)
        if not tracked_meals.empty:
            all_tracked_meals.append(tracked_meals)
    
    if not all_tracked_meals:
        return pd.DataFrame()
    
    # Combine all tracked meals
    return pd.concat(all_tracked_meals, ignore_index=True)

def calculate_daily_macros(meals_df, date_col='date'):
    """
    Calculate daily macro totals from meals
    
    Args:
        meals_df: DataFrame with meals
        date_col: Name of the date column
        
    Returns:
        DataFrame with daily macro totals
    """
    if meals_df.empty:
        return pd.DataFrame()
    
    # Ensure date is in datetime format
    meals_df[date_col] = pd.to_datetime(meals_df[date_col])
    
    # Group meals by date and calculate macro totals
    daily_data = []
    
    for date, date_meals in meals_df.groupby(date_col):
        daily_calories = 0
        daily_proteins = 0
        daily_carbs = 0
        daily_fats = 0
        
        for _, meal in date_meals.iterrows():
            # Calculate macros based on meal type
            macros = calculate_meal_macros_from_record(meal)
            daily_calories += macros['calories']
            daily_proteins += macros['proteins']
            daily_carbs += macros['carbs']
            daily_fats += macros['fats']
        
        # Add daily totals to the result
        daily_data.append({
            'date': date,
            'calories': round(daily_calories, 1),
            'proteins': round(daily_proteins, 1),
            'carbs': round(daily_carbs, 1),
            'fats': round(daily_fats, 1)
        })
    
    # Create DataFrame and sort by date
    return pd.DataFrame(daily_data).sort_values('date')

def calculate_meal_time_adherence(planned_meals, tracked_meals):
    """
    Calculate adherence percentage for each meal time
    
    Args:
        planned_meals: DataFrame with planned meals
        tracked_meals: DataFrame with tracked meals
        
    Returns:
        DataFrame with adherence percentages
    """
    if planned_meals.empty or tracked_meals.empty:
        return pd.DataFrame()
    
    # Convert dates to datetime
    planned_meals['date'] = pd.to_datetime(planned_meals['date'])
    tracked_meals['date'] = pd.to_datetime(tracked_meals['date'])
    
    # Initialize counters for each meal time
    meal_times = MealTime.as_list()
    adherence_data = {
        meal_time: {'planned': 0, 'tracked': 0} 
        for meal_time in meal_times
    }
    
    # Count planned meals by meal time
    for meal_time, group in planned_meals.groupby('meal_time'):
        if meal_time in adherence_data:
            adherence_data[meal_time]['planned'] = len(group)
    
    # Count tracked meals by meal time
    for meal_time, group in tracked_meals.groupby('meal_time'):
        if meal_time in adherence_data:
            adherence_data[meal_time]['tracked'] = len(group)
    
    # Calculate adherence percentages
    result = []
    for meal_time, counts in adherence_data.items():
        if counts['planned'] > 0:
            adherence = (counts['tracked'] / counts['planned']) * 100
            result.append({
                'meal_time': meal_time,
                'planned': counts['planned'],
                'tracked': counts['tracked'],
                'adherence': min(100, round(adherence, 1))  # Cap at 100%
            })
    
    return pd.DataFrame(result)

def display_date_range_selector(min_date, max_date):
    """Display date range selection with validation"""
    st.subheader("📅 Select Date Range for Comparison")
    
    # Calculate a default date range (last 7 days within the program)
    default_end = min(max_date, datetime.now().date())
    default_start = max(min_date, default_end - timedelta(days=6))
    
    # Date range selection
    start_date, end_date = display_date_selection(
        min_date=min_date,
        max_date=max_date,
        default_start=default_start,
        default_end=default_end
    )
    
    # Validate date range
    if end_date < start_date:
        st.error("End date must be after start date!")
        return None, None
    
    # Check if the date range is too long
    date_range = (end_date - start_date).days + 1
    if date_range > 30:
        st.warning("Date range is quite long (more than 30 days). Consider selecting a shorter period for better visualization.")
    
    return start_date, end_date

def display_program_selection():
    """Display program selection interface"""
    st.subheader("📋 Select Program")
    
    # Get all programs
    programs = db.get_all_programs()
    if programs.empty:
        st.info("No meal programs available. Please create a program first.")
        return None
    
    # Create a DataFrame for display
    display_df = pd.DataFrame({
        "Program Name": programs['name'],
        "Start Date": pd.to_datetime(programs['start_date']).dt.strftime('%d-%m-%Y'),
        "End Date": pd.to_datetime(programs['end_date']).dt.strftime('%d-%m-%Y'),
        "Duration": (pd.to_datetime(programs['end_date']) - pd.to_datetime(programs['start_date'])).dt.days + 1
    })
    
    # Display programs table
    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True
    )
    
    # Program selection
    selected_program = st.selectbox(
        "Choose a program to analyze",
        programs['name'].tolist(),
        key="program_selector"
    )
    
    # Get the selected program data
    program_data = programs[programs['name'] == selected_program].iloc[0]
    
    return program_data

def display_calorie_comparison_chart(planned_daily, tracked_daily):
    """Display chart comparing planned vs actual calories"""
    if planned_daily.empty or tracked_daily.empty:
        return
    
    # Merge data on date
    merged_data = pd.merge(
        planned_daily[['date', 'calories']].rename(columns={'calories': 'planned_calories'}),
        tracked_daily[['date', 'calories']].rename(columns={'calories': 'tracked_calories'}),
        on='date',
        how='outer'
    )
    
    # Fill NaN values with 0
    merged_data = merged_data.fillna(0)
    
    # Create figure
    fig = go.Figure()
    
    # Add planned calories line
    fig.add_trace(go.Scatter(
        x=merged_data['date'],
        y=merged_data['planned_calories'],
        mode='lines+markers',
        name='Planned Calories',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    # Add tracked calories line
    fig.add_trace(go.Scatter(
        x=merged_data['date'],
        y=merged_data['tracked_calories'],
        mode='lines+markers',
        name='Actual Calories',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=8)
    ))
    
    # Calculate difference as a line
    merged_data['difference'] = merged_data['tracked_calories'] - merged_data['planned_calories']
    merged_data['zero_line'] = 0
    
    # Create a secondary y-axis for the difference
    fig.add_trace(go.Bar(
        x=merged_data['date'],
        y=merged_data['difference'],
        name='Difference',
        marker=dict(
            color=merged_data['difference'].apply(
                lambda x: 'rgba(255, 0, 0, 0.5)' if x < 0 else 'rgba(0, 128, 0, 0.5)'
            )
        ),
        opacity=0.5,
        yaxis='y2'
    ))
    
    # Update layout with dual y-axis
    fig.update_layout(
        title='Daily Calories: Planned vs. Actual',
        xaxis_title='Date',
        yaxis_title='Calories (kcal)',
        yaxis2=dict(
            title='Difference (kcal)',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Show chart
    st.plotly_chart(fig, use_container_width=True)

def display_macros_comparison_chart(planned_daily, tracked_daily):
    """Display chart comparing planned vs actual macros"""
    if planned_daily.empty or tracked_daily.empty:
        return
    
    # Calculate averages for both datasets
    planned_avg = {
        'calories': planned_daily['calories'].mean(),
        'proteins': planned_daily['proteins'].mean(),
        'carbs': planned_daily['carbs'].mean(),
        'fats': planned_daily['fats'].mean()
    }
    
    tracked_avg = {
        'calories': tracked_daily['calories'].mean(),
        'proteins': tracked_daily['proteins'].mean(),
        'carbs': tracked_daily['carbs'].mean(),
        'fats': tracked_daily['fats'].mean()
    }
    
    # Create data for grouped bar chart
    macro_labels = ['Calories (÷10)', 'Protein (g)', 'Carbs (g)', 'Fat (g)']
    planned_values = [
        planned_avg['calories'] / 10,  # Scale down calories for better visualization
        planned_avg['proteins'],
        planned_avg['carbs'],
        planned_avg['fats']
    ]
    
    tracked_values = [
        tracked_avg['calories'] / 10,  # Scale down calories for better visualization
        tracked_avg['proteins'],
        tracked_avg['carbs'],
        tracked_avg['fats']
    ]
    
    # Adherence percentages
    adherence = [
        (tracked_avg['calories'] / planned_avg['calories'] * 100) if planned_avg['calories'] > 0 else 0,
        (tracked_avg['proteins'] / planned_avg['proteins'] * 100) if planned_avg['proteins'] > 0 else 0,
        (tracked_avg['carbs'] / planned_avg['carbs'] * 100) if planned_avg['carbs'] > 0 else 0,
        (tracked_avg['fats'] / planned_avg['fats'] * 100) if planned_avg['fats'] > 0 else 0
    ]
    
    # Create figure for macros comparison
    fig = go.Figure()
    
    # Add bars for planned and tracked macros
    fig.add_trace(go.Bar(
        x=macro_labels,
        y=planned_values,
        name='Planned',
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        x=macro_labels,
        y=tracked_values,
        name='Actual',
        marker_color='#ff7f0e'
    ))
    
    # Update layout
    fig.update_layout(
        title='Average Daily Macros: Planned vs. Actual',
        xaxis_title='Macronutrient',
        yaxis_title='Amount',
        barmode='group',
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Show chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Display adherence metrics
    st.subheader("📊 Macro Adherence Percentages")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Calories",
            f"{min(round(adherence[0], 1), 200)}%",
            delta=f"{round(tracked_avg['calories'] - planned_avg['calories'], 0)} kcal"
        )
    
    with col2:
        st.metric(
            "Protein",
            f"{min(round(adherence[1], 1), 200)}%",
            delta=f"{round(tracked_avg['proteins'] - planned_avg['proteins'], 1)}g"
        )
    
    with col3:
        st.metric(
            "Carbs",
            f"{min(round(adherence[2], 1), 200)}%",
            delta=f"{round(tracked_avg['carbs'] - planned_avg['carbs'], 1)}g"
        )
    
    with col4:
        st.metric(
            "Fat",
            f"{min(round(adherence[3], 1), 200)}%",
            delta=f"{round(tracked_avg['fats'] - planned_avg['fats'], 1)}g"
        )

def display_meal_time_adherence_chart(adherence_df):
    """Display chart showing adherence by meal time"""
    if adherence_df.empty:
        return
    
    # Create a bar chart for meal time adherence
    fig = px.bar(
        adherence_df,
        x='meal_time',
        y='adherence',
        color='adherence',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100],
        labels={
            'meal_time': 'Meal Time',
            'adherence': 'Adherence (%)'
        },
        text='adherence'
    )
    
    # Add text to show planned vs tracked counts
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    
    # Update layout
    fig.update_layout(
        title='Meal Time Adherence: Tracked vs. Planned Meals',
        xaxis_title='Meal Time',
        yaxis_title='Adherence (%)',
        yaxis_range=[0, 110],  # Give some space above 100%
        coloraxis_showscale=False,
        height=400
    )
    
    # Add annotations for planned vs tracked counts
    for i, row in enumerate(adherence_df.itertuples()):
        fig.add_annotation(
            x=row.meal_time,
            y=20,
            text=f"({row.tracked}/{row.planned})",
            showarrow=False,
            font=dict(size=10, color="black")
        )
    
    # Show chart
    st.plotly_chart(fig, use_container_width=True)

def display_compliance_table(planned_daily, tracked_daily):
    """Display a detailed compliance table by day"""
    if planned_daily.empty or tracked_daily.empty:
        return
    
    # Merge data on date
    merged_data = pd.merge(
        planned_daily,
        tracked_daily,
        on='date',
        how='outer',
        suffixes=('_planned', '_tracked')
    )
    
    # Fill NaN values with 0
    merged_data = merged_data.fillna(0)
    
    # Calculate compliance percentages for each macro
    merged_data['calories_compliance'] = (merged_data['calories_tracked'] / merged_data['calories_planned'] * 100).apply(lambda x: min(x, 100) if x > 0 else 0)
    merged_data['proteins_compliance'] = (merged_data['proteins_tracked'] / merged_data['proteins_planned'] * 100).apply(lambda x: min(x, 100) if x > 0 else 0)
    merged_data['carbs_compliance'] = (merged_data['carbs_tracked'] / merged_data['carbs_planned'] * 100).apply(lambda x: min(x, 100) if x > 0 else 0)
    merged_data['fats_compliance'] = (merged_data['fats_tracked'] / merged_data['fats_planned'] * 100).apply(lambda x: min(x, 100) if x > 0 else 0)
    
    # Calculate an overall compliance score
    merged_data['overall_compliance'] = (
        merged_data['calories_compliance'] * 0.25 +
        merged_data['proteins_compliance'] * 0.35 +  # Higher weight for protein
        merged_data['carbs_compliance'] * 0.2 +
        merged_data['fats_compliance'] * 0.2
    )
    
    # Prepare data for display
    display_df = pd.DataFrame({
        'Date': merged_data['date'].dt.strftime('%a, %b %d'),
        'Overall': merged_data['overall_compliance'].round(1),
        'Calories': merged_data['calories_compliance'].round(1),
        'Protein': merged_data['proteins_compliance'].round(1),
        'Carbs': merged_data['carbs_compliance'].round(1),
        'Fat': merged_data['fats_compliance'].round(1)
    })
    
    # Add summary row with averages
    avg_row = pd.DataFrame({
        'Date': ['AVERAGE'],
        'Overall': [display_df['Overall'].mean()],
        'Calories': [display_df['Calories'].mean()],
        'Protein': [display_df['Protein'].mean()],
        'Carbs': [display_df['Carbs'].mean()],
        'Fat': [display_df['Fat'].mean()]
    })
    
    display_df = pd.concat([display_df, avg_row], ignore_index=True)
    
    # Create a stylized table
    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Date": st.column_config.TextColumn(
                "Date",
                width="medium"
            ),
            "Overall": st.column_config.ProgressColumn(
                "Overall Compliance",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "Calories": st.column_config.ProgressColumn(
                "Calories",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "Protein": st.column_config.ProgressColumn(
                "Protein",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "Carbs": st.column_config.ProgressColumn(
                "Carbs",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "Fat": st.column_config.ProgressColumn(
                "Fat",
                format="%.1f%%",
                min_value=0,
                max_value=100
            )
        }
    )

def display_meal_comparison(planned_meals, tracked_meals):
    """
    Display a detailed comparison between planned meals and tracked meals.
    
    Args:
        planned_meals: DataFrame with planned meals
        tracked_meals: DataFrame with tracked meals
    """
    if planned_meals.empty or tracked_meals.empty:
        st.info("Not enough data for meal comparison. Make sure you have both planned and tracked meals.")
        return
    
    # Convert dates to datetime format for consistent comparison
    planned_meals['date'] = pd.to_datetime(planned_meals['date'])
    tracked_meals['date'] = pd.to_datetime(tracked_meals['date'])
    
    # Get all unique dates that have either planned or tracked meals
    all_dates = pd.concat([
        planned_meals['date'].drop_duplicates(),
        tracked_meals['date'].drop_duplicates()
    ]).drop_duplicates().sort_values()
    
    # Create a date selector
    date_options = all_dates.dt.strftime('%A, %b %d, %Y').tolist()
    date_selection = st.selectbox(
        "📅 Select a date to compare meals:",
        date_options
    )
    
    # Convert the selected date string back to datetime
    selected_date = pd.to_datetime(date_selection, format='%A, %b %d, %Y')
    selected_date_str = selected_date.strftime('%Y-%m-%d')
    
    # Filter meals for the selected date
    day_planned_meals = planned_meals[planned_meals['date'].dt.strftime('%Y-%m-%d') == selected_date_str]
    day_tracked_meals = tracked_meals[tracked_meals['date'].dt.strftime('%Y-%m-%d') == selected_date_str]
    
    # Display summary metrics for the day
    st.subheader(f"📊 Day Summary: {date_selection}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        planned_count = len(day_planned_meals)
        st.metric("Planned Meals", planned_count)
    
    with col2:
        tracked_count = len(day_tracked_meals)
        st.metric("Tracked Meals", tracked_count)
    
    with col3:
        if planned_count > 0:
            # Calculate a simple adherence metric
            followed = 0
            for _, planned_meal in day_planned_meals.iterrows():
                # Check if this meal time has a tracked meal with the same name
                matching_meals = day_tracked_meals[
                    (day_tracked_meals['meal_time'] == planned_meal['meal_time']) & 
                    (day_tracked_meals['meal_name'] == planned_meal['meal_name'])
                ]
                if not matching_meals.empty:
                    followed += 1
            
            adherence = (followed / planned_count) * 100
            st.metric("Meal Adherence", f"{adherence:.1f}%")
        else:
            st.metric("Meal Adherence", "N/A")
    
    # Divider before meal comparison
    st.divider()
    
    # Create a map of meal times to their order for sorting
    meal_time_order = {meal_time: i for i, meal_time in enumerate(MealTime.as_list())}
    
    # Process all meal times to show planned and tracked status
    all_meal_times = set(MealTime.as_list())
    processed_meal_times = set()
    
    # Get all unique meal times that have either planned or tracked meals for this day
    day_meal_times = set(day_planned_meals['meal_time'].unique()) | set(day_tracked_meals['meal_time'].unique())
    
    # Sort meal times according to the defined order
    sorted_meal_times = sorted(day_meal_times, key=lambda x: meal_time_order.get(x, 999))
    
    # Counter for expanding detailed comparisons
    comparison_counter = 0
    
    for meal_time in sorted_meal_times:
        # Get planned and tracked meals for this meal time
        time_planned_meals = day_planned_meals[day_planned_meals['meal_time'] == meal_time]
        time_tracked_meals = day_tracked_meals[day_tracked_meals['meal_time'] == meal_time]
        
        # Special styling for the meal time header
        st.markdown(f"### ⏰ {meal_time}")
        
        # Handle different scenarios:
        # 1. Planned and tracked with same name (Followed)
        # 2. Planned and tracked with different name (Substituted)
        # 3. Planned but not tracked (Missed)
        # 4. Not planned but tracked (Extra)
        
        # Check if we have both planned and tracked meals
        if not time_planned_meals.empty and not time_tracked_meals.empty:
            # Check if there's an exact match (followed the plan)
            exact_matches = pd.merge(
                time_planned_meals, 
                time_tracked_meals,
                on=['meal_time', 'meal_name'],
                how='inner',
                suffixes=('_planned', '_tracked')
            )
            
            # Display followed meals
            for _, match in exact_matches.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**✅ Followed: {match['meal_name']}**")
                        st.caption(f"Category: {match['category_planned']}")
                    
                    comparison_counter += 1
                    with col2:
                        if st.button("📊 Compare", key=f"compare_followed_{comparison_counter}"):
                            # Display detailed comparison for followed meal
                            st.session_state[f"expanded_comparison_{comparison_counter}"] = True
                    
                    # Show detailed comparison if expanded
                    if f"expanded_comparison_{comparison_counter}" in st.session_state and st.session_state[f"expanded_comparison_{comparison_counter}"]:
                        # Get macros for both planned and tracked meals
                        planned_meal = time_planned_meals[time_planned_meals['meal_name'] == match['meal_name']].iloc[0]
                        planned_macros = calculate_meal_macros_from_record(planned_meal)

                        # Find the full tracked meal record
                        tracked_meal = time_tracked_meals[time_tracked_meals['meal_name'] == match['meal_name']].iloc[0]
                        tracked_macros = calculate_meal_macros_from_record(tracked_meal)
                        
                        # Display the comparison in columns
                        st.divider()
                        macro_comparison_columns(planned_macros, tracked_macros)
            
            # Handle substituted meals
            for _, planned_meal in time_planned_meals.iterrows():
                # Skip meals that were already matched exactly
                if not exact_matches.empty and any(exact_matches['meal_name'] == planned_meal['meal_name']):
                    continue
                
                # This planned meal was substituted with something else
                with st.container(border=True):
                    # If there's a tracked meal for this time but with a different name
                    if not time_tracked_meals.empty:
                        # Get the first tracked meal as the substitute (could be multiple)
                        tracked_meal = time_tracked_meals.iloc[0]
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**🔄 Substituted: {planned_meal['meal_name']} → {tracked_meal['meal_name']}**")
                            st.caption(f"Original category: {planned_meal['category']} | Actual category: {tracked_meal['category']}")
                        
                        comparison_counter += 1
                        with col2:
                            if st.button("📊 Compare", key=f"compare_substituted_{comparison_counter}"):
                                st.session_state[f"expanded_comparison_{comparison_counter}"] = True
                        
                        # Show detailed comparison if expanded
                        if f"expanded_comparison_{comparison_counter}" in st.session_state and st.session_state[f"expanded_comparison_{comparison_counter}"]:
                            # Get macros for both planned and tracked meals
                            planned_macros = calculate_meal_macros_from_record(planned_meal)
                            tracked_macros = calculate_meal_macros_from_record(tracked_meal)
                            
                            # Display the comparison in columns
                            st.divider()
                            macro_comparison_columns(planned_macros, tracked_macros)
                            
                            # Add warnings for significant differences
                            if tracked_macros['calories'] > planned_macros['calories'] * 1.2:  # 20% more calories
                                st.warning(f"⚠️ The substituted meal has {tracked_macros['calories'] - planned_macros['calories']:.0f} more calories than planned.")
                            
                            if tracked_macros['proteins'] < planned_macros['proteins'] * 0.8:  # 20% less protein
                                st.warning(f"⚠️ The substituted meal has {planned_macros['proteins'] - tracked_macros['proteins']:.1f}g less protein than planned.")
                    else:
                        # No tracked meal at all for this time (missed)
                        st.markdown(f"**⚠️ Missed: {planned_meal['meal_name']}**")
                        st.caption(f"Category: {planned_meal['category']}")
        
        # Handle meals that were planned but not tracked (missed)
        elif not time_planned_meals.empty and time_tracked_meals.empty:
            for _, meal in time_planned_meals.iterrows():
                with st.container(border=True):
                    st.markdown(f"**⚠️ Missed: {meal['meal_name']}**")
                    st.caption(f"Category: {meal['category']}")
        
        # Handle meals that were tracked but not planned (extra)
        elif time_planned_meals.empty and not time_tracked_meals.empty:
            for _, meal in time_tracked_meals.iterrows():
                with st.container(border=True):
                    st.markdown(f"**➕ Extra: {meal['meal_name']}**")
                    st.caption(f"Category: {meal['category']}")
                    
                    comparison_counter += 1
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("📊 Details", key=f"details_extra_{comparison_counter}"):
                            st.session_state[f"expanded_comparison_{comparison_counter}"] = True
                    
                    # Show detailed comparison if expanded
                    if f"expanded_comparison_{comparison_counter}" in st.session_state and st.session_state[f"expanded_comparison_{comparison_counter}"]:
                        # Get macros for the tracked meal
                        tracked_macros = calculate_meal_macros_from_record(meal)
                        
                        # Display the details
                        st.divider()
                        st.subheader("Nutritional Content")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Calories", f"{tracked_macros['calories']:.0f} kcal")
                        with col2:
                            st.metric("Protein", f"{tracked_macros['proteins']:.1f}g")
                        with col3:
                            st.metric("Carbs", f"{tracked_macros['carbs']:.1f}g")
                        with col4:
                            st.metric("Fat", f"{tracked_macros['fats']:.1f}g")

def macro_comparison_columns(planned_macros, tracked_macros):
    """Helper function to display macro comparison in columns"""
    st.subheader("Nutritional Comparison")
    
    # Calculate percentage differences
    calories_diff = ((tracked_macros['calories'] - planned_macros['calories']) / planned_macros['calories'] * 100) if planned_macros['calories'] > 0 else 0
    protein_diff = ((tracked_macros['proteins'] - planned_macros['proteins']) / planned_macros['proteins'] * 100) if planned_macros['proteins'] > 0 else 0
    carbs_diff = ((tracked_macros['carbs'] - planned_macros['carbs']) / planned_macros['carbs'] * 100) if planned_macros['carbs'] > 0 else 0
    fats_diff = ((tracked_macros['fats'] - planned_macros['fats']) / planned_macros['fats'] * 100) if planned_macros['fats'] > 0 else 0
    
    # Create a table-like display with columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**Calories**")
        st.markdown(f"Planned: {planned_macros['calories']:.0f} kcal")
        st.markdown(f"Actual: {tracked_macros['calories']:.0f} kcal")
        diff_color = "red" if calories_diff > 0 else "green" if calories_diff < 0 else "gray"
        st.markdown(f"<span style='color:{diff_color}'>Difference: {calories_diff:+.1f}%</span>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Protein**")
        st.markdown(f"Planned: {planned_macros['proteins']:.1f}g")
        st.markdown(f"Actual: {tracked_macros['proteins']:.1f}g")
        diff_color = "green" if protein_diff > 0 else "red" if protein_diff < 0 else "gray"
        st.markdown(f"<span style='color:{diff_color}'>Difference: {protein_diff:+.1f}%</span>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("**Carbs**")
        st.markdown(f"Planned: {planned_macros['carbs']:.1f}g")
        st.markdown(f"Actual: {tracked_macros['carbs']:.1f}g")
        diff_color = "red" if carbs_diff > 10 else "green" if carbs_diff < -10 else "gray"
        st.markdown(f"<span style='color:{diff_color}'>Difference: {carbs_diff:+.1f}%</span>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("**Fat**")
        st.markdown(f"Planned: {planned_macros['fats']:.1f}g")
        st.markdown(f"Actual: {tracked_macros['fats']:.1f}g")
        diff_color = "red" if fats_diff > 10 else "green" if fats_diff < -10 else "gray"
        st.markdown(f"<span style='color:{diff_color}'>Difference: {fats_diff:+.1f}%</span>", unsafe_allow_html=True)

def main():
    """Main function for the Program Adherence page"""
    st.title("📊 Program Adherence Analysis")

    # Apply custom tab styling
    apply_custom_tab_styling()

    # Display any success/error messages
    display_success_error()
    
    # Program selection
    program_data = display_program_selection()
    if program_data is None:
        return
    
    # Display program dates
    start_date = pd.to_datetime(program_data['start_date']).date()
    end_date = pd.to_datetime(program_data['end_date']).date()
    program_id = int(program_data['id'])
    
    # Date range selection
    st.divider()
    compare_start, compare_end = display_date_range_selector(start_date, end_date)
    if compare_start is None or compare_end is None:
        return
    
    # Load planned and tracked meals
    planned_meals = get_planned_meals(program_id, compare_start, compare_end)
    tracked_meals = get_tracked_meals(compare_start, compare_end)
    
    if planned_meals.empty:
        st.warning("No planned meals found in the selected date range!")
        return
    
    if tracked_meals.empty:
        st.warning("No tracked meals found in the selected date range!")
        return
    
    # Display tabs for different analysis views
    tab1, tab2, tab3 = st.tabs(["Nutrition Analysis", "Daily Compliance", "Meal Comparison"])
    
    with tab1:
        # Calculate daily macros for both datasets
        planned_daily = calculate_daily_macros(planned_meals)
        tracked_daily = calculate_daily_macros(tracked_meals)
        
        # Calculate meal time adherence
        adherence_df = calculate_meal_time_adherence(planned_meals, tracked_meals)
        
        # Display analysis sections
        st.subheader("📈 Calorie Comparison")
        display_calorie_comparison_chart(planned_daily, tracked_daily)
        
        st.divider()
        st.subheader("🥗 Macronutrient Comparison")
        display_macros_comparison_chart(planned_daily, tracked_daily)
        
        # Divider for meal time adherence section
        st.divider()
        st.subheader("⏰ Meal Time Analysis")
        
        if not adherence_df.empty:
            display_meal_time_adherence_chart(adherence_df)
        else:
            st.info("Not enough data to analyze meal time adherence.")
    
    with tab2:
        # Calculate daily macros for both datasets
        planned_daily = calculate_daily_macros(planned_meals)
        tracked_daily = calculate_daily_macros(tracked_meals)
        
        # Daily compliance table
        st.subheader("📅 Daily Compliance Report")
        
        if not planned_daily.empty and not tracked_daily.empty:
            display_compliance_table(planned_daily, tracked_daily)
        else:
            st.info("Not enough data for a daily compliance report.")
    
    with tab3:
        # Detailed meal comparison
        st.subheader("🍽️ Meal-by-Meal Comparison")
        display_meal_comparison(planned_meals, tracked_meals)
    
    # Helpful information
    with st.expander("💡 Understanding Your Adherence Report"):
        st.markdown("""
        ### How to Interpret Your Results
        
        1. **Calorie Comparison**: The chart shows your planned vs. actual calorie intake for each day. The bars show the difference, with red indicating under-consumption and green indicating over-consumption relative to your plan.
        
        2. **Macronutrient Comparison**: This chart compares your average planned vs. actual macronutrient intake. The adherence percentages show how closely you followed your nutrition plan.
        
        3. **Meal Time Analysis**: This chart shows your adherence to the meal schedule. The percentage represents how many planned meals you actually tracked for each meal time.
        
        4. **Daily Compliance Report**: This table provides a detailed day-by-day breakdown of your compliance in each area. The overall score weighs protein adherence slightly higher due to its importance in nutrition planning.
        
        5. **Meal-by-Meal Comparison**: This detailed view shows exactly which meals you followed from your plan and which ones you substituted or missed for each day.
        
        ### Tips for Improving Adherence
        
        - **Missing Meals**: If you notice low adherence for specific meal times, try setting reminders.
        
        - **Macro Mismatches**: If you're consistently over or under certain macros, consider adjusting your meal program.
        
        - **Day-to-Day Variation**: Look for patterns of good and bad days to identify potential lifestyle factors affecting your adherence.
        
        - **Regular Tracking**: Consistent meal tracking is essential for accurate adherence analysis.
        """)

# Run the main function when this page is loaded
main()