"""
Nutrition Planner App - Test Data Generator

This script populates the nutrition app database with test data for all major features:
- User profile
- Food sources
- Meals (regular and custom)
- Meal programs
- Meal tracking

Run this script after setting up the database structure to create a complete test environment.
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_manager import NutritionDB
from utils.constants import FoodCategory, MealCategory, MealTime, ActivityLevel, GoalType

# Initialize the database
db = NutritionDB()

def setup_profile():
    """Set up the user profile with provided details"""
    print("Setting up user profile...")
    
    # Using the provided profile details
    weight = 67.0  # kg
    height = 1.69  # m
    age = 23
    gender = "Male"
    activity_level = ActivityLevel.LIGHTLY_ACTIVE.value
    goal_type = GoalType.WEIGHT_LOSS.value
    goal_percentage = 10.0
    
    # Save the profile
    db.save_profile(
        weight=weight,
        height=height,
        age=age,
        activity_level=activity_level,
        gender=gender,
        goal_type=goal_type,
        goal_percentage=goal_percentage
    )
    
    print("Profile setup complete!")

def add_food_sources():
    """Add a variety of food sources to the database"""
    print("Adding food sources...")
    
    # Protein Sources
    protein_foods = [
        {
            "name": "Chicken Breast",
            "category": FoodCategory.PROTEIN_SOURCES.value,
            "calories": 165,
            "proteins": 31,
            "carbs": 0,
            "fats": 3.6,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Turkey Breast",
            "category": FoodCategory.PROTEIN_SOURCES.value,
            "calories": 104,
            "proteins": 24,
            "carbs": 0,
            "fats": 1,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Canned Tuna",
            "category": FoodCategory.PROTEIN_SOURCES.value,
            "calories": 116,
            "proteins": 26,
            "carbs": 0,
            "fats": 1,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Egg",
            "category": FoodCategory.PROTEIN_SOURCES.value,
            "calories": 74,
            "proteins": 6.3,
            "carbs": 0.7,
            "fats": 5,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 50
        },
        {
            "name": "Salmon",
            "category": FoodCategory.PROTEIN_SOURCES.value,
            "calories": 208,
            "proteins": 22,
            "carbs": 0,
            "fats": 13,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Greek Yogurt",
            "category": FoodCategory.PROTEIN_SOURCES.value,
            "calories": 59,
            "proteins": 10,
            "carbs": 3.6,
            "fats": 0,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Cottage Cheese",
            "category": FoodCategory.PROTEIN_SOURCES.value,
            "calories": 98,
            "proteins": 11,
            "carbs": 3.4,
            "fats": 4.3,
            "portion_size": 100,
            "base_unit": "g"
        },
    ]
    
    # Complex Carbohydrates
    carb_foods = [
        {
            "name": "Brown Rice",
            "category": FoodCategory.COMPLEX_CARBOHYDRATES.value,
            "calories": 112,
            "proteins": 2.6,
            "carbs": 23,
            "fats": 0.9,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Sweet Potato",
            "category": FoodCategory.COMPLEX_CARBOHYDRATES.value,
            "calories": 86,
            "proteins": 1.6,
            "carbs": 20,
            "fats": 0.1,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Oats",
            "category": FoodCategory.COMPLEX_CARBOHYDRATES.value,
            "calories": 389,
            "proteins": 16.9,
            "carbs": 66,
            "fats": 6.9,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Quinoa",
            "category": FoodCategory.COMPLEX_CARBOHYDRATES.value,
            "calories": 120,
            "proteins": 4.4,
            "carbs": 21.3,
            "fats": 1.9,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Whole Wheat Bread",
            "category": FoodCategory.COMPLEX_CARBOHYDRATES.value,
            "calories": 247,
            "proteins": 13,
            "carbs": 41,
            "fats": 3.4,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 100
        },
        {
            "name": "Lentils",
            "category": FoodCategory.COMPLEX_CARBOHYDRATES.value,
            "calories": 116,
            "proteins": 9,
            "carbs": 20,
            "fats": 0.4,
            "portion_size": 100,
            "base_unit": "g"
        },
    ]
    
    # Healthy Fats
    fat_foods = [
        {
            "name": "Avocado",
            "category": FoodCategory.HEALTHY_FATS.value,
            "calories": 160,
            "proteins": 2,
            "carbs": 8.5,
            "fats": 14.7,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 170
        },
        {
            "name": "Almonds",
            "category": FoodCategory.HEALTHY_FATS.value,
            "calories": 579,
            "proteins": 21,
            "carbs": 22,
            "fats": 49,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Olive Oil",
            "category": FoodCategory.HEALTHY_FATS.value,
            "calories": 884,
            "proteins": 0,
            "carbs": 0,
            "fats": 100,
            "portion_size": 100,
            "base_unit": "ml"
        },
        {
            "name": "Chia Seeds",
            "category": FoodCategory.HEALTHY_FATS.value,
            "calories": 486,
            "proteins": 17,
            "carbs": 42,
            "fats": 31,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Walnuts",
            "category": FoodCategory.HEALTHY_FATS.value,
            "calories": 654,
            "proteins": 15.2,
            "carbs": 13.7,
            "fats": 65.2,
            "portion_size": 100,
            "base_unit": "g"
        },
    ]
    
    # Fruits
    fruit_foods = [
        {
            "name": "Banana",
            "category": FoodCategory.FRUITS.value,
            "calories": 89,
            "proteins": 1.1,
            "carbs": 23,
            "fats": 0.3,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 118
        },
        {
            "name": "Apple",
            "category": FoodCategory.FRUITS.value,
            "calories": 52,
            "proteins": 0.3,
            "carbs": 14,
            "fats": 0.2,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 182
        },
        {
            "name": "Blueberries",
            "category": FoodCategory.FRUITS.value,
            "calories": 57,
            "proteins": 0.7,
            "carbs": 14,
            "fats": 0.3,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Strawberries",
            "category": FoodCategory.FRUITS.value,
            "calories": 32,
            "proteins": 0.7,
            "carbs": 7.7,
            "fats": 0.3,
            "portion_size": 100,
            "base_unit": "g"
        },
        {
            "name": "Orange",
            "category": FoodCategory.FRUITS.value,
            "calories": 47,
            "proteins": 0.9,
            "carbs": 11.8,
            "fats": 0.1,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 131
        },
    ]
    
    # Combine all foods
    all_foods = protein_foods + carb_foods + fat_foods + fruit_foods
    
    # Save all foods to the database
    foods_added = 0
    for food in all_foods:
        conversion_factor = food.get("conversion_factor", 1.0)
        success = db.save_food_source(
            name=food["name"],
            category=food["category"],
            calories=food["calories"],
            proteins=food["proteins"],
            carbs=food["carbs"],
            fats=food["fats"],
            portion_size=food["portion_size"],
            base_unit=food["base_unit"],
            conversion_factor=conversion_factor
        )
        if success:
            foods_added += 1
    
    print(f"Added {foods_added} food sources successfully!")

# Execute the setup functions
if __name__ == "__main__":
    setup_profile()
    add_food_sources()