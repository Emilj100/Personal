import sys
import csv
import re
import requests
import json

# Dict til at have alle vores brugere.
users = {}

# Liste til at tjekke om brugeren indtaster et valid input ved linje 11 og 56
user_options = ["1", "2", "3", "4", "5"]

class User:
    def __init__(self, name, gender, height, age, weight, goal, training):
        self.name = name
        self.gender = gender
        self.height = height
        self.age = age
        self.weight = weight
        self.goal = goal
        self.training = training

    # Gemmer nye brugere til vores csv. Bliver brugt i create_user funktionen
    def save_to_csv(self):
        with open("data.csv", "a") as file:
            writer = csv.DictWriter(file, fieldnames=["name", "gender", "height", "age", "weight", "goal", "training"])
            writer.writerow({"name": self.name, "gender": self.gender, "height": self.height, "age": self.age, "weight": self.weight, "goal": self.goal, "training": self.training})

    # Når programmet starter bliver denne funktion kaldt. Den tager alle brugere fra CSV filen og indlæser dem i vores dict. Herefter kan vi tage den enkelte brugers objekt og gør brug af det hvis de allerede findes i programmet
    @staticmethod
    def get_all_users():
        with open("data.csv") as file:
            reader = csv.DictReader(file)
            for row in reader:
                users_name = row["name"]
                users[users_name] = User(row["name"], row["gender"], row["height"], row["age"], row["weight"], row["goal"], row["training"])

    # Viser brugerens data hvis de eksistere i programmet og ønsker at se det/ændre det
    def show_user_data(self):
        if self.goal == "1":
            goal = "Lose weight"
        elif self.goal == "2":
            goal = "Stay at my current weight"
        elif self.goal == "3":
            goal = "Gain weight"
        return f"Name: {self.name}\nGender: {self.gender}\nHeight: {self.height}\nAge: {self.age}\nWeight: {self.weight}\nGoal: {goal}\nTraining: Training {self.training} times per week"


    # Denne funktion tjekker om brugeren allerede eksistere i programmet. Vi bruger den i starten af vores main funktion
    @staticmethod
    def check_user(user_name):
        for _ in users:
            if user_name in users:
                return True
        return False

    # Regner brugerens kalorieindtag ud.
    def calorie_intake(self):
        if self.gender == "Male":
            bmr = (10 * float(self.weight)) + (6.25 * int(self.height)) - (5 * int(self.age)) + 5
        if self.gender == "Female":
            bmr = (10 * float(self.weight)) + (6.25 * int(self.height)) - (5 * int(self.age)) - 161

        if self.training == "1" or self.training == "2" or self.training == "3":
            training_days = 1.375
        elif self.training == "4" or self.training == "5":
            training_days = 1.55
        elif self.training == "6" or self.training == "7":
            training_days = 1.725

        calorie_intake = int(bmr) * training_days

        if self.goal == "1":
            calorie_intake = calorie_intake - 500
        elif self.goal == "3":
            calorie_intake = calorie_intake + 500
        print(f"\nThis is your calorie intake: {calorie_intake:.2f} calories\n")


    # Printer brugerens træningsprogram alt efter om de har indtastet 1, 2, 3 osv ved antal dage de ønsker at træne
    def __str__(self):
        with open(self.training_program) as file:
           file = file.read()
           return file
    # Arbejder sammen med __str__ over
    def give_training_program(self):
        if self.training == "1":
            training_program = "training_1.txt"
        elif self.training == "2":
            training_program = "training_2.txt"
        elif self.training == "3":
            training_program = "training_3.txt"
        elif self.training == "4":
            training_program = "training_4.txt"
        elif self.training == "5":
            training_program = "training_5.txt"
        elif self.training == "6":
            training_program = "training_6.txt"
        elif self.training == "7":
            training_program = "training_7.txt"
        self.training_program = training_program


def main():
    # Indlæser alle brugere fra CSV filen til vores dict så vi kan gøre brug af en eksisterende brugers objekt hvis der skulle komme behov for det.
    User.get_all_users()
    # Spørger om brugerens navn og gør brug af regular expression for at sikre at det er et valid navn
    while True:
        user_name = input("What's your name? ")
        if user_name := re.fullmatch(r"[a-z]+", user_name, re.IGNORECASE):
            user_name = user_name.group().title()
            break
        else:
            print("Invalid input: Please enter a valid name")
            continue
    # Tjekker om det indtastede navn allerede eksistere i systemet
    if User.check_user(user_name):
        # Giv brugeren de muligheder programmet har
        user_program_options(user_name)


    else:
        # Få data på brugeren og gem det i en CSV fil
        print(f"Welcome {user_name}! First we need some data to get the right program for you.")

        # Beder brugeren om at indtaste sit køn. Her sikre vi os via regular expression at de enten skriver male eller female.
        while True:
            gender = input("Male/Female: ").lower()
            if gender := re.fullmatch(r"male|female", gender, re.IGNORECASE):
                gender = gender.group().title()
                break
            else:
                print('Invalid input: Please enter "Male" or "Female"')
                continue
        # Funktion der opretter en ny bruger, hvis de ikke findes i systemet
        name, height, age, weight, goal, training = create_user(user_name)
        #opretter brugeren som et objekt at vores class User og derefter bruger save_to_csv funktionen, som der gemmer brugeren i CSV filen
        user = User(name, gender, height, age, weight, goal, training)
        user.save_to_csv()

        #Gemmer brugerens objekt/informationer i vores dict der hedder users
        users[user_name] = user

        print("Great! Here is your calorie intake and training program")

        # Viser brugerens kalorieindtag udfra de oplysninger brugeren har givet
        user.calorie_intake()

        # Viser brugerens træningsprogram udfra det antal dage brugeren har sagt de ønsker at træne
        user.give_training_program()
        print(user)

        # Viser brugeren de forskellige muligheder de har når de har fået oprettet en bruger
        user_program_options(user_name)

# Giver brugeren de muligheder de har når de har oprettet en bruger
def user_program_options(user_name):
    while True:

        # Tager brugerens objekt fra vores dict og gemmer det i variablen current_user
        current_user = users[user_name]

        user_input = input("\nWhat would you like to do\n 1. Track calories\n 2. See my trainingprogram and calorie intake\n 3. Update my data\n 4. Change my trainingprogram\n 5. Exit\n (Enter: 1,2,3,4 or 5)\n")

        # Starter vores kalorie tracker program og gør det muligt for brugeren at indtaste hvad de har spist i løbet af dagen
        if user_input == "1":
            #Viser brugeren hvad deres kalorieindtag er
            current_user.calorie_intake()
            # Starter kalorietracker programmet
            calorie_tracker()

        # Viser brugerens træningsprogram og kalorieindtag
        elif user_input == "2":
            # Tjekker hvad brugernes kalorieindtag er udfra brugerens oplysninger
            current_user.calorie_intake()

            # Tjekker brugerens træningsprogrammer udfra brugerens oplysninger og derefter printer programmet
            current_user.give_training_program()
            print(current_user)

        # Gør det muligt for brugeren at indtaste nye data
        elif user_input == "3":
            # Viser brugerens nuværende data
            print("This is your current data:\n")
            print(current_user.show_user_data())
            # Gør det muligt for brugeren at indtaste ny data
            print("\nPlease enter your new data:\n")
            name, height, age, weight, goal, training = create_user(user_name)
            print("\nYour data have now been updated")
            # Denne del sørger for at opdatere brugerens oplysninger i vores dict, da "current_user" netop gemmer på "users[user_name]". Så vi opdatere derfor både brugerens oplysninger i objektet gemt i dicten men også selve attributerne.
            current_user.height = height
            current_user.age = age
            current_user.weight = weight
            current_user.goal = goal
            current_user.training = training
            # Herefter opretter vi data.csv på ny og indtaster alle vores brugeres oplysninger igen samt den nuværendes bruger nye oplysninger ####sikre at det bliver opdateret i dict
            with open("data.csv", "w") as file:
                writer = csv.DictWriter(file, fieldnames=["name", "gender", "height", "age", "weight", "goal", "training"])
                writer.writeheader()
                for user in users:
                    writer.writerow({"name": users[user].name, "gender": users[user].gender, "height": users[user].height, "age": users[user].age, "weight": users[user].weight, "goal": users[user].goal, "training": users[user].training})



        # Gør det muligt for brugeren at indtaste hvor mange gange de ønsker at træne om ugen
        elif user_input == "4":
            # Viser brugeren hvor mange gange de træner om ugen lige nu
            print(f"\nYou currently train {current_user.training} times per week.\n")
            # Spørger brugeren hvor mange gange de ønsker at træne om ugen nu og sikre at brugeren skriver et valid input
            while True:
                training = input("How many days would you like to train per week?\n (Enter 1,2,3,4,5,6 or 7)\n")
                if training := re.fullmatch(r"1|2|3|4|5|6|7", training):
                    training = training.group()
                    break
                else:
                    print("Invalid input: Please enter 1, 2, 3, 4, 5, 6 or 7")
                    continue
            # Opdatere brugerens valg af antal dage at træne både i vores dict og CSV fil
            current_user.training = training
            with open("data.csv", "w") as file:
                writer = csv.DictWriter(file, fieldnames=["name", "gender", "height", "age", "weight", "goal", "training"])
                writer.writeheader()
                for user in users:
                    writer.writerow({"name": users[user].name, "gender": users[user].gender, "height": users[user].height, "age": users[user].age, "weight": users[user].weight, "goal": users[user].goal, "training": users[user].training})
            # Viser brugeren sit nye træningsprogram
            current_user.give_training_program()
            print(current_user)

        # Stopper programmet
        elif user_input == "5":
            # Exit programmet
            sys.exit("Program ended")

        # Sikre at brugeren indtaster et valid input når de skal fortælle hvilken funktion fra programmet som de ønsker at gøre brug af.
        if not user_input in user_options:
            print("Please enter 1,2,3,4 or 5")


# Funktionen der indsamler en ny brugers oplysninger og sikre at oplysningerne er korrekte
def create_user(user_name):
        name = user_name

        # Ved alle disse while True loops beder vi brugeren om inputs og tjekker efter fejl i brugerens input. Vi beder brugeren om at indtaste et input indtil de skriver et valid input.
        while True:
            height = input("Height: ")
            if height := re.fullmatch(r"([0-9]{3})( )?(cm)?", height, re.IGNORECASE):
                height = height.group(1)
                break
            else:
                print("Invalid input: Please enter a valid height")
                continue

        while True:
            age = input("Age: ")
            if age := re.fullmatch(r"([0-9]{1,2})(years old)?", age, re.IGNORECASE):
                age = age.group(1)
                break
            else:
                print("Invalid input: Please enter a valid age")
                continue

        while True:
            weight = input("Weight: ")
            if weight := re.fullmatch(r"([0-9,.]{2,5})( )?(kg|kilo)?", weight, re.IGNORECASE):
                weight = weight.group(1)
                weight = weight.replace(",", ".")
                break
            else:
                print("Invalid input: Please enter a valid weight")
                continue

        print(f"\nNice {name}! Let us know a bit more about your goals and how many days you want to train per week.\n")

        while True:
            goal = input("What is your goal?\n 1. Lose weight\n 2. Stay at my current weight\n 3. Gain weight\n (Enter 1,2 or 3)\n")
            if goal := re.fullmatch(r"1|2|3", goal):
                goal = goal.group()
                break
            else:
                print("Invalid input: Please enter 1, 2 or 3")
                continue

        while True:
            training = input("How many days would you like to train per week?\n (Enter 1,2,3,4,5,6 or 7)\n")
            if training := re.fullmatch(r"1|2|3|4|5|6|7", training):
                training = training.group()
                break
            else:
                print("Invalid input: Please enter 1, 2, 3, 4, 5, 6 or 7")
                continue

        return name, height, age, weight, goal, training



# Gør det muligt for brugeren at indtaste hvad de har spist og derefter får antal kalorier osv de har spist
def calorie_tracker():

    # Vores API, som der gør det hele muligt
    try:
        # Spørger brugeren om hvad de har spist i dag, som vi så indsætter i vores API
        food_query = input("What did you eat today? ")


        API_KEY = "6158963245cf646896228de0c3d0ba3a"
        APP_ID = "584633a6"


        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"


        headers = {
            "x-app-id": APP_ID,
            "x-app-key": API_KEY,
            "Content-Type": "application/json"
        }

        # Data, der skal sendes i anmodningen - den tekstbaserede forespørgsel
        data = {
            "query": food_query
        }

        # Send POST-forespørgsel til Nutritionix API
        response = requests.post(url, headers=headers, json=data)

        # Ændre svaret til JSON-format
        nutrition_data = response.json()

        # Viser brugeren tallene for det som brugeren har indtastet
        print("Here is the data for the food you have been eating today:\n")

        all_calories = []
        all_protein = []
        all_carbohydrate = []
        all_fat = []

        for food in nutrition_data["foods"]:
            all_calories.append(food["nf_calories"])
            all_protein.append(food["nf_protein"])
            all_carbohydrate.append(food["nf_total_carbohydrate"])
            all_fat.append(food["nf_total_fat"])


        print(f"{sum(all_calories):.2f} calories")
        print(f"{sum(all_protein):.2f} protein")
        print(f"{sum(all_carbohydrate):.2f} carbohydrate")
        print(f"{sum(all_fat):.2f} fat")

    # Tjekke om vi kan få det til at køre i loop indtil den gør det korrekt
    except KeyError:
        print('Error: Please make sure that your input doesnt have any spelling mistake. Please enter "1" and try again.')

if __name__ == "__main__":
    main()
