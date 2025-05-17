"""
Nutrition App - Test Data Generator Part 3: Creating Meal Programs

This script creates a meal program for the last 30 days up to today:
- Creates a 30-day program starting from 30 days ago
- Assigns different meals for each day and meal time
- Creates realistic meal patterns (e.g., same breakfast on weekdays)
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

def create_meal_program():
    """Create a meal program for the last 30 days up to today"""
    print("Creating meal program...")
    
    # Calculate program dates based on today's date
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=29)  # 30 days including today
    
    # Format the program name based on the date range
    start_month = start_date.strftime("%B")
    end_month = end_date.strftime("%B")
    
    if start_month == end_month:
        program_name = f"{start_month} {start_date.year} Meal Plan"
    else:
        program_name = f"{start_month}-{end_month} {end_date.year} Meal Plan"
    
    # Create the program
    program_id = db.save_meal_program(program_name, start_date, end_date)
    
    if not program_id:
        print("Failed to create meal program!")
        return
    
    print(f"Created program: {program_name} (ID: {program_id})")
    print(f"Date range: {start_date} to {end_date}")
    
    # Load all available meals
    all_meals = db.get_all_meals()
    
    # Group meals by category
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
    
    # Create consistent meal patterns
    # For example: Same breakfast on weekdays, different on weekends
    weekday_breakfast = get_random_meal_id(breakfast_meals)
    weekend_breakfast = get_random_meal_id(breakfast_meals)
    
    # Different lunch options for variety
    lunch_options = [get_random_meal_id(lunch_meals) for _ in range(min(3, len(lunch_meals)))]
    if not lunch_options:
        print("Warning: No lunch meals available.")
        lunch_options = [get_random_meal_id(all_meals)]
    
    # Different dinner options
    dinner_options = [get_random_meal_id(dinner_meals) for _ in range(min(3, len(dinner_meals)))]
    if not dinner_options:
        print("Warning: No dinner meals available.")
        dinner_options = [get_random_meal_id(all_meals)]
    
    # Snack options
    morning_snack_options = [get_random_meal_id(snack_meals) for _ in range(min(2, len(snack_meals)))]
    if not morning_snack_options:
        print("Warning: No snack meals available for morning.")
        morning_snack_options = [get_random_meal_id(all_meals)]
        
    afternoon_snack_options = [get_random_meal_id(snack_meals) for _ in range(min(2, len(snack_meals)))]
    if not afternoon_snack_options:
        print("Warning: No snack meals available for afternoon.")
        afternoon_snack_options = [get_random_meal_id(all_meals)]
    
    # Assign meals for each day in the program
    meals_added = 0
    current_date = start_date
    
    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5  # 5 = Saturday, 6 = Sunday
        
        # Assign breakfast
        breakfast_id = weekend_breakfast if is_weekend else weekday_breakfast
        if breakfast_id:
            db.add_meal_to_program(program_id, breakfast_id, current_date, MealTime.BREAKFAST.value)
            meals_added += 1
        
        # Assign morning snack (not every day)
        if random.random() > 0.3 and morning_snack_options:  # 70% chance of having a morning snack
            morning_snack_id = random.choice(morning_snack_options)
            db.add_meal_to_program(program_id, morning_snack_id, current_date, MealTime.MORNING_SNACK.value)
            meals_added += 1
        
        # Assign lunch
        if lunch_options:
            lunch_id = random.choice(lunch_options)
            db.add_meal_to_program(program_id, lunch_id, current_date, MealTime.LUNCH.value)
            meals_added += 1
        
        # Assign afternoon snack (not every day)
        if random.random() > 0.4 and afternoon_snack_options:  # 60% chance of having an afternoon snack
            afternoon_snack_id = random.choice(afternoon_snack_options)
            db.add_meal_to_program(program_id, afternoon_snack_id, current_date, MealTime.AFTERNOON_SNACK.value)
            meals_added += 1
        
        # Assign dinner
        if dinner_options:
            dinner_id = random.choice(dinner_options)
            db.add_meal_to_program(program_id, dinner_id, current_date, MealTime.DINNER.value)
            meals_added += 1
        
        # Move to next day
        current_date += timedelta(days=1)
    
    print(f"Added {meals_added} meals to the program!")
    return program_id

# Execute the program creation function
if __name__ == "__main__":
    create_meal_program()