"""
Nutrition calculation utilities for the Nutrition App.

This module provides common functions for calculating nutritional data:
- BMR (Basal Metabolic Rate)
- TDEE (Total Daily Energy Expenditure)
- Target calories based on goals
- Macro nutrient targets
- Macro breakdowns for meals
"""
from typing import Dict, Tuple, Optional, Union, List, Any
import pandas as pd
from utils.constants import ActivityLevel, GoalType, NutritionConstants

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation.
    
    Args:
        weight: Weight in kg
        height: Height in meters
        age: Age in years
        gender: 'Male' or 'Female'
        
    Returns:
        BMR in calories per day
    """
    if gender == "Male":
        return 10 * weight + 6.25 * height * 100 - 5 * age + 5
    else:  # Female
        return 10 * weight + 6.25 * height * 100 - 5 * age - 161

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure (TDEE) based on BMR and activity level.
    
    Args:
        bmr: Basal Metabolic Rate in calories per day
        activity_level: Activity level as string (e.g., "Sedentary", "Lightly Active")
        
    Returns:
        TDEE in calories per day
    """
    return bmr * ActivityLevel.get_multiplier(activity_level)

def calculate_target_calories(tdee: float, goal_type: str, goal_percentage: float) -> float:
    """
    Calculate target calories based on TDEE, goal type, and goal percentage.
    
    Args:
        tdee: Total Daily Energy Expenditure in calories per day
        goal_type: Type of goal ("Weight Loss", "Maintenance", "Weight Gain")
        goal_percentage: Percentage to adjust calories by (for weight loss/gain)
        
    Returns:
        Target calories per day
    """
    if goal_type == GoalType.WEIGHT_LOSS.value:
        return tdee * (1 - goal_percentage/100)
    elif goal_type == GoalType.WEIGHT_GAIN.value:
        return tdee * (1 + goal_percentage/100)
    else:  # Maintenance
        return tdee
    
def calculate_food_macros(food: Dict[str, Any], quantity: float) -> Dict[str, float]:
    """
    Calculate macros for a single food item based on quantity.
    
    Args:
        food: Dictionary containing food source data (calories, proteins, carbs, fats, base_unit, conversion_factor)
        quantity: Amount of food in the base unit
        
    Returns:
        Dict with keys 'calories', 'proteins', 'carbs', 'fats' containing calculated values
    """
    # Calculate factor based on base unit
    if food['base_unit'] in ['g', 'ml']:
        factor = quantity / 100  # Convert to 100g/ml basis
    else:  # unit-based foods
        factor = quantity * food['conversion_factor'] / 100  # Convert units to grams then to 100g basis
    
    return {
        'calories': food['calories'] * factor,
        'proteins': food['proteins'] * factor,
        'carbs': food['carbs'] * factor,
        'fats': food['fats'] * factor
    }

def calculate_meal_macros(foods_data: Union[pd.DataFrame, List[Dict[str, Any]]], 
                        quantities: Optional[Dict[str, Dict]] = None) -> Dict[str, float]:
    """
    Calculate total macros for a meal based on its foods.
    
    This function can work with either:
    1. A DataFrame of foods + a dictionary of quantities
    2. A list of food dictionaries that already include quantities
    
    Args:
        foods_data: Either a DataFrame of food sources or a list of food dictionaries with quantities
        quantities: Optional dict mapping food names to quantity data (only used with DataFrame)
        
    Returns:
        Dict with keys 'calories', 'proteins', 'carbs', 'fats' containing totals
    """
    total_calories = 0
    total_proteins = 0
    total_carbs = 0
    total_fats = 0
    
    # Case 1: DataFrame of foods + quantities dict
    if isinstance(foods_data, pd.DataFrame) and quantities is not None:
        for food_name, data in quantities.items():
            quantity = data['quantity']
            if quantity > 0:
                food = foods_data[foods_data['name'] == food_name]
                if not food.empty:
                    food = food.iloc[0]
                    macros = calculate_food_macros(food, quantity)
                    
                    total_calories += macros['calories']
                    total_proteins += macros['proteins']
                    total_carbs += macros['carbs']
                    total_fats += macros['fats']
    
    # Case 2: List of food dictionaries that include quantities
    elif isinstance(foods_data, list):
        for food in foods_data:
            if 'quantity' in food and food['quantity'] > 0:
                macros = calculate_food_macros(food, food['quantity'])
                
                total_calories += macros['calories']
                total_proteins += macros['proteins']
                total_carbs += macros['carbs']
                total_fats += macros['fats']
    
    return {
        'calories': round(total_calories, 1),
        'proteins': round(total_proteins, 1),
        'carbs': round(total_carbs, 1),
        'fats': round(total_fats, 1)
    }

def calculate_macro_percentages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate macro percentages for given dataframe with nutrition data.
    
    Args:
        df: DataFrame containing 'calories', 'proteins', 'carbs', 'fats' columns
        
    Returns:
        DataFrame with additional columns for macro percentages
    """
    constants = NutritionConstants()
    
    # Create a copy to avoid modifying original
    result_df = df.copy()
    
    # Filter to only rows with calories > 0 to avoid division by zero
    with_calories = result_df[result_df['calories'] > 0]
    
    # Calculate percentages
    with_calories['proteins_pct'] = (with_calories['proteins'] * constants.PROTEIN_CALORIES_PER_GRAM / 
                                    with_calories['calories'] * 100).round(1)
    with_calories['carbs_pct'] = (with_calories['carbs'] * constants.CARB_CALORIES_PER_GRAM / 
                                 with_calories['calories'] * 100).round(1)
    with_calories['fats_pct'] = (with_calories['fats'] * constants.FAT_CALORIES_PER_GRAM / 
                                with_calories['calories'] * 100).round(1)
    
    # Update the original DataFrame where calories > 0
    result_df.update(with_calories)
    
    return result_df

def calculate_meal_macros_from_record(meal: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate macros for a meal from a database record.
    
    Args:
        meal: Dictionary containing meal data (including 'type' and possibly 'foods')
        
    Returns:
        Dict with keys 'calories', 'proteins', 'carbs', 'fats' containing calculated values
    """
    # For custom meals, return the stored macros
    if meal['type'] == 'custom':
        return {
            'calories': round(meal['calories'], 1),
            'proteins': round(meal['proteins'], 1),
            'carbs': round(meal['carbs'], 1),
            'fats': round(meal['fats'], 1)
        }
    
    # For regular meals, calculate macros from foods
    elif meal['type'] == 'regular' and 'foods' in meal and meal['foods']:
        return calculate_meal_macros(meal['foods'])
    
    # Default to zeros if no data available
    return {
        'calories': 0,
        'proteins': 0,
        'carbs': 0,
        'fats': 0
    }

def process_meals_data(meals_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process meals data to ensure all meals have calculated macros.
    
    Args:
        meals_df: DataFrame containing meals data
        
    Returns:
        DataFrame with added/updated macros columns
    """
    # Create a copy to avoid modifying original
    result_df = meals_df.copy()
    
    # Calculate macros for regular meals
    for idx, meal in result_df.iterrows():
        if meal['type'] == 'regular':
            if 'foods' in meal and meal['foods']:
                macros = calculate_meal_macros(meal['foods'])
                result_df.at[idx, 'calories'] = macros['calories']
                result_df.at[idx, 'proteins'] = macros['proteins']
                result_df.at[idx, 'carbs'] = macros['carbs']
                result_df.at[idx, 'fats'] = macros['fats']
    
    return result_df

def calculate_all_metrics(
    weight: float, 
    height: float, 
    age: int, 
    gender: str, 
    activity_level: str, 
    goal_type: str, 
    goal_percentage: float
) -> Tuple[float, float, float]:
    """
    Calculate all profile metrics at once: BMR, TDEE, and target calories.
    
    Args:
        weight: Weight in kg
        height: Height in meters
        age: Age in years
        gender: 'Male' or 'Female'
        activity_level: Activity level (e.g., "Sedentary", "Lightly Active")
        goal_type: Type of goal ("Weight Loss", "Maintenance", "Weight Gain")
        goal_percentage: Percentage to adjust calories by (for weight loss/gain)
        
    Returns:
        Tuple of (BMR, TDEE, target_calories)
    """
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    target_calories = calculate_target_calories(tdee, goal_type, goal_percentage)
    
    return round(bmr, 0), round(tdee, 0), round(target_calories, 0)

def calculate_macro_targets(
    weight: float, 
    target_calories: float, 
    protein_per_kg: Optional[float] = None,
    carb_percentage: Optional[float] = None,
    fat_percentage: Optional[float] = None
) -> Dict[str, float]:
    """
    Calculate macro targets based on weight and target calories.
    
    Args:
        weight: Weight in kg
        target_calories: Target calories per day
        protein_per_kg: Grams of protein per kg of bodyweight (default from NutritionConstants)
        carb_percentage: Percentage of calories from carbs (default from NutritionConstants)
        fat_percentage: Percentage of calories from fat (default from NutritionConstants)
        
    Returns:
        Dict with keys 'protein', 'carbs', 'fats' containing target grams per day
    """
    constants = NutritionConstants()
    
    # Use provided values or defaults
    protein_per_kg = protein_per_kg or constants.PROTEIN_PER_KG_BODYWEIGHT
    carb_percentage = carb_percentage or constants.DEFAULT_CARB_PERCENTAGE
    fat_percentage = fat_percentage or constants.DEFAULT_FAT_PERCENTAGE
    
    # Calculate protein target based on bodyweight
    protein_target = weight * protein_per_kg
    
    # Calculate calories from protein
    protein_calories = protein_target * constants.PROTEIN_CALORIES_PER_GRAM
    
    # Calculate remaining calories to distribute between carbs and fats
    remaining_calories = target_calories - protein_calories
    
    # Adjust carb and fat percentages to distribute remaining calories
    total_percentage = carb_percentage + fat_percentage
    adjusted_carb_percentage = (carb_percentage / total_percentage) * 100
    adjusted_fat_percentage = (fat_percentage / total_percentage) * 100
    
    # Calculate carbs and fats based on adjusted percentages
    carbs_target = (remaining_calories * (adjusted_carb_percentage / 100)) / constants.CARB_CALORIES_PER_GRAM
    fats_target = (remaining_calories * (adjusted_fat_percentage / 100)) / constants.FAT_CALORIES_PER_GRAM
    
    return {
        'protein': round(protein_target, 0),
        'carbs': round(carbs_target, 0),
        'fats': round(fats_target, 0)
    }

def get_macro_distribution(macros: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate the percentage distribution of macros.
    
    Args:
        macros: Dict with keys 'calories', 'proteins', 'carbs', 'fats'
        
    Returns:
        Dict with keys 'proteins_pct', 'carbs_pct', 'fats_pct' containing percentages
    """
    constants = NutritionConstants()
    
    # Calculate total calories from macros
    protein_cals = macros['proteins'] * constants.PROTEIN_CALORIES_PER_GRAM
    carb_cals = macros['carbs'] * constants.CARB_CALORIES_PER_GRAM
    fat_cals = macros['fats'] * constants.FAT_CALORIES_PER_GRAM
    
    total_cals = protein_cals + carb_cals + fat_cals
    
    # Avoid division by zero
    if total_cals == 0:
        return {
            'proteins_pct': 0,
            'carbs_pct': 0,
            'fats_pct': 0
        }
    
    return {
        'proteins_pct': round((protein_cals / total_cals) * 100, 1),
        'carbs_pct': round((carb_cals / total_cals) * 100, 1),
        'fats_pct': round((fat_cals / total_cals) * 100, 1)
    }

def get_macro_compliance(
    macros: Dict[str, float], 
    targets: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate compliance percentages for macros against targets.
    
    Args:
        macros: Dict with keys 'proteins', 'carbs', 'fats'
        targets: Dict with keys 'protein', 'carbs', 'fats'
        
    Returns:
        Dict with keys 'calories_pct', 'proteins_pct', 'carbs_pct', 'fats_pct' 
        containing compliance percentages
    """
    constants = NutritionConstants()
    
    # Calculate total calories
    macros_calories = (macros['proteins'] * constants.PROTEIN_CALORIES_PER_GRAM +
                      macros['carbs'] * constants.CARB_CALORIES_PER_GRAM +
                      macros['fats'] * constants.FAT_CALORIES_PER_GRAM)
    
    target_calories = (targets['protein'] * constants.PROTEIN_CALORIES_PER_GRAM +
                      targets['carbs'] * constants.CARB_CALORIES_PER_GRAM +
                      targets['fats'] * constants.FAT_CALORIES_PER_GRAM)
    
    # Calculate compliance percentages (with bounds)
    return {
        'calories_pct': min(100, round((macros_calories / target_calories) * 100 if target_calories else 0, 1)),
        'proteins_pct': min(100, round((macros['proteins'] / targets['protein']) * 100 if targets['protein'] else 0, 1)),
        'carbs_pct': min(100, round((macros['carbs'] / targets['carbs']) * 100 if targets['carbs'] else 0, 1)),
        'fats_pct': min(100, round((macros['fats'] / targets['fats']) * 100 if targets['fats'] else 0, 1))
    }