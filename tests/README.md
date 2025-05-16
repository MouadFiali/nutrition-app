# Nutrition App Test Data Generator

This generator creates realistic test data for the Nutrition App application to facilitate testing and demonstration.

## Data Generated

1. **User Profile**
   - Height: 1.69m
   - Weight: 67kg
   - Gender: Male
   - Age: 23
   - Activity Level: Lightly Active
   - Goal: Weight Loss (10% deficit)

2. **Food Sources (20+ items)**
   - Protein sources (chicken, eggs, fish, etc.)
   - Complex carbohydrates (rice, oats, etc.)
   - Healthy fats (avocado, nuts, oils)
   - Fruits (berries, bananas, etc.)

3. **Meals (20+ items)**
   - Regular meals (composed of food sources)
     - 3+ breakfast options
     - 3+ lunch options
     - 3+ dinner options
     - 3+ snack options
   - Custom meals (with manually defined macros)
     - Multiple options for each meal category

4. **Meal Program**
   - Dynamic program covering the last 30 days up to today
   - Scheduled meals for each day and meal time
   - Realistic meal patterns (consistent breakfasts, varied dinners)

5. **Meal Tracking Data**
   - Tracks meals based on the generated program
   - Falls back to last 15 days if no program exists
   - Includes variation from the plan (substitutions, skipped meals)
   - Realistic timestamps and occasional notes

## Usage

### Setup

Place these files in a `tests` directory within your project structure:
```
/nutrition_app/
├── tests/
│   ├── test_data_generator.py      # Main generator script
│   ├── test_data_generator_1.py    # Profile & Foods
│   ├── test_data_generator_2.py    # Meals
│   ├── test_data_generator_3.py    # Meal Program
│   ├── test_data_generator_4.py    # Meal Tracking
│   └── README.md                   # This file
```
Make sure your database file (`nutrition_app.db`) is accessible. If you want to start fresh, delete any existing database file.

### Running the Generator

From the project root directory:
```
python tests/test_data_generator.py
```

This will populate the database with all necessary test data. Progress information will be displayed during the process.

### Running Individual Components

You can run specific parts of the generator if needed:

```bash
# Profile and Food Sources
python tests/test_data_generator_1.py

# Meals
python tests/test_data_generator_2.py

# Meal Program (last 30 days)
python tests/test_data_generator_3.py

# Meal Tracking (based on program or last 15 days)
python tests/test_data_generator_4.py
```

**Important**: Always run scripts from the project root directory to ensure the database is created in the correct location.

## Key Features

### Dynamic Date Ranges

- The meal program generator creates programs from 30 days ago up to today
- The meal tracking generator dynamically tracks meals from the program's start date to today
- If no program exists, tracking defaults to the last 15 days

### Realistic Patterns

- Weekday/weekend meal variations
- Appropriate meal times (breakfast in morning, dinner in evening)
- Variable meal frequency (occasional skipped meals)
- Realistic substitution patterns (20% chance of meal substitution)

### Notes and Variations

- Tracking includes realistic notes about meals
- Timestamps are generated appropriately for each meal time
- Today's timestamps are always in the past (never in the future)

## Customization

You can customize the generated data by editing the scripts:

- Modify the profile details in `test_data_generator_1.py`
- Add/change food sources in `test_data_generator_1.py`
- Create different meal options in `test_data_generator_2.py`
- Adjust the program generation patterns in `test_data_generator_3.py`
- Change tracking behavior in `test_data_generator_4.py`

## Notes

- Running the generator multiple times may create duplicate entries for some items
- It's recommended to start with a fresh database when generating test data
- Some aspects use random selection, so each run will produce slightly different results