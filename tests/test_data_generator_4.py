"""
Nutrition Planner App - Test Data Generator Part 4: Creating Meal Tracking Data

This script creates meal tracking data from May 1, 2025 to May 16, 2025:
- Tracks meals based on the created meal program
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
    """Create meal tracking data from May 1 to May 16, 2025"""
    print("Creating meal tracking data...")
    
    # Date range for tracking
    start_date = datetime(2025, 5, 1).date()
    end_date = datetime(2025, 5, 16).date()  # Today's date in the scenario
    
    # Get all available meals
    all_meals = db.get_all_meals()
    if all_meals.empty:
        print("No meals available for tracking!")
        return
    
    # Get all meal programs
    programs = db.get_all_programs()
    if programs.empty:
        print("No meal programs available!")
        return
    
    # Get the first program (should be our May program)
    program_id = programs.iloc[0]['id']
    
    # Get the program meals
    program_meals = db.get_program_meals(program_id)
    if program_meals.empty:
        print("No meals in the program!")
        return
    
    # Group meals by category for substitutions
    breakfast_meals = all_meals[all_meals['category'] == MealCategory.BREAKFAST.value]
    lunch_meals = all_meals[all_meals['category'] == MealCategory.LUNCH_DINNER.value]
    dinner_meals = all_meals[all_meals['category'] == MealCategory.LUNCH_DINNER.value]
    snack_meals = all_meals[all_meals['category'] == MealCategory.SNACKS.value]
    
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
        
        # Get planned meals for this day
        day_meals = program_meals[program_meals['date'] == date_str]
        
        # For each meal time, decide whether to track the planned meal or substitute
        for meal_time in MealTime.as_list():
            # Sometimes skip tracking a meal (15% chance)
            if random.random() < 0.15:
                continue
                
            # Get the planned meal for this time if it exists
            planned_meal = day_meals[day_meals['meal_time'] == meal_time]
            
            # Determine which meal to track
            if planned_meal.empty or random.random() < 0.2:  # 20% chance to substitute
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