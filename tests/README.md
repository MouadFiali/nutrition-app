# Nutrition Planner Test Data Generator

This test data generator creates a comprehensive set of demo data for the Nutrition Planner application. It populates the database with realistic data for all application features, allowing for thorough testing and demonstration.

## What Data Is Generated

The generator creates:

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
   - A month-long program (May 1-31, 2025)
   - Contains scheduled meals for each day and meal time
   - Follows realistic meal patterns (e.g., consistent breakfast on weekdays)

5. **Meal Tracking Data**
   - Tracked meals from May 1 to May 16, 2025
   - Mix of meals from the program and substitutions
   - Realistic timestamps for each meal time
   - Occasional notes for added realism

## Installation and Usage

### Prerequisites
- Python 3.7+
- The Nutrition Planner application installed with database setup

### Setup

1. Place all test data generator files in a `tests` directory within your project:
   ```
   /nutrition_app/
   ├── tests/
   │   ├── test_data_generator.py
   │   ├── test_data_generator_1.py
   │   ├── test_data_generator_2.py
   │   ├── test_data_generator_3.py
   │   ├── test_data_generator_4.py
   ├── utils/
   │   ├── constants.py
   │   ├── db_manager.py
   │   └── ...
   └── ...
   ```

2. Make sure your database file (`nutrition_app.db`) is accessible. If you want to start fresh, delete any existing database file.

### Running the Generator

1. Navigate to the project root directory:
   ```
   cd nutrition_app
   ```

2. Run the main generator script:
   ```
   python tests/test_data_generator.py
   ```

3. Confirm when prompted to begin the data generation process.

4. The script will populate the database with all the test data, displaying progress information along the way.

### Running Individual Parts

You can also run individual parts of the data generator if you only need specific data:

- **Profile and Food Sources**:
  ```
  python tests/test_data_generator_1.py
  ```

- **Meals**:
  ```
  python tests/test_data_generator_2.py
  ```

- **Meal Program**:
  ```
  python tests/test_data_generator_3.py
  ```

- **Meal Tracking**:
  ```
  python tests/test_data_generator_4.py
  ```

### Note

It is necessary to run the scripts from the root directory of the project to ensure that the db is created in the correct location. If done from a different directory, make sure to move the resulting database file (nutrition_app.db) to the correct location (`/nutrition_app/`).
## Testing the Application

After running the data generator, you can test all features of the Nutrition Planner application:

1. **Profile Management**
   - View the created profile
   - Update profile information
   - See calculated metrics (BMR, TDEE, calorie targets)

2. **Food Source Management**
   - Browse the created food sources
   - Filter by categories
   - Edit food information
   - Add new foods

3. **Meal Management**
   - View regular and custom meals
   - See meal nutritional information
   - Create new meals

4. **Meal Programs**
   - View the created May 2025 program
   - Navigate through the calendar
   - Edit scheduled meals
   - Create new programs

5. **Meal Tracking**
   - View tracked meals
   - Track new meals
   - See progress and statistics

## Customization

You can modify the generator scripts to create different types of data:

- Edit the profile information in `test_data_generator_1.py`
- Add or modify food sources in `test_data_generator_1.py`
- Create different meals in `test_data_generator_2.py`
- Change the program dates in `test_data_generator_3.py`
- Adjust the tracking period in `test_data_generator_4.py`

## Notes

- Running the generator multiple times will create duplicate entries for some items, leading to potential database integrity errors. It's recommended to start with a fresh database.
- The generator uses random selection for some aspects, so the exact data will vary between runs.