import sqlite3
from datetime import datetime

class RecipeManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS recipes
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                ingredients TEXT,
                                instructions TEXT,
                                rating INTEGER,
                                date_added TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE)''')
        self.conn.commit()

    def add_recipe(self, name, ingredients, instructions, rating=0):
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''INSERT INTO recipes (name, ingredients, instructions, rating, date_added)
                               VALUES (?, ?, ?, ?, ?)''', (name, ingredients, instructions, rating, date_added))
        self.conn.commit()

    def add_category(self, name):
        try:
            self.cursor.execute('''INSERT INTO categories (name) VALUES (?)''', (name,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Category name already exists

    def rate_recipe(self, recipe_id, rating):
        self.cursor.execute('''UPDATE recipes SET rating = ? WHERE id = ?''', (rating, recipe_id))
        self.conn.commit()

    def get_all_categories(self):
        self.cursor.execute('''SELECT * FROM categories''')
        categories = self.cursor.fetchall()
        return categories

    def search_recipes(self, query):
        self.cursor.execute('''SELECT * FROM recipes
                               WHERE name LIKE ? OR ingredients LIKE ? OR instructions LIKE ?''',
                            ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
        recipes = self.cursor.fetchall()
        return recipes

    def view_recipe(self, recipe_id):
        self.cursor.execute('''SELECT * FROM recipes WHERE id = ?''', (recipe_id,))
        recipe = self.cursor.fetchone()
        return recipe

class UserPreferences:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS preferences
                               (id INTEGER PRIMARY KEY,
                                favorite_category TEXT,
                                max_rating INTEGER)''')
        self.conn.commit()

    def set_favorite_category(self, category):
        self.cursor.execute('''INSERT OR REPLACE INTO preferences (id, favorite_category) VALUES (1, ?)''', (category,))
        self.conn.commit()

    def set_max_rating(self, max_rating):
        self.cursor.execute('''INSERT OR REPLACE INTO preferences (id, max_rating) VALUES (1, ?)''', (max_rating,))
        self.conn.commit()

    def get_favorite_category(self):
        self.cursor.execute('''SELECT favorite_category FROM preferences WHERE id = 1''')
        favorite_category = self.cursor.fetchone()
        return favorite_category[0] if favorite_category else None

    def get_max_rating(self):
        self.cursor.execute('''SELECT max_rating FROM preferences WHERE id = 1''')
        max_rating = self.cursor.fetchone()
        return max_rating[0] if max_rating else None

def main():
    recipe_manager = RecipeManager('recipes.db')
    user_preferences = UserPreferences('preferences.db')

    while True:
        print("\nRecipe Manager Menu:")
        print("1. Add Recipe")
        print("2. Rate Recipe")
        print("3. Search Recipes")
        print("4. View Recipe")
        print("5. Set Favorite Category")
        print("6. Set Max Rating")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter recipe name: ")
            ingredients = input("Enter ingredients (comma-separated): ").split(',')
            instructions = input("Enter instructions: ")
            recipe_manager.add_recipe(name, ','.join(ingredients), instructions)
            print("Recipe added successfully!")

        elif choice == "2":
            recipe_id = input("Enter recipe ID: ")
            rating = int(input("Enter rating (1-5): "))
            recipe_manager.rate_recipe(recipe_id, rating)
            print("Recipe rated successfully!")

        elif choice == "3":
            query = input("Enter search query: ")
            recipes = recipe_manager.search_recipes(query)
            if recipes:
                print("Search results:")
                for recipe in recipes:
                    print(f"ID: {recipe[0]}, Name: {recipe[1]}")
            else:
                print("No recipes found.")

        elif choice == "4":
            recipe_id = input("Enter recipe ID: ")
            recipe = recipe_manager.view_recipe(recipe_id)
            if recipe:
                print("Recipe details:")
                print(f"Name: {recipe[1]}")
                print(f"Ingredients: {recipe[2]}")
                print(f"Instructions: {recipe[3]}")
                print(f"Rating: {recipe[4]}")
            else:
                print("Recipe not found.")

        elif choice == "5":
            category = input("Enter favorite category: ")
            success = recipe_manager.add_category(category)
            if success:
                user_preferences.set_favorite_category(category)
                print("Favorite category set successfully!")
            else:
                print("Category already exists.")

        elif choice == "6":
            max_rating = int(input("Enter max rating (1-5): "))
            user_preferences.set_max_rating(max_rating)
            print("Max rating set successfully!")

        elif choice == "7":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

    recipe_manager.conn.close()
    user_preferences.conn.close()

if __name__ == "__main__":
    main()
