"""
Profile summary page for the Nutrition Planner application.

This page displays a summary of the user's profile information,
calculated metrics (BMR, TDEE), and nutritional targets.
"""
import streamlit as st
import pandas as pd
from utils.db_manager import NutritionDB
from utils.constants import ActivityLevel, GoalType
from utils.nutrition import calculate_all_metrics, calculate_macro_targets
from utils.ui import (
    display_success_error, 
    display_metrics, 
    display_profile_card,
    create_macro_charts
)

# Initialize database
db = NutritionDB()

def display_nutrition_metrics(profile):
    """Display calculated nutrition metrics and macro targets."""
    # Calculate all metrics
    bmr, tdee, target_calories = calculate_all_metrics(
        profile[1], profile[2], profile[3], profile[5],
        profile[4], profile[6], profile[7]
    )
    
    # Display metrics
    st.subheader("⚡ Energy Metrics")
    metrics = {
        "Basal Metabolic Rate": bmr,
        "Total Daily Energy Expenditure": tdee,
        "Target Daily Calories": target_calories
    }
    
    formatter = {
        "Basal Metabolic Rate": "{:.0f} kcal",
        "Total Daily Energy Expenditure": "{:.0f} kcal",
        "Target Daily Calories": "{:.0f} kcal"
    }
    
    display_metrics(metrics, 3, formatter)
    
    # Calculate and display macro targets
    st.divider()
    st.subheader("🥗 Daily Macro Targets")
    
    macros = calculate_macro_targets(profile[1], target_calories)
    
    macro_metrics = {
        "Protein Target": macros['protein'],
        "Carbs Target": macros['carbs'],
        "Fats Target": macros['fats']
    }
    
    macro_formatter = {
        "Protein Target": "{:.0f}g",
        "Carbs Target": "{:.0f}g",
        "Fats Target": "{:.0f}g"
    }
    
    display_metrics(macro_metrics, 3, macro_formatter)
    
    # Display visualization of macro distribution
    st.divider()
    st.subheader("📊 Macro Distribution")
    
    col1, col2 = st.columns(2)
    
    # Calculate percentages
    protein_cal = macros['protein'] * 4
    carbs_cal = macros['carbs'] * 4
    fats_cal = macros['fats'] * 9
    total_cal = protein_cal + carbs_cal + fats_cal
    
    protein_pct = (protein_cal / total_cal) * 100
    carbs_pct = (carbs_cal / total_cal) * 100
    fats_pct = (fats_cal / total_cal) * 100
    
    # Create and display charts
    with col1:
        dist_fig, _ = create_macro_charts(
            {
                'calories': target_calories,
                'proteins': macros['protein'],
                'carbs': macros['carbs'], 
                'fats': macros['fats']
            }
        )
        st.plotly_chart(dist_fig, use_container_width=True)
    
    with col2:
        st.markdown("### Caloric Distribution")
        st.markdown(f"**Protein:** {protein_pct:.1f}% ({protein_cal:.0f} kcal)")
        st.progress(protein_pct/100)
        
        st.markdown(f"**Carbs:** {carbs_pct:.1f}% ({carbs_cal:.0f} kcal)")
        st.progress(carbs_pct/100)
        
        st.markdown(f"**Fats:** {fats_pct:.1f}% ({fats_cal:.0f} kcal)")
        st.progress(fats_pct/100)

def display_profile_info(profile):
    """Display profile information in a card format."""
    st.subheader(f"👤 Profile Overview")
    display_profile_card(profile)

def main():
    """Main function for the Profile Summary page."""
    st.title("📊 Profile Summary")
    
    # Display any success/error messages
    display_success_error()
    
    # Load profile 
    profile = db.load_profile()
    
    if profile:
        # Display profile sections
        display_profile_info(profile)
        st.divider()
        display_nutrition_metrics(profile)
        
        # Add helpful information at the bottom
        with st.expander("Understanding Your Metrics"):
            st.markdown("""
            ### Metric Explanations
            
            - **BMR (Basal Metabolic Rate)**: The number of calories your body needs to maintain basic functions while at rest.
            
            - **TDEE (Total Daily Energy Expenditure)**: Your estimated daily calorie burn based on your BMR and activity level.
            
            - **Target Calories**: Your daily calorie goal based on your fitness objectives.
            
            - **Macro Targets**: 
                - **Protein**: Important for muscle repair and growth (4 calories per gram)
                - **Carbs**: Primary energy source for your body (4 calories per gram)
                - **Fats**: Essential for hormone production and nutrient absorption (9 calories per gram)
            """)
    else:
        st.warning("No profile data available. Please fill out the profile form in the Edit Profile page.")
        st.page_link("_pages/account/profile/edit_profile.py", label="Edit Profile", icon="👤")

main()