"""
Nutrition Planner App - Test Data Generator Part 4: Creating Meal Tracking Data

This script creates meal tracking data for the most recent meal program or the last 15 days:
- Tracks meals based on the created meal program if available
- Falls back to the last 15 days if no program is found
- Adds some variations from the program for realism
- Includes occasional notes with the tracked meals
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import random

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_manager import NutritionDB
from utils.constants import FoodCategory, MealCategory, MealTime, ActivityLevel, GoalType

# Initialize the database
db = NutritionDB()

def create_meal_tracking_data():
    """Create meal tracking data based on the most recent program or last 15 days"""
    print("Creating meal tracking data...")
    
    # Get all available meals
    all_meals = db.get_all_meals()
    if all_meals.empty:
        print("No meals available for tracking!")
        return
    
    # Get all meal programs
    programs = db.get_all_programs()
    
    # Default tracking period (if no program is found)
    today = datetime.now().date()
    default_start_date = today - timedelta(days=14)  # 15 days including today
    
    # If we have programs, use the most recent one's dates
    if not programs.empty:
        # Sort programs by created date (newest first)
        programs = programs.sort_values('created_at', ascending=False)
        program_id = programs.iloc[0]['id']
        
        # Get program start and end dates
        program_start = pd.to_datetime(programs.iloc[0]['start_date']).date()
        program_end = pd.to_datetime(programs.iloc[0]['end_date']).date()
        
        # If program end date is in the future, cap it at today
        if program_end > today:
            program_end = today
            
        # If program is very long, limit tracking to at most 30 days
        if (program_end - program_start).days > 30:
            program_start = program_end - timedelta(days=29)
        
        start_date = program_start
        end_date = today
        
        print(f"Using program: {programs.iloc[0]['name']} (ID: {program_id})")
        print(f"Date range: {start_date} to {end_date}")
        
        # Get the program meals
        program_meals = db.get_program_meals(program_id)
        if program_meals.empty:
            print("No meals in the program! Using default tracking period.")
            start_date = default_start_date
            end_date = today
            program_meals = pd.DataFrame()
    else:
        print("No meal programs found! Using default tracking period.")
        program_id = None
        program_meals = pd.DataFrame()
        start_date = default_start_date
        end_date = today
    
    print(f"Creating tracking data from {start_date} to {end_date}")
    
    # Group meals by category for substitutions
    breakfast_meals = all_meals[all_meals['category'] == MealCategory.BREAKFAST.value]
    lunch_meals = all_meals[all_meals['category'] == MealCategory.LUNCH_DINNER.value]
    dinner_meals = all_meals[all_meals['category'] == MealCategory.LUNCH_DINNER.value]
    snack_meals = all_meals[all_meals['category'] == MealCategory.SNACKS.value]
    
    # If any category is empty, use a fallback
    if breakfast_meals.empty:
        breakfast_meals = all_meals
    if lunch_meals.empty:
        lunch_meals = all_meals
    if dinner_meals.empty:
        dinner_meals = all_meals
    if snack_meals.empty:
        snack_meals = all_meals
    
    # Helper function to get a random meal ID from a category
    def get_random_meal_id(meals_df):
        if meals_df.empty:
            return None
        random_index = random.randint(0, len(meals_df) - 1)
        return int(meals_df.iloc[random_index]['id'])
    
    # Sample notes to add variety
    breakfast_notes = [
        "Felt energized after this breakfast",
        "Added extra protein",
        "Felt a bit rushed this morning",
        "Perfect start to the day",
        "Added cinnamon on top"
    ]
    
    lunch_notes = [
        "Ate at the office",
        "Shared lunch with colleagues",
        "Added extra vegetables",
        "Felt satisfied but not too full",
        "Had a smaller portion than usual"
    ]
    
    dinner_notes = [
        "Ate dinner earlier than usual",
        "Had a large portion after workout",
        "Cooking went really well today",
        "Added some herbs for flavor",
        "Felt really satisfied after this meal"
    ]
    
    snack_notes = [
        "Perfect timing before workout",
        "Just what I needed in the afternoon",
        "Quick snack on the go",
        "Helped with afternoon energy dip",
        "Had this while working"
    ]
    
    # Track meals for each day in the range
    tracked_count = 0
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Get planned meals for this day if program exists
        if not program_meals.empty:
            day_meals = program_meals[program_meals['date'] == date_str]
        else:
            day_meals = pd.DataFrame()
        
        # For each meal time, decide whether to track the planned meal or substitute
        for meal_time in MealTime.as_list():
            # Sometimes skip tracking a meal (15% chance)
            if random.random() < 0.15:
                continue
                
            # Get the planned meal for this time if it exists
            if not day_meals.empty:
                planned_meal = day_meals[day_meals['meal_time'] == meal_time]
            else:
                planned_meal = pd.DataFrame()
            
            # Determine which meal to track
            if planned_meal.empty or random.random() < 0.2:  # 20% chance to substitute or no planned meal
                # Substitute with a different meal
                if meal_time == MealTime.BREAKFAST.value:
                    meal_id = get_random_meal_id(breakfast_meals)
                    notes = random.choice(breakfast_notes) if random.random() < 0.5 else None
                elif meal_time == MealTime.LUNCH.value:
                    meal_id = get_random_meal_id(lunch_meals)
                    notes = random.choice(lunch_notes) if random.random() < 0.5 else None
                elif meal_time == MealTime.DINNER.value:
                    meal_id = get_random_meal_id(dinner_meals)
                    notes = random.choice(dinner_notes) if random.random() < 0.5 else None
                else:  # Snacks
                    meal_id = get_random_meal_id(snack_meals)
                    notes = random.choice(snack_notes) if random.random() < 0.5 else None
            else:
                # Track the planned meal
                meal_id = int(planned_meal.iloc[0]['meal_id'])
                
                # Add notes occasionally
                if random.random() < 0.3:  # 30% chance to add notes
                    if meal_time == MealTime.BREAKFAST.value:
                        notes = random.choice(breakfast_notes)
                    elif meal_time == MealTime.LUNCH.value:
                        notes = random.choice(lunch_notes)
                    elif meal_time == MealTime.DINNER.value:
                        notes = random.choice(dinner_notes)
                    else:  # Snacks
                        notes = random.choice(snack_notes)
                else:
                    notes = None
            
            # Skip if no meal ID was found
            if not meal_id:
                continue
            
            # Create a realistic timestamp for the meal
            if meal_time == MealTime.BREAKFAST.value:
                hour = random.randint(7, 9)
            elif meal_time == MealTime.MORNING_SNACK.value:
                hour = random.randint(10, 11)
            elif meal_time == MealTime.LUNCH.value:
                hour = random.randint(12, 14)
            elif meal_time == MealTime.AFTERNOON_SNACK.value:
                hour = random.randint(15, 17)
            else:  # Dinner
                hour = random.randint(18, 21)
                
            minute = random.randint(0, 59)
            
            # For past dates, use a date in the past
            # For today, ensure the time is before now
            if current_date == today:
                now = datetime.now()
                if hour > now.hour or (hour == now.hour and minute > now.minute):
                    hour = now.hour
                    minute = max(0, now.minute - 5)  # 5 minutes ago at most
            
            actual_time = datetime(
                current_date.year, 
                current_date.month, 
                current_date.day, 
                hour, 
                minute
            )
            
            # Track the meal
            success = db.track_meal(
                date=current_date,
                meal_id=meal_id,
                meal_time=meal_time,
                actual_time=actual_time,
                notes=notes
            )
            
            if success:
                tracked_count += 1
        
        # Move to next day
        current_date += timedelta(days=1)
    
    print(f"Tracked {tracked_count} meals from {start_date} to {end_date}!")

# Execute the meal tracking function
if __name__ == "__main__":
    create_meal_tracking_data()