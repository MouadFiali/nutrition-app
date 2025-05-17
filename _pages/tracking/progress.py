"""
Progress Tracking page for the Nutrition App.

This page allows users to view their nutritional progress over time.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.db_manager import NutritionDB
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

def load_tracked_data(start_date, end_date):
    """Load tracked meal data for the selected date range"""
    # Create date range and initialize empty list for tracked meals
    date_range = pd.date_range(start_date, end_date, freq='D')
    all_tracked_meals = []
    
    # Fetch tracked meals for each date
    for date in date_range:
        tracked_meals = db.get_tracked_meals(date)
        if not tracked_meals.empty:
            all_tracked_meals.append(tracked_meals)
    
    if not all_tracked_meals:
        return pd.DataFrame()
    
    # Combine all tracked meals
    return pd.concat(all_tracked_meals, ignore_index=True)

def calculate_daily_totals(tracked_meals):
    """Calculate daily nutritional totals from tracked meals"""
    if tracked_meals.empty:
        return pd.DataFrame()
    
    # Add date column in datetime format
    tracked_meals['date_dt'] = pd.to_datetime(tracked_meals['date'])
    
    # Initialize daily totals dataframe
    daily_data = []
    
    # Group by date
    for date, meals in tracked_meals.groupby('date'):
        daily_calories = 0
        daily_proteins = 0
        daily_carbs = 0
        daily_fats = 0
        
        for _, meal in meals.iterrows():
            # Calculate macros based on meal type
            if meal['type'] == 'custom':
                daily_calories += meal['calories']
                daily_proteins += meal['proteins']
                daily_carbs += meal['carbs']
                daily_fats += meal['fats']
            elif meal['type'] == 'regular' and 'foods' in meal and meal['foods']:
                macros = calculate_meal_macros_from_record(meal)
                daily_calories += macros['calories']
                daily_proteins += macros['proteins']
                daily_carbs += macros['carbs']
                daily_fats += macros['fats']
        
        # Add daily totals to dataframe
        daily_data.append({
            'date': pd.to_datetime(date),
            'calories': round(daily_calories, 1),
            'proteins': round(daily_proteins, 1),
            'carbs': round(daily_carbs, 1),
            'fats': round(daily_fats, 1)
        })
    
    # Convert to dataframe and sort by date
    daily_df = pd.DataFrame(daily_data)
    daily_df = daily_df.sort_values('date')
    
    return daily_df

def display_calorie_chart(daily_data, target_calories):
    """Display chart of daily calories vs target"""
    # Create figure
    fig = go.Figure()
    
    # Add calories line
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['calories'],
        mode='lines+markers',
        name='Daily Calories',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    # Add target line
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=[target_calories] * len(daily_data),
        mode='lines',
        name='Target Calories',
        line=dict(color='rgba(255, 0, 0, 0.5)', width=2, dash='dash')
    ))
    
    # Update layout
    fig.update_layout(
        title='Daily Calories vs Target',
        xaxis_title='Date',
        yaxis_title='Calories (kcal)',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Show chart
    st.plotly_chart(fig, use_container_width=True)

def display_macros_chart(daily_data, protein_target, carbs_target, fats_target):
    """Display chart of daily macros vs targets"""
    # Create figure
    fig = go.Figure()
    
    # Add protein line
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['proteins'],
        mode='lines+markers',
        name='Protein (g)',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=8)
    ))
    
    # Add carbs line
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['carbs'],
        mode='lines+markers',
        name='Carbs (g)',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=8)
    ))
    
    # Add fats line
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['fats'],
        mode='lines+markers',
        name='Fats (g)',
        line=dict(color='#d62728', width=3),
        marker=dict(size=8)
    ))
    
    # Add target lines
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=[protein_target] * len(daily_data),
        mode='lines',
        name='Protein Target',
        line=dict(color='rgba(44, 160, 44, 0.5)', width=2, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=[carbs_target] * len(daily_data),
        mode='lines',
        name='Carbs Target',
        line=dict(color='rgba(255, 127, 14, 0.5)', width=2, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=[fats_target] * len(daily_data),
        mode='lines',
        name='Fats Target',
        line=dict(color='rgba(214, 39, 40, 0.5)', width=2, dash='dash')
    ))
    
    # Update layout
    fig.update_layout(
        title='Daily Macronutrients vs Targets',
        xaxis_title='Date',
        yaxis_title='Grams',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Show chart
    st.plotly_chart(fig, use_container_width=True)

def display_macro_distribution_chart(daily_data):
    """Display chart of macro distribution percentages"""
    if daily_data.empty:
        return
    
    # Calculate macro distribution percentages
    daily_data['protein_cals'] = daily_data['proteins'] * 4
    daily_data['carb_cals'] = daily_data['carbs'] * 4
    daily_data['fat_cals'] = daily_data['fats'] * 9
    
    daily_data['protein_pct'] = (daily_data['protein_cals'] / daily_data['calories'] * 100).round(1)
    daily_data['carb_pct'] = (daily_data['carb_cals'] / daily_data['calories'] * 100).round(1)
    daily_data['fat_pct'] = (daily_data['fat_cals'] / daily_data['calories'] * 100).round(1)
    
    # Create stacked area chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['protein_pct'],
        mode='lines',
        name='Protein %',
        line=dict(width=0),
        stackgroup='one',
        fillcolor='rgba(44, 160, 44, 0.7)'
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['carb_pct'],
        mode='lines',
        name='Carbs %',
        line=dict(width=0),
        stackgroup='one',
        fillcolor='rgba(255, 127, 14, 0.7)'
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['fat_pct'],
        mode='lines',
        name='Fat %',
        line=dict(width=0),
        stackgroup='one',
        fillcolor='rgba(214, 39, 40, 0.7)'
    ))
    
    # Update layout
    fig.update_layout(
        title='Daily Macro Distribution',
        xaxis_title='Date',
        yaxis_title='Percentage of Total Calories',
        hovermode='x unified',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Show chart
    st.plotly_chart(fig, use_container_width=True)

def display_daily_totals_table(daily_data):
    """Display table of daily nutrition totals"""
    if daily_data.empty:
        return
    
    # Format dataframe for display
    display_df = daily_data.copy()
    display_df['date'] = display_df['date'].dt.strftime('%a, %b %d')
    
    # Rename columns
    display_df = display_df.rename(columns={
        'date': 'Date',
        'calories': 'Calories (kcal)',
        'proteins': 'Protein (g)',
        'carbs': 'Carbs (g)',
        'fats': 'Fat (g)'
    })
    
    # Display table
    st.subheader("📋 Daily Nutrition Totals")
    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Calories (kcal)": st.column_config.NumberColumn(format="%.0f"),
            "Protein (g)": st.column_config.NumberColumn(format="%.1f"),
            "Carbs (g)": st.column_config.NumberColumn(format="%.1f"),
            "Fat (g)": st.column_config.NumberColumn(format="%.1f")
        }
    )

def main():
    """Main function for the Progress Tracking page"""
    st.title("📈 Track Your Progress")
    
    # Display any success/error messages
    display_success_error()
    
    # Load profile and targets
    profile_targets = load_profile_and_targets()
    
    if not profile_targets[0]:
        st.warning("Please set up your profile first!")
        return
    
    # Unpack targets
    _, target_calories, protein_target, carbs_target, fats_target = profile_targets
    
    # Date range selection
    st.subheader("📅 Select Date Range")
    
    # Default to last 7 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    start_date, end_date = display_date_selection(
        min_date=end_date - timedelta(days=90),
        max_date=end_date,
        default_start=start_date,
        default_end=end_date
    )
    
    # Ensure date range is valid
    if end_date < start_date:
        st.error("End date must be after start date")
        return
    
    # Calculate date range duration
    days_in_range = (end_date - start_date).days + 1
    
    # Load tracked data
    tracked_meals = load_tracked_data(start_date, end_date)
    
    if tracked_meals.empty:
        st.info(f"No tracked meals found for the selected date range ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})")
        return
    
    # Calculate daily totals
    daily_data = calculate_daily_totals(tracked_meals)
    
    if daily_data.empty:
        st.info("No nutritional data available for the selected date range")
        return
    
    # Display summary metrics
    st.subheader("📊 Nutrition Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_calories = daily_data['calories'].mean()
        st.metric(
            "Average Calories", 
            f"{avg_calories:.0f} kcal",
            f"{(avg_calories/target_calories*100):.0f}% of target"
        )
    
    with col2:
        avg_protein = daily_data['proteins'].mean()
        st.metric(
            "Average Protein", 
            f"{avg_protein:.1f}g",
            f"{(avg_protein/protein_target*100):.0f}% of target"
        )
    
    with col3:
        avg_carbs = daily_data['carbs'].mean()
        st.metric(
            "Average Carbs", 
            f"{avg_carbs:.1f}g",
            f"{(avg_carbs/carbs_target*100):.0f}% of target"
        )
    
    with col4:
        avg_fat = daily_data['fats'].mean()
        st.metric(
            "Average Fat", 
            f"{avg_fat:.1f}g",
            f"{(avg_fat/fats_target*100):.0f}% of target"
        )
    
    # Display charts
    st.divider()
    
    # Calories chart
    display_calorie_chart(daily_data, target_calories)
    
    # Macros chart
    display_macros_chart(daily_data, protein_target, carbs_target, fats_target)
    
    # Macro distribution chart
    display_macro_distribution_chart(daily_data)
    
    # Daily totals table
    st.divider()
    display_daily_totals_table(daily_data)
    
    # Show helpful information
    with st.expander("💡 Understanding Your Progress"):
        st.markdown("""
        ### Interpreting Your Nutrition Data
        
        1. **Calorie Tracking**: Compare your daily calories to your target to see if you're consistently over or under your goal.
        
        2. **Macro Balance**: Look at your macro distribution to ensure you're getting a balanced diet with adequate protein.
        
        3. **Trends Over Time**: Focus on overall trends rather than day-to-day fluctuations.
        
        4. **Consistency**: Check how many days you tracked completely vs. partially to ensure your data is accurate.
        
        ### Using This Page
        
        - Adjust the date range to view different time periods
        - Hover over chart points to see detailed data
        - Use the table at the bottom to see the exact numbers for each day
        - Track your meals regularly for more accurate progress tracking
        """)

main()