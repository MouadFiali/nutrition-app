"""
Nutrition Planner App - Test Data Generator Part 2: Creating Meals

This script creates a variety of regular and custom meals for testing:
- Regular meals (made from food sources) for each meal category
- Custom meals with manually defined macros
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

def create_regular_meals():
    """Create regular meals composed of food sources"""
    print("Creating regular meals...")
    
    # Get all food sources to work with
    food_sources = db.load_food_sources()
    
    # Helper function to find a food by name
    def get_food_data(name):
        food = food_sources[food_sources['name'] == name]
        if not food.empty:
            return {'id': int(food.iloc[0]['id']), 'quantity': 0.0, 'base_unit': food.iloc[0]['base_unit']}
        return None
    
    # Create breakfast meals
    breakfast_meals = [
        {
            "name": "Oatmeal with Berries",
            "category": MealCategory.BREAKFAST.value,
            "foods": {
                "Oats": {"quantity": 50.0},
                "Blueberries": {"quantity": 50.0},
                "Greek Yogurt": {"quantity": 100.0},
                "Chia Seeds": {"quantity": 10.0}
            }
        },
        {
            "name": "Scrambled Eggs on Toast",
            "category": MealCategory.BREAKFAST.value,
            "foods": {
                "Egg": {"quantity": 3.0},
                "Whole Wheat Bread": {"quantity": 2.0},
                "Avocado": {"quantity": 0.5}
            }
        },
        {
            "name": "Protein Smoothie",
            "category": MealCategory.BREAKFAST.value,
            "foods": {
                "Greek Yogurt": {"quantity": 150.0},
                "Banana": {"quantity": 1.0},
                "Strawberries": {"quantity": 50.0},
                "Chia Seeds": {"quantity": 5.0}
            }
        }
    ]
    
    # Create lunch meals
    lunch_meals = [
        {
            "name": "Chicken and Rice Bowl",
            "category": MealCategory.LUNCH_DINNER.value,
            "foods": {
                "Chicken Breast": {"quantity": 120.0},
                "Brown Rice": {"quantity": 150.0},
                "Avocado": {"quantity": 0.5},
                "Olive Oil": {"quantity": 10.0}
            }
        },
        {
            "name": "Tuna Salad",
            "category": MealCategory.LUNCH_DINNER.value,
            "foods": {
                "Canned Tuna": {"quantity": 100.0},
                "Olive Oil": {"quantity": 10.0},
                "Sweet Potato": {"quantity": 100.0}
            }
        },
        {
            "name": "Quinoa and Turkey Bowl",
            "category": MealCategory.LUNCH_DINNER.value,
            "foods": {
                "Turkey Breast": {"quantity": 100.0},
                "Quinoa": {"quantity": 100.0},
                "Olive Oil": {"quantity": 5.0},
                "Blueberries": {"quantity": 30.0}
            }
        }
    ]
    
    # Create dinner meals
    dinner_meals = [
        {
            "name": "Salmon with Sweet Potato",
            "category": MealCategory.LUNCH_DINNER.value,
            "foods": {
                "Salmon": {"quantity": 150.0},
                "Sweet Potato": {"quantity": 150.0},
                "Olive Oil": {"quantity": 10.0}
            }
        },
        {
            "name": "Lentil and Vegetable Stew",
            "category": MealCategory.LUNCH_DINNER.value,
            "foods": {
                "Lentils": {"quantity": 150.0},
                "Olive Oil": {"quantity": 15.0},
                "Quinoa": {"quantity": 50.0}
            }
        },
        {
            "name": "Chicken and Quinoa",
            "category": MealCategory.LUNCH_DINNER.value,
            "foods": {
                "Chicken Breast": {"quantity": 150.0},
                "Quinoa": {"quantity": 100.0},
                "Olive Oil": {"quantity": 10.0},
                "Avocado": {"quantity": 0.5}
            }
        }
    ]
    
    # Create snack meals
    snack_meals = [
        {
            "name": "Greek Yogurt with Nuts",
            "category": MealCategory.SNACKS.value,
            "foods": {
                "Greek Yogurt": {"quantity": 150.0},
                "Almonds": {"quantity": 20.0},
                "Blueberries": {"quantity": 30.0}
            }
        },
        {
            "name": "Fruit and Nut Mix",
            "category": MealCategory.SNACKS.value,
            "foods": {
                "Apple": {"quantity": 1.0},
                "Almonds": {"quantity": 25.0},
                "Walnuts": {"quantity": 15.0}
            }
        },
        {
            "name": "Cottage Cheese with Fruit",
            "category": MealCategory.SNACKS.value,
            "foods": {
                "Cottage Cheese": {"quantity": 100.0},
                "Strawberries": {"quantity": 50.0},
                "Chia Seeds": {"quantity": 5.0}
            }
        }
    ]
    
    # Combine all meals
    all_meals = breakfast_meals + lunch_meals + dinner_meals + snack_meals
    
    # Process and save each meal
    meals_added = 0
    for meal in all_meals:
        # Process food quantities
        foods_quantities = {}
        for food_name, food_data in meal["foods"].items():
            base_data = get_food_data(food_name)
            if base_data:
                base_data["quantity"] = food_data["quantity"]
                foods_quantities[food_name] = base_data
        
        # Save the meal
        success = db.save_meal(
            name=meal["name"],
            category=meal["category"],
            meal_type="regular",
            foods_quantities=foods_quantities
        )
        
        if success:
            meals_added += 1
    
    print(f"Added {meals_added} regular meals successfully!")

def create_custom_meals():
    """Create custom meals with manually defined macros"""
    print("Creating custom meals...")
    
    # Custom breakfast meals
    breakfast_meals = [
        {
            "name": "Restaurant Breakfast",
            "category": MealCategory.BREAKFAST.value,
            "macros": {
                "calories": 450,
                "proteins": 25,
                "carbs": 40,
                "fats": 15
            }
        },
        {
            "name": "High Protein Breakfast",
            "category": MealCategory.BREAKFAST.value,
            "macros": {
                "calories": 390,
                "proteins": 35,
                "carbs": 25,
                "fats": 10
            }
        }
    ]
    
    # Custom lunch meals
    lunch_meals = [
        {
            "name": "Restaurant Lunch",
            "category": MealCategory.LUNCH_DINNER.value,
            "macros": {
                "calories": 650,
                "proteins": 30,
                "carbs": 60,
                "fats": 20
            }
        },
        {
            "name": "Office Lunch",
            "category": MealCategory.LUNCH_DINNER.value,
            "macros": {
                "calories": 580,
                "proteins": 25,
                "carbs": 65,
                "fats": 15
            }
        }
    ]
    
    # Custom dinner meals
    dinner_meals = [
        {
            "name": "Restaurant Dinner",
            "category": MealCategory.LUNCH_DINNER.value,
            "macros": {
                "calories": 750,
                "proteins": 35,
                "carbs": 70,
                "fats": 25
            }
        },
        {
            "name": "Light Dinner",
            "category": MealCategory.LUNCH_DINNER.value,
            "macros": {
                "calories": 450,
                "proteins": 30,
                "carbs": 35,
                "fats": 10
            }
        }
    ]
    
    # Custom snack meals
    snack_meals = [
        {
            "name": "Protein Bar",
            "category": MealCategory.SNACKS.value,
            "macros": {
                "calories": 220,
                "proteins": 15,
                "carbs": 25,
                "fats": 8
            }
        },
        {
            "name": "Coffee Shop Snack",
            "category": MealCategory.SNACKS.value,
            "macros": {
                "calories": 300,
                "proteins": 5,
                "carbs": 40,
                "fats": 12
            }
        }
    ]
    
    # Combine all meals
    all_meals = breakfast_meals + lunch_meals + dinner_meals + snack_meals
    
    # Save each meal
    meals_added = 0
    for meal in all_meals:
        success = db.save_meal(
            name=meal["name"],
            category=meal["category"],
            meal_type="custom",
            custom_macros=meal["macros"]
        )
        
        if success:
            meals_added += 1
    
    print(f"Added {meals_added} custom meals successfully!")

# Execute the meal creation functions
if __name__ == "__main__":
    create_regular_meals()
    create_custom_meals()