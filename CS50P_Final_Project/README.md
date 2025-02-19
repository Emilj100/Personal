    # Fitness program
    #### Video Demo:  https://www.loom.com/share/2e8005e08773490894e1941c93b7504a?sid=da792f17-e025-45fe-b12c-8fa890e9199c
    #### Description:

    What can the program do?
    My program can help the user to get a custom training program based on how many days the user want to train per week. It can also calculate how many calories the user should eat per day based on the users goal and information.
    The program can also help the user track how many calories he/she has ben eating per day. Lets say the user has been eating 1 banana and 250 gram of chicken today. Then he can input this in the program and the program will tell the user how many calories, protein, carbohydrate and fat he/she has been eating today based on the users input. It is also possible for the user to change his/hers data, goals and traning program.

    My thoughts:
    When I started building this program I had 3 things I wanted to include in the program which is OOP, CSV/data and API. I wanted to include this since I believe it is very important to understand and very useful. I have never tried to code before and this is my first project and im proud of the result! CS50 python is also the first course that I have taken within coding.
    I listened to David's advice that you should build something which is interesting for you. I really like health and fitness, so I thought this would be a great idea.

    project.py
    This file includes all of the program functions.

    data.CSV:
    This file includes all of the users information

    training_1-7.txt:
    These files includes the training program for training 1 day per week up to 7 days per week.

    The programs structure:
    The program has 1 class, 1 main function and 3 other functions.
    Let me first explain how the class works:

    def __init__ which have all our attributes. For each object/user we want these informations: name, gender, height, age, weight, goal(If they want to lose weight or another goal), training(How many days they want to train per week)

    def save_to_csv which saves the users information to a CSV file

    def get_all_users which takes all of the users from the CSV file when the program starts and put them into a dict as a object

    def show_user_data which shows the users data if they want to see it/change it

    def check_user which check if the user is already exsisting in the program

    def calorie_intake which calculates the users calorie_intake based on the users information

    def __str__ and give_training_program which prints a training program based on how many times the user wants to train per week

    That was all our functions in the class. Lets move on to the main funktion.
    The main functions begins with get_all_users. This loads all the users from the CSV file to a dict, so we can use the users object later if we need it. After this we ask the user about his/hers name. Here we use regular expression to make sure that the user inputs a valid name. Afterwards we check if the user already exist in our dict. If the user exist we call the user_program_options function which shows the user the different things the program can do. If the program doesnt recognize the users name it will start to create an account for the user. We begin with asking the user about their gender. Afterwards we call our create_user function. Here we get the users information and make sure that the user inputs valid information with reagular expression. I have chosen to not implement the gender information in the create_user functions since i want to be able to use the function again if the user wants the update his/hers data. I do not think the user should be able to update their gender since they will always be either a male or female. After that we create and object of the user and saves the users information to our csv. We also save the users object to our dict of users objects. After that we show the user his/hers calorie_intake and training program based on the information the user have given us. Now when the user have an account we give the user the program options.

    Now we have our user_program_options. This function will run when the user have an account in the system. To begin with we take the users object from the dict and save it in current_user. This means we now has the users object and can use his/hers information. The user get 5 options. He she can either 1. Track calories 2. See my trainingprogram and calorie intake 3. Update my data 4. Change my trainingprogram 5. Exit. If the user inputs "1" then the program will start our track calories system and let the user track how many calories he/she has been eating today based on the food they have been eating. If the user inputs "2" then the program will show the users calorie intake and training program. If the user inputs "3" then the user will see their current data but also be able to update their data. We save the users new data in our dict but also the CSV file. If the user inputs "4" the program will show the user how many times they currently train per week but also gives them the options to change how many times they train per week. If the user inputs "5" the program will exit with "sys.exit". We also make sure that the user either enter 1,2,3,4 or 5.

    The next function is our create_user function. This functions get the users data and make sure that the user input valid information. So lets take the users height as an example. Here vi use regular expression to make sure that the user input a valid height. The user is allowed to enter 3 numbers and if he/she want they can write "cm" afterwards. A user input could be "180 cm". We then use regular expressions for all the other informations aswell but with different criteria.

    The last function we have is our calorie_tracker function. This function uses an API which is called NutritionIX API. This API has alot of data about food. So we use this API to check how many calories, protein, carbohydrate and fat that there is in the food the user has been eating. We can get alot of information about the food from the API but i have chosen to only use the information about calories, protein, carbohydrate and fat. The API is a bit sensitive tho. Therefore i have maken sure that if the user gets and error the program will give the user this error message: Please make sure that your input doesnt have any spelling mistake. Please enter "1" and try again.




