import sys
import csv
import re
import requests
from typing import Dict

# Globale variabler
users: Dict[str, 'User'] = {}

class User:
    def __init__(self, name, gender, height, age, weight, goal, training):
        self.name = name
        self.gender = gender
        self.height = height
        self.age = age
        self.weight = weight
        self.goal = goal
        self.training = training

    def save_to_csv(self):
        """Gemmer brugeren til CSV-filen."""
        with open("data.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["name", "gender", "height", "age", "weight", "goal", "training"])
            writer.writerow(self.to_dict())

    def to_dict(self):
        """Returnerer brugerens data som en ordbog."""
        return {
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "age": self.age,
            "weight": self.weight,
            "goal": self.goal,
            "training": self.training
        }

    @staticmethod
    def load_users():
        """Indlæser alle brugere fra CSV-filen."""
        try:
            with open("data.csv", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    users[row["name"]] = User(**row)
        except FileNotFoundError:
            print("Ingen brugerdata fundet.")

    def calculate_calories(self):
        """Beregner og returnerer brugerens daglige kaloriebehov baseret på deres data."""
        bmr = (10 * float(self.weight)) + (6.25 * int(self.height)) - (5 * int(self.age))
        bmr += 5 if self.gender == "Male" else -161

        activity_factor = {
            "1": 1.375, "2": 1.375, "3": 1.375,
            "4": 1.55, "5": 1.55,
            "6": 1.725, "7": 1.725
        }.get(self.training, 1.375)

        calorie_needs = bmr * activity_factor
        calorie_needs += 500 if self.goal == "3" else -500 if self.goal == "1" else 0

        return f"\nThis is your calorie intake: {calorie_needs:.2f} calories\n"

    def give_training_program(self):
        """Vælger og returnerer træningsprogram baseret på antal dage."""
        try:
            training_file = f"training_{self.training}.txt"
            with open(training_file) as file:
                return file.read()
        except FileNotFoundError:
            return "Træningsprogram ikke fundet."

def create_user(name):
    """Opretter en ny bruger med indtastede data og gemmer dem."""
    gender = input_valid("Male/Female: ", r"(male|female)", lambda x: x.title())
    height = input_valid("Height (in cm): ", r"\d{2,3}")
    age = input_valid("Age: ", r"\d{1,2}")
    weight = input_valid("Weight (in kg): ", r"\d{1,3}(\.\d{1,2})?", lambda x: x.replace(",", "."))
    goal = input_valid("Goal (1=Lose, 2=Maintain, 3=Gain): ", r"[1-3]")
    training = input_valid("Training days per week (1-7): ", r"[1-7]")

    user = User(name, gender, height, age, weight, goal, training)
    user.save_to_csv()
    users[name] = user
    return user

def input_valid(prompt, pattern, transform=lambda x: x):
    """Validér brugerinput baseret på et regulært udtryk."""
    while True:
        response = input(prompt).strip()
        match = re.fullmatch(pattern, response, re.IGNORECASE)
        if match:
            return transform(match.group())
        print("Invalid input, try again.")

def show_main_menu(user):
    """Vis hovedmenuen for brugeren og håndter valgmuligheder."""
    while True:
        print("\nOptions:\n1. Track calories\n2. View program & calorie intake\n3. Update data\n4. Change program\n5. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            print(user.calculate_calories())
            track_calories()
        elif choice == "2":
            print(user.calculate_calories())
            print(user.give_training_program())
        elif choice == "3":
            update_user_data(user)
        elif choice == "4":
            user.training = input_valid("New training days per week (1-7): ", r"[1-7]")
            update_csv()
            print(user.give_training_program())
        elif choice == "5":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice, try again.")

def update_user_data(user):
    """Opdaterer og gemmer brugerens data i CSV-filen."""
    user.height = input_valid("New height: ", r"\d{2,3}")
    user.age = input_valid("New age: ", r"\d{1,2}")
    user.weight = input_valid("New weight: ", r"\d{1,3}(\.\d{1,2})?", lambda x: x.replace(",", "."))
    user.goal = input_valid("New goal (1=Lose, 2=Maintain, 3=Gain): ", r"[1-3]")
    user.training = input_valid("New training days per week (1-7): ", r"[1-7]")
    update_csv()

def update_csv():
    """Opdaterer CSV-filen med alle brugernes data."""
    with open("data.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "gender", "height", "age", "weight", "goal", "training"])
        writer.writeheader()
        for user in users.values():
            writer.writerow(user.to_dict())

def track_calories():
    """Kalorietracker, der integrerer med en API."""
    food_item = input("What did you eat today? ")
    API_KEY = "6158963245cf646896228de0c3d0ba3a"
    APP_ID = "584633a6"
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {"x-app-id": APP_ID, "x-app-key": API_KEY, "Content-Type": "application/json"}
    data = {"query": food_item}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        nutrition_data = response.json()

        calories = sum(food["nf_calories"] for food in nutrition_data["foods"])
        protein = sum(food["nf_protein"] for food in nutrition_data["foods"])
        carbs = sum(food["nf_total_carbohydrate"] for food in nutrition_data["foods"])
        fat = sum(food["nf_total_fat"] for food in nutrition_data["foods"])

        print(f"\nCalories: {calories:.2f}\nProtein: {protein:.2f}\nCarbs: {carbs:.2f}\nFat: {fat:.2f}")
    except (requests.RequestException, KeyError):
        print("Could not retrieve data, please check your input.")

def main():
    User.load_users()
    user_name = input_valid("What's your name? ", r"[a-zA-Z]+", lambda x: x.title())
    user = users.get(user_name) or create_user(user_name)
    print("\nGreat! Here is your calorie intake and training program")
    print(user.calculate_calories())
    print(user.give_training_program())
    show_main_menu(user)

if __name__ == "__main__":
    main()
