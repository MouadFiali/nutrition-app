"""
Food sources initialization script for the Nutrition Planner application.

This script populates the database with default food sources.
Run this script to initialize the food database with common foods.
"""
from utils.db_manager import NutritionDB
import pandas as pd
import os
import sys

# Ensure we can import from parent directory when running this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize database
db = NutritionDB()

# Initial food sources data with enhanced unit handling
food_sources = {
    "Protein Sources": [
        {
            "name": "Chicken Breast",
            "calories": 165,
            "proteins": 31,
            "carbs": 0,
            "fats": 3.6,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Turkey Breast",
            "calories": 157,
            "proteins": 30,
            "carbs": 0,
            "fats": 3.6,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Canned Tuna",
            "calories": 116,
            "proteins": 26,
            "carbs": 0,
            "fats": 1,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Egg",
            "calories": 74,
            "proteins": 6.3,
            "carbs": 0.7,
            "fats": 5,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 52.0  # 1 egg ≈ 52g
        },
        {
            "name": "White Fish",
            "calories": 105,
            "proteins": 22,
            "carbs": 0,
            "fats": 2,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Greek Yogurt 0%",
            "calories": 59,
            "proteins": 10,
            "carbs": 3.6,
            "fats": 0,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        }
    ],
    "Complex Carbohydrates": [
        {
            "name": "Brown Rice",
            "calories": 112,
            "proteins": 2.6,
            "carbs": 23,
            "fats": 0.9,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Sweet Potato",
            "calories": 86,
            "proteins": 1.6,
            "carbs": 20,
            "fats": 0.1,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Oats",
            "calories": 389,
            "proteins": 16.9,
            "carbs": 66,
            "fats": 6.9,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Quinoa",
            "calories": 120,
            "proteins": 4.4,
            "carbs": 21.3,
            "fats": 1.9,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Lentils",
            "calories": 116,
            "proteins": 9,
            "carbs": 20,
            "fats": 0.4,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        }
    ],
    "Healthy Fats": [
        {
            "name": "Avocado",
            "calories": 160,
            "proteins": 2,
            "carbs": 8.5,
            "fats": 14.7,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 170.0  # 1 medium avocado ≈ 170g
        },
        {
            "name": "Almonds",
            "calories": 579,
            "proteins": 21,
            "carbs": 22,
            "fats": 49,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Olive Oil",
            "calories": 884,
            "proteins": 0,
            "carbs": 0,
            "fats": 100,
            "portion_size": 100,
            "base_unit": "ml",
            "conversion_factor": 1.0
        },
        {
            "name": "Salmon",
            "calories": 208,
            "proteins": 22,
            "carbs": 0,
            "fats": 13,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Chia Seeds",
            "calories": 486,
            "proteins": 17,
            "carbs": 42,
            "fats": 31,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        }
    ],
    "Fruits": [
        {
            "name": "Banana",
            "calories": 89,
            "proteins": 1.1,
            "carbs": 23,
            "fats": 0.3,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 118.0  # 1 medium banana ≈ 118g
        },
        {
            "name": "Apple",
            "calories": 52,
            "proteins": 0.3,
            "carbs": 14,
            "fats": 0.2,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 182.0  # 1 medium apple ≈ 182g
        },
        {
            "name": "Blueberries",
            "calories": 57,
            "proteins": 0.7,
            "carbs": 14,
            "fats": 0.3,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Strawberries",
            "calories": 32,
            "proteins": 0.7,
            "carbs": 7.7,
            "fats": 0.3,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        }
    ],
    "Vegetables": [
        {
            "name": "Broccoli",
            "calories": 34,
            "proteins": 2.8,
            "carbs": 7,
            "fats": 0.4,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Spinach",
            "calories": 23,
            "proteins": 2.9,
            "carbs": 3.6,
            "fats": 0.4,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        },
        {
            "name": "Bell Pepper",
            "calories": 31,
            "proteins": 1,
            "carbs": 6,
            "fats": 0.3,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 120.0  # 1 medium pepper ≈ 120g
        },
        {
            "name": "Carrot",
            "calories": 41,
            "proteins": 0.9,
            "carbs": 10,
            "fats": 0.2,
            "portion_size": 1,
            "base_unit": "unit",
            "conversion_factor": 72.0  # 1 medium carrot ≈ 72g
        }
    ],
    "Dairy and Alternatives": [
        {
            "name": "Milk 2%",
            "calories": 50,
            "proteins": 3.3,
            "carbs": 4.8,
            "fats": 1.9,
            "portion_size": 100,
            "base_unit": "ml",
            "conversion_factor": 1.0
        },
        {
            "name": "Almond Milk",
            "calories": 13,
            "proteins": 0.4,
            "carbs": 0.3,
            "fats": 1.1,
            "portion_size": 100,
            "base_unit": "ml",
            "conversion_factor": 1.0
        },
        {
            "name": "Cheddar Cheese",
            "calories": 402,
            "proteins": 25,
            "carbs": 1.3,
            "fats": 33,
            "portion_size": 100,
            "base_unit": "g",
            "conversion_factor": 1.0
        }
    ]
}

def init_food_sources():
    """Initialize food sources with enhanced unit handling"""
    conn = db.get_connection()
    c = conn.cursor()
    
    # Clear existing food sources
    c.execute('DELETE FROM food_sources')
    
    # Insert new food sources
    for category, foods in food_sources.items():
        for food in foods:
            try:
                c.execute('''
                    INSERT INTO food_sources (
                        name, category, calories, proteins, carbs, fats, 
                        portion_size, base_unit, conversion_factor
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    food["name"],
                    category,
                    food["calories"],
                    food["proteins"],
                    food["carbs"],
                    food["fats"],
                    food["portion_size"],
                    food["base_unit"],
                    food["conversion_factor"]
                ))
            except Exception as e:
                print(f"Error inserting {food['name']}: {e}")
    
    conn.commit()
    conn.close()
    print(f"Successfully added {sum(len(foods) for foods in food_sources.values())} food sources")

def verify_food_sources():
    """Verify that food sources were initialized correctly"""
    foods_df = db.load_food_sources()
    
    if foods_df.empty:
        print("No food sources found in the database!")
        return
    
    print("\nFood sources by category:")
    for category in foods_df['category'].unique():
        print(f"\n{category}:")
        category_foods = foods_df[foods_df['category'] == category]
        print(category_foods[['name', 'calories', 'proteins', 'carbs', 'fats', 
                              'portion_size', 'base_unit', 'conversion_factor']].to_string())
    
    print(f"\nTotal food sources: {len(foods_df)}")

# Check if there are already food sources in the database
    existing_foods = db.load_food_sources()
    
    if not existing_foods.empty:
        response = input("Food sources already exist in the database. Do you want to reset? (y/n): ")
        if response.lower() != 'y':
            print("Initialization aborted.")
            exit()
    
    # Initialize food sources
    init_food_sources()
    
    # Verify the data
    verify_food_sources()