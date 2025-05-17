"""
Constants module for the Nutrition App.

This module defines enums and constants used throughout the application to ensure
consistency and maintainability.
"""

from enum import Enum, auto
from typing import Dict, List, Union, TypedDict
from dataclasses import dataclass


class ActivityLevel(Enum):
    """Enum for user activity levels with associated multipliers."""
    SEDENTARY = "Sedentary"
    LIGHTLY_ACTIVE = "Lightly Active"
    VERY_ACTIVE = "Very Active"
    EXTREMELY_ACTIVE = "Extremely Active"

    @classmethod
    def as_list(cls) -> List[str]:
        """Return all activity levels as a list of strings."""
        return [level.value for level in cls]

    @classmethod
    def get_multiplier(cls, level: Union[str, 'ActivityLevel']) -> float:
        """Get the TDEE multiplier for a given activity level."""
        multipliers = {
            cls.SEDENTARY: 1.2,
            cls.LIGHTLY_ACTIVE: 1.24,
            cls.VERY_ACTIVE: 1.4,
            cls.EXTREMELY_ACTIVE: 1.62
        }
        
        if isinstance(level, str):
            for activity_level in cls:
                if activity_level.value == level:
                    return multipliers[activity_level]
            raise ValueError(f"Unknown activity level: {level}")
        
        return multipliers[level]


class GoalType(Enum):
    """Enum for fitness goal types."""
    WEIGHT_LOSS = "Weight Loss"
    MAINTENANCE = "Maintenance"
    WEIGHT_GAIN = "Weight Gain"

    @classmethod
    def as_list(cls) -> List[str]:
        """Return all goal types as a list of strings."""
        return [goal.value for goal in cls]


class MealCategory(Enum):
    """Enum for meal categories."""
    BREAKFAST = "Breakfast"
    LUNCH_DINNER = "Lunch/Dinner"  # New category for meals suitable for both lunch and dinner
    SNACKS = "Snacks"

    @classmethod
    def as_list(cls) -> List[str]:
        """Return all meal categories as a list of strings."""
        return [category.value for category in cls]


class MealTime(Enum):
    """Enum for specific meal times throughout the day."""
    BREAKFAST = "Breakfast"
    MORNING_SNACK = "Morning Snack"
    LUNCH = "Lunch"
    AFTERNOON_SNACK = "Afternoon Snack"
    DINNER = "Dinner"

    @classmethod
    def as_list(cls) -> List[str]:
        """Return all meal times as a list of strings."""
        return [time.value for time in cls]

    @classmethod
    def get_category(cls, meal_time: Union[str, 'MealTime']) -> str:
        """Map a meal time to its corresponding meal category."""
        meal_time_to_category = {
            cls.BREAKFAST: MealCategory.BREAKFAST.value,
            cls.MORNING_SNACK: MealCategory.SNACKS.value,
            cls.AFTERNOON_SNACK: MealCategory.SNACKS.value,
            cls.LUNCH: MealCategory.LUNCH_DINNER.value,
            cls.DINNER: MealCategory.LUNCH_DINNER.value,
        }
        
        if isinstance(meal_time, str):
            for time in cls:
                if time.value == meal_time:
                    return meal_time_to_category[time]
            raise ValueError(f"Unknown meal time: {meal_time}")
        
        return meal_time_to_category[meal_time]


class FoodCategory(Enum):
    """Enum for food categories."""
    PROTEIN_SOURCES = "Protein Sources"
    COMPLEX_CARBOHYDRATES = "Complex Carbohydrates"
    HEALTHY_FATS = "Healthy Fats"
    FRUITS = "Fruits"

    @classmethod
    def as_list(cls) -> List[str]:
        """Return all food categories as a list of strings."""
        return [category.value for category in cls]


class BaseUnit(Enum):
    """Enum for base units of measurement for food."""
    GRAMS = "g"
    MILLILITERS = "ml"
    UNIT = "unit"

    @classmethod
    def as_list(cls) -> List[str]:
        """Return all base units as a list of strings."""
        return [unit.value for unit in cls]


# Nutrition constants
@dataclass
class NutritionConstants:
    """Constants for nutrition calculations."""
    PROTEIN_CALORIES_PER_GRAM: float = 4.0
    CARB_CALORIES_PER_GRAM: float = 4.0
    FAT_CALORIES_PER_GRAM: float = 9.0
    
    # Default goal percentages
    DEFAULT_PROTEIN_PERCENTAGE: float = 30.0  # % of total calories
    DEFAULT_CARB_PERCENTAGE: float = 45.0     # % of total calories
    DEFAULT_FAT_PERCENTAGE: float = 25.0      # % of total calories
    
    # Default target values for macros
    PROTEIN_PER_KG_BODYWEIGHT: float = 2.0  # g/kg bodyweight


# UI Constants
DAYS_PER_PAGE: int = 7
DEFAULT_FOOD_SLOTS: int = 3