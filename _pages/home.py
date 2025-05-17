"""
Home page for the Nutrition App.

This is the landing page that provides an overview of the application
and displays summary information if a profile exists.
"""
import streamlit as st
from utils.db_manager import NutritionDB

# Initialize database
db = NutritionDB()

def load_profile_data():
    """Load profile data without caching"""
    return db.load_profile()

def display_welcome_message():
    """Display welcome message and features"""
    st.markdown("""    
    ### This application helps you manage your nutrition and meal planning:
    
    - 👤 **Track your profile** and caloric needs
    - 🍎 **Manage food sources** and their nutritional content
    - 📋 **Plan your meals** based on your goals
    - 📅 **Create meal programs** for specific periods
    - 📊 **Analyze program adherence** and compare planned vs. actual meals
    - 📈 **Track your progress** over time
    """)

def display_profile_summary(profile):
    """Display profile summary in columns"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Current Goal")
        goal_text = f"""
        **Goal Type:** {profile[6]}
        **{'Deficit' if profile[6] == 'Weight Loss' else 'Surplus' if profile[6] == 'Weight Gain' else 'Maintenance'} Level:** {profile[7]}%
        """
        st.info(goal_text)
    
    with col2:
        st.subheader("📊 Quick Stats")
        stats_text = f"""
        **Weight:** {profile[1]} kg
        **Height:** {profile[2]} m
        **Activity Level:** {profile[4]}
        """
        st.info(stats_text)

def display_get_started():
    """Display getting started section with consistent card styling"""
    st.header("📋 Getting Started")
    
    # First row: Profile, Food, Meals
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.subheader("1️⃣ Set Up Your Profile")
            st.markdown("Begin by setting up your profile with your personal information:")
            st.markdown("""
            - Weight and height
            - Age and gender
            - Activity level & Nutritional goals
            """)
            st.page_link("_pages/account/profile/edit_profile.py", label="Edit Profile", icon="👤")
    
    with col2:
        with st.container(border=True):
            st.subheader("2️⃣ Add Food Sources")
            st.markdown("Add the foods you commonly eat to your food database:")
            st.markdown("""
            - Create a personal food library
            - Track nutritional information
            - Use these foods in your meals
            """)
            st.page_link("_pages/food/add_food.py", label="Add Foods", icon="🍎")
    
    with col3:
        with st.container(border=True):
            st.subheader("3️⃣ Create Meals")
            st.markdown("Create meals from your food sources:")
            st.markdown("""
            - Build regular meals from your foods
            - Add custom meals with known macros
            - Use these meals in your programs
            """)
            st.page_link("_pages/meals/create_meals.py", label="Create Meals", icon="🍽️")
            
    # Add some spacing between rows
    st.write("")
    
    # Second row: Programs, Progress, Adherence
    col4, col5, col6 = st.columns(3)
    
    with col4:
        with st.container(border=True):
            st.subheader("4️⃣ Plan Your Meals")
            st.markdown("Create meal programs for specific time periods:")
            st.markdown("""
            - Schedule meals for days or weeks
            - Balance your nutrition throughout the week
            - Plan ahead for your goals
            """)
            st.page_link("_pages/programs/create_program.py", label="Create Program", icon="📝")
    
    with col5:
        with st.container(border=True):
            st.subheader("5️⃣ Track Your Progress")
            st.markdown("Log your meals and track your progress:")
            st.markdown("""
            - Record what you actually eat
            - Monitor your nutritional intake
            - Visualize your progress over time
            """)
            st.page_link("_pages/tracking/log.py", label="Log Meals", icon="📝")
    
    with col6:
        with st.container(border=True):
            st.subheader("6️⃣ Analyze Adherence")
            st.markdown("Compare your planned meals with actual consumption:")
            st.markdown("""
            - See how closely you follow your plan
            - Identify substitution patterns
            - Improve your meal planning strategy
            """)
            st.page_link("_pages/tracking/program_adherence.py", label="Program Adherence", icon="📊")

def display_app_stats():
    """Display application statistics"""
    st.header("📊 App Statistics")
    
    # Get database statistics
    stats = db.get_app_stats()
    
    # Display stats in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Food Sources", stats["food_sources"])
    
    with col2:
        st.metric("Meals Created", stats["meals"])
    
    with col3:
        st.metric("Meal Programs", stats["meal_programs"])
    
    with col4:
        st.metric("Meals Tracked", stats["meal_tracking"])

def main():
    """Main function for the Home page"""
    st.title("🥗 Nutrition App")
    
    # Display welcome message
    display_welcome_message()
    
    # Load profile data
    profile = load_profile_data()
    
    # If profile exists, show profile summary
    if profile:
        st.divider()
        display_profile_summary(profile)
    else:
        # If no profile, show prominent button to create profile
        st.warning("👋 Please set up your profile to get started!")
        st.page_link("_pages/account/profile/edit_profile.py", label="Edit Profile", icon="👤")
    
    # Display getting started section regardless of profile status
    st.divider()
    display_get_started()
    
    # Display app statistics
    st.divider()
    display_app_stats()

main()