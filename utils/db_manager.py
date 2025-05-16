import sqlite3
import pandas as pd
from datetime import datetime
from utils.constants import MealTime

class NutritionDB:
    def __init__(self, db_name='nutrition_app.db'):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Create profile table (unchanged)
        c.execute('''
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY,
                weight REAL,
                height REAL,
                age INTEGER,
                activity_level TEXT,
                gender TEXT,
                goal_type TEXT,
                goal_percentage REAL,
                last_updated TIMESTAMP
            )
        ''')
        
        # Update food sources table with new fields
        c.execute('''
            CREATE TABLE IF NOT EXISTS food_sources (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                category TEXT,
                calories REAL,
                proteins REAL,
                carbs REAL,
                fats REAL,
                portion_size REAL,
                base_unit TEXT,  -- 'g', 'ml', or 'unit'
                conversion_factor REAL DEFAULT 1.0  -- conversion to grams if needed
            )
        ''')

        # Create meals table - now macros are only stored for custom meals
        c.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                category TEXT,
                type TEXT,
                calories REAL,  -- Only used for custom meals
                proteins REAL,  -- Only used for custom meals
                carbs REAL,     -- Only used for custom meals
                fats REAL,      -- Only used for custom meals
                created_at TIMESTAMP
            )
        ''')
        
        # Create meal_foods table (unchanged)
        c.execute('''
            CREATE TABLE IF NOT EXISTS meal_foods (
                id INTEGER PRIMARY KEY,
                meal_id INTEGER,
                food_id INTEGER,
                quantity REAL,
                FOREIGN KEY (meal_id) REFERENCES meals (id) ON DELETE CASCADE,
                FOREIGN KEY (food_id) REFERENCES food_sources (id) ON DELETE CASCADE
            )
        ''')

        # Table to store meal programs
        c.execute('''
            CREATE TABLE IF NOT EXISTS meal_programs (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table to store meals in a program
        c.execute('''
            CREATE TABLE IF NOT EXISTS program_meals (
                id INTEGER PRIMARY KEY,
                program_id INTEGER NOT NULL,
                meal_id INTEGER NOT NULL,
                date DATE NOT NULL,
                meal_time TEXT NOT NULL,
                FOREIGN KEY (program_id) REFERENCES meal_programs (id) ON DELETE CASCADE,
                FOREIGN KEY (meal_id) REFERENCES meals (id) ON DELETE CASCADE
            )
        ''')
        
        # Table to track actual meals eaten
        c.execute('''
            CREATE TABLE IF NOT EXISTS meal_tracking (
                id INTEGER PRIMARY KEY,
                date DATE NOT NULL,
                meal_id INTEGER NOT NULL,
                meal_time TEXT NOT NULL,
                actual_time TIMESTAMP NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meal_id) REFERENCES meals (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_profile(self, weight, height, age, activity_level, gender, goal_type, goal_percentage):
        """Save or update profile information"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Delete existing profile (we'll only keep one profile for now)
        c.execute('DELETE FROM profile')
        
        # Insert new profile
        c.execute('''
            INSERT INTO profile (
                weight, height, age, activity_level, gender, 
                goal_type, goal_percentage, last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (weight, height, age, activity_level, gender, 
              goal_type, goal_percentage, datetime.now()))
        
        conn.commit()
        conn.close()

    def load_profile(self):
        """Load the most recent profile"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM profile ORDER BY last_updated DESC LIMIT 1')
        profile = c.fetchone()
        
        conn.close()
        return profile
    
    def get_app_stats(self):
        """Return counts for food_sources, meals, meal_programs, and meal_tracking tables."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM food_sources")
        food_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM meals")
        meal_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM meal_programs")
        program_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM meal_tracking")
        tracking_count = c.fetchone()[0]
        conn.close()
        return {
            "food_sources": food_count,
            "meals": meal_count,
            "meal_programs": program_count,
            "meal_tracking": tracking_count
        }

    def load_food_sources(self):
        """Load all food sources"""
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT * FROM food_sources', conn)
        conn.close()
        return df

    def save_food_source(self, name, category, calories, proteins, carbs, fats, 
                        portion_size, base_unit, conversion_factor=1.0):
        """Save a new food source with simplified unit handling"""
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO food_sources (
                    name, category, calories, proteins, carbs, fats, 
                    portion_size, base_unit, conversion_factor
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, category, calories, proteins, carbs, fats, 
                portion_size, base_unit, conversion_factor
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def update_food_source(self, food_id, name, category, calories, proteins, 
                         carbs, fats, portion_size, base_unit, conversion_factor=1.0):
        """Update an existing food source"""
        # Ensure food_id is an integer
        food_id = int(food_id)
        
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                UPDATE food_sources 
                SET name=?, category=?, calories=?, proteins=?, carbs=?, fats=?, 
                    portion_size=?, base_unit=?, conversion_factor=?
                WHERE id=?
            ''', (
                name, category, calories, proteins, carbs, fats, 
                portion_size, base_unit, conversion_factor, food_id
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_multiple_food_sources(self, food_names):
        """Delete multiple food sources by their names"""
        if not food_names:
            return
            
        conn = self.get_connection()
        c = conn.cursor()
        
        placeholders = ','.join('?' * len(food_names))
        c.execute(f'DELETE FROM food_sources WHERE name IN ({placeholders})', food_names)
        
        conn.commit()
        conn.close()

    def save_meal(self, name, category, meal_type, foods_quantities=None, custom_macros=None):
        """Save a new meal
        
        Args:
            name (str): Meal name
            category (str): breakfast, lunch, dinner, or snacks
            meal_type (str): regular or custom
            foods_quantities (dict): {food_name: quantity} for regular meals
            custom_macros (dict): {calories, proteins, carbs, fats} for custom meals
        """
        conn = self.get_connection()
        c = conn.cursor()
        
        if meal_type == "custom":
            # For custom meals, store the macros directly
            c.execute('''
                INSERT INTO meals (
                    name, category, type, calories, proteins, carbs, fats, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, category, meal_type,
                custom_macros['calories'], custom_macros['proteins'],
                custom_macros['carbs'], custom_macros['fats'],
                datetime.now()
            ))
        else:
            # For regular meals, don't store the macros (they will be calculated when needed)
            c.execute('''
                INSERT INTO meals (
                    name, category, type, created_at
                ) VALUES (?, ?, ?, ?)
            ''', (
                name, category, meal_type, datetime.now()
            ))

        try:
            if meal_type == "regular" and foods_quantities:
                meal_id = c.lastrowid
                
                # Get food IDs for the food names
                for food_name, data in foods_quantities.items():
                    food_id = int(data['id'])
                    quantity = data['quantity']    
                    # Add food quantity
                    c.execute('''
                        INSERT INTO meal_foods (meal_id, food_id, quantity)
                        VALUES (?, ?, ?)
                    ''', (meal_id, food_id, quantity))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_meal_with_foods(self, meal_id):
        """Get meal details including its foods if it's a regular meal"""
        # Ensure meal_id is an integer
        meal_id = int(meal_id)
        
        conn = self.get_connection()
        
        # Get meal basic info
        meal_query = 'SELECT * FROM meals WHERE id = ?'
        meal_df = pd.read_sql_query(meal_query, conn, params=(meal_id,))
        
        if meal_df.empty:
            conn.close()
            return None
            
        meal = meal_df.iloc[0].to_dict()

        if meal['type'] == 'regular':
            # Get meal foods
            foods_query = '''
                SELECT f.*, mf.quantity 
                FROM food_sources f
                JOIN meal_foods mf ON f.id = mf.food_id
                WHERE mf.meal_id = ?
            '''
            foods_df = pd.read_sql_query(foods_query, conn, params=(meal_id,))
            meal['foods'] = foods_df.to_dict('records')
        
        conn.close()
        return meal

    def get_all_meals(self):
        """Get all meals with their foods for calculation"""
        conn = self.get_connection()
        
        # Get all meals
        meals = pd.read_sql_query('SELECT * FROM meals', conn)
        
        # If we have any regular meals, we need to get their food ingredients
        if not meals.empty:
            # Ensure the 'foods' column is initialized as an object type to store lists
            meals['foods'] = [[] for _ in range(len(meals))]
            
            regular_meals = meals[meals['type'] == 'regular']
            
            if not regular_meals.empty:
                # For each regular meal, get its foods
                for idx, meal in regular_meals.iterrows():
                    meal_id = int(meal['id'])
                    
                    # Get foods for this meal
                    foods_query = '''
                        SELECT f.*, mf.quantity 
                        FROM food_sources f
                        JOIN meal_foods mf ON f.id = mf.food_id
                        WHERE mf.meal_id = ?
                    '''
                    foods = pd.read_sql_query(foods_query, conn, params=(meal_id,))
                    
                    if not foods.empty:
                        # Store the foods as a list of dictionaries in a new column
                        meals.at[idx, 'foods'] = foods.to_dict('records')
        
        conn.close()
        return meals
    
    def get_regular_meals(self):
        """Get all regular meals with their foods"""
        conn = self.get_connection()
        meals = pd.read_sql_query('SELECT * FROM meals WHERE type = "regular"', conn)
        
        if not meals.empty:
            # Initialize the 'foods' column with empty lists
            meals['foods'] = [[] for _ in range(len(meals))]
            
            # For each regular meal, get its foods
            for idx, meal in meals.iterrows():
                meal_id = int(meal['id'])
                
                # Get foods for this meal
                foods_query = '''
                    SELECT f.*, mf.quantity 
                    FROM food_sources f
                    JOIN meal_foods mf ON f.id = mf.food_id
                    WHERE mf.meal_id = ?
                '''
                foods = pd.read_sql_query(foods_query, conn, params=(meal_id,))

                if not foods.empty:
                    # Store the foods as a list of dictionaries in a new column
                    meals.at[idx, 'foods'] = foods.to_dict('records')
        
        conn.close()
        return meals
    
    def get_custom_meals(self):
        """Get all custom meals"""
        conn = self.get_connection()
        meals = pd.read_sql_query('SELECT * FROM meals WHERE type = "custom"', conn)
        conn.close()
        return meals

    def update_meal(self, meal_id, name, category, foods_quantities=None, custom_macros=None):
        """Update an existing meal"""
        # Ensure meal_id is an integer
        meal_id = int(meal_id)
        
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            meal = pd.read_sql_query(
                'SELECT type FROM meals WHERE id = ?',
                conn,
                params=(meal_id,)
            ).iloc[0]

            if meal['type'] == 'custom':
                # For custom meals, update the macros
                c.execute('''
                    UPDATE meals 
                    SET name=?, category=?, calories=?, proteins=?, carbs=?, fats=?
                    WHERE id=?
                ''', (
                    name, category,
                    custom_macros['calories'], custom_macros['proteins'],
                    custom_macros['carbs'], custom_macros['fats'],
                    meal_id
                ))
            else:
                # For regular meals, only update name and category
                c.execute('''
                    UPDATE meals 
                    SET name=?, category=?
                    WHERE id=?
                ''', (
                    name, category, meal_id
                ))
            
            if meal['type'] == 'regular' and foods_quantities:
                # Update food quantities
                c.execute('DELETE FROM meal_foods WHERE meal_id = ?', (meal_id,))
                for food_name, data in foods_quantities.items():
                    food_id = int(data['id'])
                    quantity = data['quantity']
                    
                    c.execute('''
                        INSERT INTO meal_foods (meal_id, food_id, quantity)
                        VALUES (?, ?, ?)
                    ''', (meal_id, food_id, quantity))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_meal(self, meal_id):
        """Delete a meal and its food relations"""
        # Ensure meal_id is an integer
        meal_id = int(meal_id)
        
        conn = self.get_connection()
        c = conn.cursor()
        
        # Delete the meal
        c.execute('DELETE FROM meals WHERE id = ?', (meal_id,))
        
        # Check if the meal was deleted
        if c.rowcount == 0:
            print(f"No meal found with ID {meal_id}. Nothing was deleted.")
            conn.close()
            return False

        # Delete meal foods
        c.execute('DELETE FROM meal_foods WHERE meal_id = ?', (meal_id,))

        conn.commit()
        conn.close()
        return True

    def check_meal_in_programs(self, meal_id):
        """Check if a meal is used in any programs"""
        # Ensure meal_id is an integer
        meal_id = int(meal_id)
        
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT COUNT(*) 
            FROM program_meals 
            WHERE meal_id = ?
        ''', (meal_id,))
        
        count = c.fetchone()[0]
        conn.close()
        
        return count > 0
        
    def check_food_in_meals(self, food_names):
        """
        Check if food sources are used in any meals.
        Args:
            food_names: List of food names to check
        Returns:
            Dict with usage information if foods are in use
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        placeholders = ','.join(['?'] * len(food_names))
        query = f"""
            SELECT f.name as food_name, m.id as meal_id, m.name as meal_name, mf.quantity
            FROM food_sources f
            JOIN meal_foods mf ON f.id = mf.food_id
            JOIN meals m ON mf.meal_id = m.id
            WHERE f.name IN ({placeholders})
        """
        cursor.execute(query, food_names)
        results = cursor.fetchall()
        conn.close()
        if not results:
            return None
        foods_in_meals = {}
        meals_set = set()
        meal_names = {}
        for row in results:
            food_name, meal_id, meal_name, quantity = row
            if food_name not in foods_in_meals:
                foods_in_meals[food_name] = []
            foods_in_meals[food_name].append({
                'meal_id': meal_id,
                'meal_name': meal_name,
                'quantity': quantity
            })
            meals_set.add(meal_id)
            meal_names[meal_id] = meal_name
        return {
            'foods_in_meals': foods_in_meals,
            'total_meals': len(meals_set),
            'meals': [{'id': mid, 'name': meal_names[mid]} for mid in meals_set]
        }
    
    def check_meals_in_programs(self, meal_ids):
        """
        Check if any meals are used in programs.
        Args:
            meal_ids: List of meal IDs to check
        Returns:
            Dict with program info if meals are in programs
        """
        if not meal_ids:
            return None
        # Ensure meal_ids are integers
        meal_ids = [int(meal_id) for meal_id in meal_ids]

        conn = self.get_connection()
        cursor = conn.cursor()
        placeholders = ','.join(['?'] * len(meal_ids))
        query = f"""
            SELECT DISTINCT p.id, p.name
            FROM meal_programs p
            JOIN program_meals pm ON p.id = pm.program_id
            WHERE pm.meal_id IN ({placeholders})
        """
        cursor.execute(query, meal_ids)
        results = cursor.fetchall()
        conn.close()
        if not results:
            return None
        return {
            'programs': results,
            'total_programs': len(results)
        }

    def save_meal_program(self, name, start_date, end_date):
        """Save a new meal program"""
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO meal_programs (name, start_date, end_date)
                VALUES (?, ?, ?)
            ''', (name, start_date, end_date))
            program_id = c.lastrowid
            conn.commit()
            return program_id
        except Exception as e:
            print(f"Error saving meal program: {e}")
            return None
        finally:
            conn.close()

    def add_meal_to_program(self, program_id, meal_id, date, meal_time):
        """Add a meal to a program"""
        # Ensure ids are integers
        program_id = int(program_id)
        meal_id = int(meal_id)
        
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO program_meals (program_id, meal_id, date, meal_time)
                VALUES (?, ?, ?, ?)
            ''', (program_id, meal_id, date, meal_time))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding meal to program: {e}")
            return False
        finally:
            conn.close()

    def track_meal(self, date, meal_id, meal_time, actual_time, notes=None):
        """Track an actual meal eaten"""
        # Ensure meal_id is an integer
        meal_id = int(meal_id)
        
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO meal_tracking 
                (date, meal_id, meal_time, actual_time, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, meal_id, meal_time, actual_time, notes))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error tracking meal: {e}")
            return False
        finally:
            conn.close()

    def delete_tracked_meal(self, tracked_meal_id):
        """Delete a tracked meal entry by its ID."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM meal_tracking WHERE id = ?', (tracked_meal_id,))
        deleted = c.rowcount
        conn.commit()
        conn.close()
        return deleted > 0

    def get_program_meals(self, program_id, date=None):
        """Get meals for a program, optionally filtered by date"""
        # Ensure program_id is an integer
        program_id = int(program_id)
        
        conn = self.get_connection()
        
        query = '''
            SELECT pm.*, m.name as meal_name, m.category, m.type
            FROM program_meals pm
            JOIN meals m ON pm.meal_id = m.id
            WHERE pm.program_id = ?
        '''
        params = [program_id]
        
        if date:
            query += ' AND pm.date = ?'
            params.append(date)
            
        df = pd.read_sql_query(query, conn, params=params)
        
        # Get the food details for regular meals
        if not df.empty:
            # Add 'foods' column first with default empty lists
            df['foods'] = [[] for _ in range(len(df))]

            # Handle regular meals
            regular_meals = df[df['type'] == 'regular']
            
            if not regular_meals.empty:
                # For each regular meal, fetch its foods
                for idx, row in regular_meals.iterrows():
                    meal_id = int(row['meal_id'])
                    
                    foods_query = '''
                        SELECT f.*, mf.quantity
                        FROM food_sources f
                        JOIN meal_foods mf ON f.id = mf.food_id
                        WHERE mf.meal_id = ?
                    '''
                    foods = pd.read_sql_query(foods_query, conn, params=(meal_id,))
                    
                    if not foods.empty:
                        # Store the foods as a list of dictionaries
                        df.at[idx, 'foods'] = foods.to_dict('records')
            
            # Also get macros for custom meals
            custom_meals = df[df['type'] == 'custom']
            
            if not custom_meals.empty:
                for idx, row in custom_meals.iterrows():
                    meal_id = int(row['meal_id'])
                    
                    macros_query = '''
                        SELECT calories, proteins, carbs, fats
                        FROM meals
                        WHERE id = ?
                    '''
                    macros = pd.read_sql_query(macros_query, conn, params=(meal_id,))
                    
                    if not macros.empty:
                        df.at[idx, 'calories'] = macros.iloc[0]['calories']
                        df.at[idx, 'proteins'] = macros.iloc[0]['proteins']
                        df.at[idx, 'carbs'] = macros.iloc[0]['carbs']
                        df.at[idx, 'fats'] = macros.iloc[0]['fats']
        
        conn.close()
        return df

    def get_tracked_meals(self, date):
        """Get tracked meals for a specific date"""
        conn = self.get_connection()
        
        # Convert date to string in YYYY-MM-DD format
        if isinstance(date, pd.Timestamp):
            date = date.strftime('%Y-%m-%d')
        elif isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
        
        query = '''
            SELECT mt.*, m.name as meal_name, m.category, m.type
            FROM meal_tracking mt
            JOIN meals m ON mt.meal_id = m.id
            WHERE DATE(mt.date) = DATE(?)
        '''
        
        df = pd.read_sql_query(query, conn, params=[date])
        
        # Similar to get_program_meals, populate foods and macros
        if not df.empty:
            # Add 'foods' column first with default empty lists
            df['foods'] = [[] for _ in range(len(df))]

            # Handle regular meals
            regular_meals = df[df['type'] == 'regular']
            if not regular_meals.empty:
                for idx, row in regular_meals.iterrows():
                    meal_id = int(row['meal_id'])
                    
                    foods_query = '''
                        SELECT f.*, mf.quantity
                        FROM food_sources f
                        JOIN meal_foods mf ON f.id = mf.food_id
                        WHERE mf.meal_id = ?
                    '''
                    foods = pd.read_sql_query(foods_query, conn, params=(meal_id,))
                    
                    if not foods.empty:
                        df.at[idx, 'foods'] = foods.to_dict('records')
            
            # Handle custom meals
            custom_meals = df[df['type'] == 'custom']
            if not custom_meals.empty:
                for idx, row in custom_meals.iterrows():
                    meal_id = int(row['meal_id'])
                    
                    macros_query = '''
                        SELECT calories, proteins, carbs, fats
                        FROM meals
                        WHERE id = ?
                    '''
                    macros = pd.read_sql_query(macros_query, conn, params=(meal_id,))
                    
                    if not macros.empty:
                        df.at[idx, 'calories'] = macros.iloc[0]['calories']
                        df.at[idx, 'proteins'] = macros.iloc[0]['proteins']
                        df.at[idx, 'carbs'] = macros.iloc[0]['carbs']
                        df.at[idx, 'fats'] = macros.iloc[0]['fats']
        
        conn.close()
        return df
    
    def get_all_programs(self):
        """Get all meal programs"""
        conn = self.get_connection()
        query = 'SELECT * FROM meal_programs WHERE is_active = 1'
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def delete_program(self, program_id):
        """Delete a meal program and its meals"""
        # Ensure program_id is an integer
        program_id = int(program_id)
        
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            # Delete program meals first (foreign key constraint)
            c.execute('DELETE FROM program_meals WHERE program_id = ?', (program_id,))
            # Delete the program
            c.execute('DELETE FROM meal_programs WHERE id = ?', (program_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting program: {e}")
            return False
        finally:
            conn.close()

    def delete_program_meal(self, program_id, date, meal_time):
        """Delete a specific meal from a program"""
        # Ensure program_id is an integer
        program_id = int(program_id)
        
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                DELETE FROM program_meals 
                WHERE program_id = ? AND date = ? AND meal_time = ?
            ''', (program_id, date, meal_time))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting program meal: {e}")
            return False
        finally:
            conn.close()

    def get_program_meals(self, program_id):
        """Get all meals in a program with their details"""
        # Ensure program_id is an integer
        program_id = int(program_id)
        
        conn = self.get_connection()
        
        meal_time_order = '\n'.join(
            f"WHEN '{meal_time}' THEN {index + 1}" 
            for index, meal_time in enumerate(MealTime.as_list())
        )

        query = f'''
            SELECT pm.*, m.name as meal_name, m.category, m.type
            FROM program_meals pm
            JOIN meals m ON pm.meal_id = m.id
            WHERE pm.program_id = ?
            ORDER BY pm.date, 
            CASE pm.meal_time 
                {meal_time_order}
            END
        '''
        
        df = pd.read_sql_query(query, conn, params=[program_id])
        
        # Get the foods for regular meals and macros for custom meals
        if not df.empty:
            # Add 'foods' column first with default empty lists
            df['foods'] = [[] for _ in range(len(df))]
            
            # Handle regular meals
            regular_meals = df[df['type'] == 'regular']
            if not regular_meals.empty:
                for idx, row in regular_meals.iterrows():
                    meal_id = int(row['meal_id'])
                    
                    foods_query = '''
                        SELECT f.*, mf.quantity
                        FROM food_sources f
                        JOIN meal_foods mf ON f.id = mf.food_id
                        WHERE mf.meal_id = ?
                    '''
                    foods = pd.read_sql_query(foods_query, conn, params=(meal_id,))
                    
                    if not foods.empty:
                        df.at[idx, 'foods'] = foods.to_dict('records')
            
            # Handle custom meals
            custom_meals = df[df['type'] == 'custom']
            if not custom_meals.empty:
                for idx, row in custom_meals.iterrows():
                    meal_id = int(row['meal_id'])
                    
                    macros_query = '''
                        SELECT calories, proteins, carbs, fats
                        FROM meals
                        WHERE id = ?
                    '''
                    macros = pd.read_sql_query(macros_query, conn, params=(meal_id,))
                    
                    if not macros.empty:
                        df.at[idx, 'calories'] = macros.iloc[0]['calories']
                        df.at[idx, 'proteins'] = macros.iloc[0]['proteins']
                        df.at[idx, 'carbs'] = macros.iloc[0]['carbs']
                        df.at[idx, 'fats'] = macros.iloc[0]['fats']
        
        conn.close()
        return df
    
    def update_program_meal(self, program_id, meal_id, date, meal_time):
        """Update or create a program meal for a specific date and time"""
        # Ensure ids are integers
        program_id = int(program_id)
        meal_id = int(meal_id)
        
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            # Check if meal exists for this time slot
            c.execute('''
                SELECT id FROM program_meals 
                WHERE program_id = ? AND date = ? AND meal_time = ?
            ''', (program_id, date, meal_time))
            existing = c.fetchone()
            
            if existing:
                # Update existing meal
                c.execute('''
                    UPDATE program_meals 
                    SET meal_id = ?
                    WHERE program_id = ? AND date = ? AND meal_time = ?
                ''', (meal_id, program_id, date, meal_time))
            else:
                # Insert new meal
                c.execute('''
                    INSERT INTO program_meals (program_id, meal_id, date, meal_time)
                    VALUES (?, ?, ?, ?)
                ''', (program_id, meal_id, date, meal_time))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating program meal: {e}")
            return False
        finally:
            conn.close()