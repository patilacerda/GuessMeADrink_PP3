import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random
from colorama import Fore, Back, Style
import os
import sys

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('cocktail_recipes')
RECIPES = SHEET.worksheet('recipes')
recipe_list = RECIPES.get_all_records()

menu_art = '\033[36m' + """

                    ████████████████████████████████████
                    ██░░░░░░██░░░░░░░░░░░░░░░░░░░░░░░░██
                      ██      ██                    ██
                        ██      ██                ██
                          ██      ░░░░          ██
                            ██    ░░██        ██
Welcome to                    ██      ██    ██
                                ██        ██
                                  ██    ██
         Guess me a drink           ████
                                    ████
                                    ████
                                    ████
                                    ████
                                    ████
                                    ████
                                  ████████
                                ████████████
                            ▓▓▓▓████████████▓▓██
""" + '\033[39m'


def calculate_age(birth_date):
    # Calculate the age based on the birth date.
    today = datetime.today()
    age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def select_random_cocktail():
    # Randomly select a row and column (cocktail) from recipe_list
    random_row = random.randint(2, len(recipe_list))
    random_column = random.randint(2, len(spirit_categories))
    cocktail = RECIPES.cell(random_row, random_column).value
    return cocktail


def user_continue():
    while True:
        user_flavor_choice = input('\033[33m' + """
                Do you want to try another cocktail? (y/n):\n
        """ + '\033[39m').strip()
        if user_flavor_choice == "n":
            print('\033[36m' + """
                    Thanks for using Guess me a drink!
                        Enjoy your drinks wisely,
                    and don't forget to stay hydrated:)
            """ + '\033[39m')
            sys.exit()

        elif user_flavor_choice == "y":
            return True
        else:
            print('\033[31m' + """
                Invalid input. Please enter 'y' or 'n'.
            """ + '\033[39m')


print(menu_art)

# Wait for the user to press Enter
input("Press Enter to start...")

# Clear the terminal
os.system("clear" if os.name == "posix" else "cls")

# Verify the age of the user
while True:
    user_age_str = input("Please enter your date of birth (dd/mm/yyyy): \n")
    try:
        user_age_date = datetime.strptime(user_age_str, "%d/%m/%Y")
        user_age = calculate_age(user_age_date)
        break
    except ValueError:
        print('\033[31m' + """
            Invalid date format. Please use the format dd/mm/yyyy.
        """ + '\033[39m')

if user_age < 18:
    underage = 18 - user_age
    print(f"""
                For now, you can have a soda.""" + '\033[36m' + """

                                       ██
                                     ██  ██
                          ░░░░░░░░ ██
                       ░░░░░░░░░░██░░
                    █████████████████████
                    ███               ███
                       ███████████████
                       ███         ███
                       ███         ███
                       ███ U  w  U ███
                       ███ ░░   ░░ ███
                       ███         ███
                       █████░░░░░█████
                         ███████████""" + '\033[39m' + f"""

            Come back in {underage} years and try again!""")
else:
    print("Let's get started!")
    # Get the spirit category from the first row of the sheet
    spirit_categories = SHEET.sheet1.row_values(1)[1:]

    # Add "Random" as an option to select a random drink
    spirit_categories.append("I'm feeling lucky")

    while True:
        print('\033[33m' + "Choose a spirit category: " + '\033[39m')
        for i, category in enumerate(spirit_categories, start=1):
            # Main menu
            print(f"{i}. {category}")

        try:
            user_choice = int(input(
                "Enter the number of your chosen spirit category: \n"))
            if 1 <= user_choice <= len(spirit_categories):
                selected_category = spirit_categories[user_choice - 1]

                if selected_category == "I'm feeling lucky":
                    # Select a random cocktail
                    random_cocktail = select_random_cocktail()
                    print(f"Here's your lucky cocktail: {random_cocktail}")
                    if not user_continue():
                        break

                else:
                    # Get the available flavors
                    spirit_row = RECIPES.row_values(1)
                    spirit_index = spirit_row.index(selected_category)
                    flavors = RECIPES.col_values(1)
                    flavors = flavors[1:]  # Skip the header
                    return_to_menu = False

                    while not return_to_menu:
                        # Show the flavor options to the user
                        print('\033[33m' + "Choose a flavor:" + '\033[39m')
                        for i, flavor in enumerate(flavors, start=1):
                            print(f"{i}. {flavor}")
                        try:
                            user_flavor_choice = int(input(
                                "Enter the number of your chosen flavor: \n"))
                            if 1 <= user_flavor_choice <= len(flavors):
                                selected_flavor = flavors[
                                    user_flavor_choice - 1]

                                # Find the row index of the selected spirit
                                spirit_index = spirit_categories.index(
                                    selected_category)

                                # Return the recipe
                                recipe = RECIPES.cell(
                                    user_flavor_choice + 1,
                                    spirit_index + 2).value

                                print("You selected: " + '\033[33m' + f"""
                                {selected_category} - {selected_flavor}
                                """)
                                print('\033[39m')
                                print(f"Here's your recipe:\n{recipe}")
                                if not user_continue():
                                    break  # Exit the flavor selection loop
                                else:
                                    return_to_menu = True
                            else:
                                print('\033[31m' + """
                    Invalid selection. Please choose a valid flavor.
                                """ + '\033[39m')
                        except ValueError:
                            print('\033[31m' + """
                        Invalid input. Please enter a valid number.
                            """ + '\033[39m')
            else:
                print('\033[31m' + """
                Invalid selection. Please choose a valid spirit category.
                """ + '\033[39m')
        except ValueError:
            print('\033[31m' + """
                        Invalid input. Please enter a valid number.
            """ + '\033[39m')
