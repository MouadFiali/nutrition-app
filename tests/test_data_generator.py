"""
Nutrition App - Complete Test Data Generator

This script runs all parts of the test data generation process:
1. Sets up the user profile
2. Creates food sources
3. Creates regular and custom meals
4. Creates a meal program for May 2025
5. Creates meal tracking data from May 1-16, 2025

Run this script to fully populate the database for testing all features of the application.
"""
import os
import sys
import time

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_manager import NutritionDB
from utils.constants import FoodCategory, MealCategory, MealTime, ActivityLevel, GoalType

# Import the functions from each part
from test_data_generator_1 import setup_profile, add_food_sources
from test_data_generator_2 import create_regular_meals, create_custom_meals
from test_data_generator_3 import create_meal_program
from test_data_generator_4 import create_meal_tracking_data

def generate_all_test_data():
    """Run the complete test data generation process"""
    print("=" * 50)
    print("NUTRITION APP TEST DATA GENERATOR")
    print("=" * 50)
    print("This script will populate the database with comprehensive test data.")
    print("Make sure you have an empty database or are ready to overwrite existing data.")
    
    # Confirm before proceeding
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    # Initialize the database
    db = NutritionDB()
    
    # Start the data generation process
    print("\n1. Setting up user profile...")
    setup_profile()
    time.sleep(1)
    
    print("\n2. Adding food sources...")
    add_food_sources()
    time.sleep(1)
    
    print("\n3. Creating regular meals...")
    create_regular_meals()
    time.sleep(1)
    
    print("\n4. Creating custom meals...")
    create_custom_meals()
    time.sleep(1)
    
    print("\n5. Creating meal program...")
    create_meal_program()
    time.sleep(1)
    
    print("\n6. Creating meal tracking data...")
    create_meal_tracking_data()
    
    print("\n" + "=" * 50)
    print("TEST DATA GENERATION COMPLETE!")
    print("=" * 50)
    print("The database has been populated with test data for all app features:")
    print("- 1 user profile with weight loss goal")
    print("- Various food sources across different categories")
    print("- Multiple regular and custom meals for each meal category")
    print("- A meal program for the last 30 days")
    print("- Tracked meals for the last 15 days or the most recent program")
    print("\nYou can now test all functionality of the Nutrition App.")

if __name__ == "__main__":
    generate_all_test_data()