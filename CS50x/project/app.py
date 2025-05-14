import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import re
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_wtf import CSRFProtect

# Load environment variables from the "private.env" file
load_dotenv("private.env")


# Retrieve API keys from environment variables
spoonacular_api_key = os.environ.get("SPOONACULAR_API_KEY")
nutritionix_api_key = os.environ.get("NUTRITIONIX_API_KEY")
nutritionix_api_id  = os.environ.get("NUTRITIONIX_API_ID")
openai_api_key      = os.environ.get("OPENAI_API_KEY")

# Initialize the Flask application
app = Flask(__name__)

# Set the secret key used for securely signing session cookies and CSRF tokens.
# This should be a strong, randomly generated string and is loaded from the environment.
app.secret_key = os.environ.get("SECRET_KEY")

# Configure session settings:
# - Sessions are not permanent (they expire when the browser is closed)
# - Sessions are stored in the filesystem (useful for development or small deployments)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Enhance cookie security:
# - SESSION_COOKIE_SECURE: Ensures cookies are only sent over HTTPS.
# - SESSION_COOKIE_HTTPONLY: Prevents JavaScript from accessing the cookies.
# - SESSION_COOKIE_SAMESITE: Helps protect against CSRF attacks by controlling how cookies are sent with cross-site requests.
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Initialize server-side session management and CSRF protection.
Session(app)
csrf = CSRFProtect(app)

# Initialize the database connection using an SQLite database.
db = SQL("sqlite:///health.db")


def login_required(f):
    """
    Decorator to require user login for protected routes.
    If the user is not logged in (i.e., "user_id" is not in session),
    they are redirected to the login page.
    Reference: https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if "user_id" exists in the session; if not, redirect to login page
        if session.get("user_id") is None:
            return redirect("/login")
        # Otherwise, execute the original route function
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Set response headers to disable caching, ensuring users always get fresh content."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")
def index():
    # Render the homepage template when the root URL is accessed
    return render_template("index.html")


@app.route("/register-part1", methods=["GET", "POST"])
def registerpart1():
    # If the form is submitted via POST, process the registration data
    if request.method == "POST":
        # Get the email input from the form
        email = request.form.get("email")

        # Validate form fields and return the form with an error message if any check fails
        if not request.form.get("name"):
            # Name field must not be empty
            return render_template("register-part1.html", error="Must provide Name")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            # Email must match a simple regex pattern to be considered valid
            return render_template("register-part1.html", error="Must provide valid email")
        elif not request.form.get("password") or not len(request.form.get("password")) >= 8:
            # Password must be provided and be at least 8 characters long
            return render_template("register-part1.html", error="Password must be at least 8 characters long")
        elif request.form.get("password") != request.form.get("confirm_password"):
            # Confirm that the password and its confirmation match
            return render_template("register-part1.html", error="Passwords must match")

        # Store the user's name, email, and hashed password in the session for use in later registration steps
        session["name"] = request.form.get("name")
        session["email"] = request.form.get("email")
        session["password"] = generate_password_hash(request.form.get("password"))

        # Redirect the user to the next registration step
        return redirect("/register-part2")

    # For GET requests, simply render the registration form template
    return render_template("register-part1.html")



@app.route("/register-part2", methods=["GET", "POST"])
def registerpart2():
    if request.method == "POST":
        # Try to convert the 'age' input to an integer
        try:
            age = int(request.form.get("age"))
        except ValueError:
            return render_template("register-part2.html", error="Please enter a valid number for age.")

        # Validate that the gender input is either "Male" or "Female"
        if not request.form.get("gender") in ["Male", "Female"]:
            return render_template("register-part2.html", error="Please select a valid gender")

        # Try to convert 'height', 'weight', and 'goal_weight' to floats
        try:
            height = float(request.form.get("height"))
            weight = float(request.form.get("weight"))
            goal_weight = float(request.form.get("goal_weight"))
        except ValueError:
            return render_template("register-part2.html", error="Height, weight, and goal weight must be numbers")

        # Ensure the goal type is valid
        if not request.form.get("goal_type") in ["lose weight", "gain weight", "stay at current weight"]:
            return render_template("register-part2.html", error="Please select a valid goal")

        # Validate the experience level
        if not request.form.get("experience_level") in ["Beginner", "Intermediate", "Advanced"]:
            return render_template("register-part2.html", error="Please select a valid experience level")

        # Validate that training days is an integer between 1 and 7
        try:
            training_days = int(request.form.get("training_days"))
            if not (1 <= training_days <= 7):
                return render_template("register-part2.html", error="Training days must be between 1 and 7.")
        except ValueError:
            return render_template("register-part2.html", error="Training days must be a number")

        # Calculate the Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation
        if request.form.get("gender") == "Male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # Adjust calorie intake based on the number of training days
        if (1 <= training_days <= 3):
            calorie_intake = bmr * 1.375
        elif (4 <= training_days <= 5):
            calorie_intake = bmr * 1.55
        else:
            calorie_intake = bmr * 1.725

        # Further adjust calorie intake based on the user's goal type
        if request.form.get("goal_type") == "lose weight":
            calorie_intake = round(calorie_intake - 500)
        elif request.form.get("goal_type") == "gain weight":
            calorie_intake = round(calorie_intake + 500)

        # Insert the new user into the database with all registration details
        try:
            user_id = db.execute(
                """
                INSERT INTO users (name, email, password, age, gender, height, weight, start_weight, goal_weight, goal_type, training_days, experience_level, daily_calorie_goal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                session["name"].title(), session["email"], session["password"], age,
                request.form.get("gender"), height, weight, weight, goal_weight,
                request.form.get("goal_type"), training_days, request.form.get("experience_level"), calorie_intake
            )
            # Store the new user's ID in the session
            session["user_id"] = user_id

        except ValueError:
            # If an error occurs (e.g., duplicate email), redirect back to registration part1 with an error
            return render_template("register-part1.html", error="Email already exist")

        # Remove temporary registration data from the session
        session.pop("name", None)
        session.pop("email", None)
        session.pop("password", None)

        # Redirect to the homepage after successful registration
        return redirect("/")

    # For GET requests, simply render the registration page for part 2
    return render_template("register-part2.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear any existing session data on login attempt
    session.clear()

    if request.method == "POST":
        # Retrieve email and password from the login form
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate that both email and password were provided
        if not email:
            return render_template("login.html", error="Must provide email")
        elif not password:
            return render_template("login.html", error="Must provide password")

        # Query the database for a user with the provided email
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)

        # Check if exactly one user was found and verify the password hash
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return render_template("login.html", error="Invalid username and/or password")

        # Store the user's ID in the session to mark them as logged in
        session["user_id"] = rows[0]["id"]

        # Redirect the user to the homepage upon successful login
        return redirect("/")

    else:
        # For GET requests, simply render the login page with no error message
        return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    # Clear the session to log the user out
    session.clear()
    # Redirect to the homepage after logout
    return redirect("/")


@app.route("/calorietracker", methods=["GET", "POST"])
@login_required
def calorietracker():
    # Retrieve the current user's ID from the session
    user_id = session["user_id"]

    # Fetch the food log for the current day from the database
    food_log = db.execute(
        """
        SELECT id, food_name, serving_qty, serving_unit, calories, proteins, carbohydrates, fats
        FROM food_log
        WHERE user_id = ? AND DATE(created_at) = DATE('now')
        """,
        user_id
    )

    # Define a helper function to retrieve macro nutrient totals for the current day
    def get_macros():
        return db.execute(
            """
            SELECT SUM(proteins) AS total_proteins,
                   SUM(carbohydrates) AS total_carbohydrates,
                   SUM(fats) AS total_fats,
                   SUM(calories) AS total_calories
            FROM food_log
            WHERE user_id = ? AND DATE(created_at) = DATE('now')
            """,
            user_id
        )[0]

    # Get the macros and calculate total calories consumed and remaining calories
    macros = get_macros()
    calorie_goal = db.execute("SELECT daily_calorie_goal FROM users WHERE id = ?", user_id)[0]["daily_calorie_goal"]
    total_consumed = macros["total_calories"] if macros["total_calories"] else 0
    remaining_calories = calorie_goal - total_consumed

    if request.method == "POST":
        # Determine which action was submitted from the form (add or delete)
        action = request.form.get("action")

        if action == "add":  # Handling for adding food items
            food_query = request.form.get("food")

            url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
            headers = {
                "x-app-id": nutritionix_api_id,
                "x-app-key": nutritionix_api_key,
                "Content-Type": "application/json"
            }
            data = {"query": food_query}
            response = requests.post(url, headers=headers, json=data)

            failed_items = []  # Initialize list for items not recognized by the API

            if response.status_code == 200:
                nutrition_data = response.json()

                if "foods" in nutrition_data and nutrition_data["foods"]:
                    # Extract the recognized food names in lowercase for comparison
                    recognized_foods = [food["food_name"].lower() for food in nutrition_data["foods"]]

                    # Split the user input by commas and trim whitespace
                    input_items = [item.strip().lower() for item in food_query.split(",")]

                    # Insert each recognized food item into the food_log table
                    for food in nutrition_data["foods"]:
                        try:
                            db.execute(
                                """
                                INSERT INTO food_log (user_id, food_name, serving_qty, serving_unit, calories, proteins, carbohydrates, fats)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                user_id,
                                food["food_name"].title(),  # Capitalize food name for consistency
                                food["serving_qty"],
                                food["serving_unit"],
                                food["nf_calories"],
                                food["nf_protein"],
                                food["nf_total_carbohydrate"],
                                food["nf_total_fat"]
                            )
                        except Exception:
                            pass  # Ignore errors during insertion

                    # Identify any input items that were not recognized by the API
                    failed_items = [
                        item for item in input_items
                        if not any(recognized_food in item for recognized_food in recognized_foods)
                    ]
                else:
                    # If no foods were recognized in the API response, consider all items as failed
                    failed_items = [item.strip() for item in food_query.split(",")]

            else:
                # If the API call fails, render the page with an error message
                return render_template(
                    "calorietracker.html",
                    food_log=food_log,
                    macros=macros,
                    total_consumed=round(total_consumed),
                    remaining_calories=round(remaining_calories),
                    calorie_goal=round(calorie_goal),
                    error="No valid food items were recognized. Please try again with specific food descriptions."
                )

            # Set an error message if there are any failed items to process
            error = None
            if failed_items:
                error = f"The following items could not be processed: {', '.join(failed_items)}."

            # Refresh food log and macros data after adding the food items
            food_log = db.execute(
                """
                SELECT id, food_name, serving_qty, serving_unit, calories, proteins, carbohydrates, fats
                FROM food_log
                WHERE user_id = ? AND DATE(created_at) = DATE('now')
                """,
                user_id
            )
            macros = get_macros()
            total_consumed = macros["total_calories"] if macros["total_calories"] else 0
            remaining_calories = calorie_goal - total_consumed

            # Render the calorietracker page with updated data and any error message
            return render_template(
                "calorietracker.html",
                food_log=food_log,
                macros=macros,
                total_consumed=round(total_consumed),
                remaining_calories=round(remaining_calories),
                calorie_goal=round(calorie_goal),
                error=error
            )

        elif action == "delete":  # Handling for deleting a food item
            food_id = request.form.get("food_id")
            # Delete the specified food item from the database
            db.execute("DELETE FROM food_log WHERE id = ? AND user_id = ?", food_id, user_id)
            # Redirect to the calorietracker page to refresh data after deletion
            return redirect("/calorietracker")

    # For GET requests, render the calorietracker page with the current food log and macros
    return render_template(
        "calorietracker.html",
        food_log=food_log,
        macros=macros,
        total_consumed=round(total_consumed),
        remaining_calories=round(remaining_calories),
        calorie_goal=round(calorie_goal)
    )



@app.route("/traininglog", methods=["GET", "POST"])
@login_required
def traininglog():
    # Retrieve the current user's ID from the session
    user_id = session["user_id"]

    if request.method == "POST":
        # Get the selected day_id from the form submission
        day_id = request.form.get("day_id")
        # Store the day_id in the session for later use in the training session
        session["day_id"] = day_id
        # Redirect the user to the training session page
        return redirect("/trainingsession")
    else:
        # For GET requests, first retrieve the user's training preferences
        user_data = db.execute(
            """
            SELECT training_days, experience_level
            FROM users
            WHERE id = ?
            """,
            user_id
        )

        # Retrieve program data including the last recorded weight (if available) for each exercise
        raw_program_data = db.execute(
            """
            SELECT
                pd.id AS day_id,
                pd.day_number,
                pd.day_name,
                pe.exercise_name,
                pe.sets,
                pe.reps,
                COALESCE(ls.last_weight, pe.weight) AS weight
            FROM
                training_programs tp
            JOIN
                program_days pd ON tp.id = pd.program_id
            JOIN
                program_exercises pe ON pd.id = pe.day_id
            LEFT JOIN LastSession ls
                ON pe.exercise_name = ls.exercise_name
                AND ls.user_id = ?
                AND ls.day_id = pd.id
            WHERE
                tp.days_per_week = ? AND
                tp.experience_level = ?
            ORDER BY
                pd.day_number, pe.exercise_name
            """,
            user_id, user_data[0]["training_days"], user_data[0]["experience_level"]
        )

        # Group the program data by day number for easier rendering in the template
        program_data = {}
        for row in raw_program_data:
            day_number = row["day_number"]
            if day_number not in program_data:
                program_data[day_number] = {
                    "day_id": row["day_id"],
                    "day_name": row["day_name"],
                    "exercises": []
                }
            program_data[day_number]["exercises"].append({
                "exercise_name": row["exercise_name"],
                "sets": row["sets"],
                "reps": row["reps"],
                "weight": row["weight"]
            })

        # Fetch training history from the last 7 days for display
        training_history = db.execute(
            """
            SELECT DATE(created_at) AS created_at, day_name, exercise_name, sets, reps, weight
            FROM TrainingLogs
            WHERE user_id = ? AND DATE(created_at) >= DATE('now', '-7 days')
            ORDER BY DATE(created_at) DESC, id DESC
            """,
            user_id
        )

        # Render the training log page with the program data and training history
        return render_template("traininglog.html", program_data=program_data, training_history=training_history)


@app.route("/trainingsession", methods=["GET", "POST"])
@login_required
def trainingsession():
    # Retrieve current user's ID and the selected day_id from the session
    user_id = session["user_id"]
    day_id = session.get("day_id")

    # If no day_id is stored, redirect back to the training log page
    if not day_id:
        return redirect("/traininglog")

    # Helper function to retrieve training data (exercises and day info) for the given day_id
    def get_training_data(user_id, day_id):
        # Fetch day information (day number and name)
        day_info = db.execute(
            """
            SELECT day_number, day_name
            FROM program_days
            WHERE id = ?
            """,
            day_id
        )
        # Fetch exercises for the day, including the last recorded weight if available
        exercises = db.execute(
            """
            SELECT
                pe.exercise_name,
                pe.sets,
                pe.reps,
                COALESCE(ls.last_weight, NULL) AS weight
            FROM program_exercises pe
            LEFT JOIN LastSession ls
                ON pe.exercise_name = ls.exercise_name
                AND ls.user_id = ?
                AND ls.day_id = pe.day_id
            WHERE pe.day_id = ?
            ORDER BY pe.exercise_name
            """,
            user_id, day_id
        )
        if not day_info:
            return None, None
        return exercises, day_info[0]

    if request.method == "POST":
        # Get the training data (exercises and day information) for the selected day
        exercises, day_info = get_training_data(user_id, day_id)
        if not exercises or not day_info:
            return redirect("/traininglog")

        # Generate a common timestamp for the entire training session
        session_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Loop through each exercise and record the entered weight
        for exercise in exercises:
            exercise_name = exercise["exercise_name"]
            weight = request.form.get(exercise_name, type=float)
            if weight is None:
                continue  # Skip if no weight is provided for this exercise
            # Insert a new record in the TrainingLogs table with the shared timestamp
            db.execute(
                """
                INSERT INTO TrainingLogs (user_id, day_id, day_name, exercise_name, sets, reps, weight, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                user_id, day_id, day_info["day_name"], exercise_name, exercise["sets"], exercise["reps"], weight, session_ts
            )
            # Check if a record exists in LastSession for the given exercise
            last_session_exists = db.execute(
                """
                SELECT last_weight FROM LastSession
                WHERE user_id = ? AND day_id = ? AND exercise_name = ?
                """,
                user_id, day_id, exercise_name
            )
            if last_session_exists:
                # Update the existing record with the new weight
                db.execute(
                    """
                    UPDATE LastSession
                    SET last_weight = ?
                    WHERE user_id = ? AND day_id = ? AND exercise_name = ?
                    """,
                    weight, user_id, day_id, exercise_name
                )
            else:
                # Insert a new record in LastSession if one does not exist
                db.execute(
                    """
                    INSERT INTO LastSession (user_id, day_id, exercise_name, last_weight)
                    VALUES (?, ?, ?, ?)
                    """,
                    user_id, day_id, exercise_name, weight
                )
        # Remove the day_id from session once the training session is completed
        session.pop("day_id", None)
        # Redirect back to the training log page after recording the session
        return redirect("/traininglog")
    else:
        # For GET requests, fetch the training data for the selected day
        exercises, day_info = get_training_data(user_id, day_id)
        if not exercises or not day_info:
            return redirect("/traininglog")
        # Render the training session page with the exercises and day info
        return render_template("training-session.html", training_data=exercises, day_info=day_info)



@app.route("/api/fitness_coach", methods=["POST"])
def fitness_coach():
    # Retrieve the JSON payload sent by the client
    data = request.get_json()

    # Extract the list of messages from the payload (e.g., chat history)
    messages = data.get("messages", [])

    # Define the system prompt that instructs the AI on its role and behavior
    system_prompt = (
        "You are a friendly and knowledgeable AI Fitness Coach on an English-language health and fitness website. "
        "The website allows users to:\n"
        "1. Track their daily calorie intake.\n"
        "2. Generate personalized workout plans.\n"
        "3. Log and monitor their workouts (exercises, sets, reps, etc.).\n"
        "4. Receive meal plans matching their calorie needs.\n"
        "5. Provide initial user data upon registration (name, email, password, age, weight, height, goal weight, gender, goal (lose weight, gain weight or maintain weight), Training experience level and training days per week).\n"
        "6. See a personalized dashboard with weekly calorie intake, weight progress, workout frequency, and daily/weekly check-ins.\n\n"
        "Behavior and style:\n"
        "1. Always be clear, concise, and supportive.\n"
        "2. Provide helpful suggestions on training, nutrition, or goal-setting within your knowledge.\n"
        "3. Avoid strict medical advice beyond general fitness.\n"
        "4. Respond in English unless otherwise requested.\n"
        "5. Keep answers relatively short and practical."
    )

    # Insert the system prompt at the beginning of the messages list
    messages.insert(0, {"role": "system", "content": system_prompt})

    # Get the OpenAI API key from environment variables
    if not openai_api_key:
        return jsonify({"reply": "No OpenAI API key found on the server."}), 500

    # Prepare headers for the OpenAI API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    # Prepare the payload for the chat completion request
    payload = {
        "model": "gpt-4",  # Use the GPT-4 model
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 150
    }

    try:
        # Make a POST request to the OpenAI Chat Completions endpoint
        openai_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        # Raise an error if the request did not succeed
        openai_response.raise_for_status()
        # Parse the JSON response from OpenAI
        response_data = openai_response.json()
        # Extract the reply from the response and strip extra whitespace
        reply = response_data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        # Print the error for debugging and set a default error reply
        print("Error calling OpenAI API:", e)
        reply = "I'm sorry, I couldn't process your request at the moment."

    # Return the reply as a JSON response to the client
    return jsonify({"reply": reply})


@app.route("/dashboard")
@login_required
def dashboard():
    # Get the current user's ID from the session
    user_id = session.get("user_id")

    # Fetch the user's data from the "users" table
    user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    if not user_data:
        # If no user is found, render the dashboard with an error message
        return render_template("dashboard/dashboard.html", error="User not found.", user={})
    user = user_data[0]
    user_name = user.get("name", "User")

    # 1. Latest Check-in Weight from the "check_ins" table
    latest_checkin_data = db.execute(
        "SELECT weight, created_at FROM check_ins WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        user_id
    )
    if latest_checkin_data:
        latest_weight = latest_checkin_data[0]["weight"]
    else:
        latest_weight = "No data yet"

    # 2. Average Caloric Intake for the current week
    today = datetime.today()
    # Determine the start of the week (Monday)
    start_of_week = today - timedelta(days=today.weekday())
    start_str = start_of_week.strftime("%Y-%m-%d")
    # Query the food_log for daily calories from the start of the week until now
    daily_data = db.execute(
        """
        SELECT DATE(created_at) AS day,
               SUM(calories) AS total_calories
        FROM food_log
        WHERE user_id = ?
          AND DATE(created_at) BETWEEN ? AND DATE('now', 'localtime')
          AND DATE(created_at) < DATE('now', 'localtime')
        GROUP BY day
        ORDER BY day ASC
        """,
        user_id, start_str
    )
    if daily_data:
        total_calories_week = sum(row["total_calories"] for row in daily_data)
        average_caloric_intake = round(total_calories_week / len(daily_data), 1)
    else:
        average_caloric_intake = "No data yet"

    # 3. Workouts This Week (from TrainingLogs)
    sessions_data = db.execute(
        """
        SELECT COUNT(DISTINCT created_at) AS session_count
        FROM TrainingLogs
        WHERE user_id = ?
          AND DATE(created_at) BETWEEN ? AND DATE('now', 'localtime')
        """,
        user_id, start_str
    )
    total_sessions = sessions_data[0]["session_count"] if sessions_data else 0

    # 4. Progress Towards Weight Goal calculation
    start_weight = user.get("start_weight")
    goal_weight = user.get("goal_weight")
    goal_type = user.get("goal_type", "stay at current weight")
    # Use the latest check-in weight if available, otherwise use the stored weight
    current_weight = latest_weight if latest_weight != "No data yet" else user.get("weight")
    progress = 0
    if start_weight and goal_weight and current_weight:
        if goal_type.lower() == "lose weight":
            progress = ((start_weight - current_weight) / (start_weight - goal_weight)) * 100
        elif goal_type.lower() == "gain weight":
            progress = ((current_weight - start_weight) / (goal_weight - start_weight)) * 100
        elif goal_type.lower() == "stay at current weight":
            progress = 0
        # Ensure the progress percentage is between 0 and 100 and round it
        progress = min(max(round(progress, 1), 0), 100)

    # 5. Weight Progress Graph – use the last 10 check-ins (chronologically from start to now)
    checkin_history = db.execute(
        "SELECT weight, DATE(created_at) as created_at FROM check_ins WHERE user_id = ? ORDER BY created_at ASC",
        user_id
    )
    # If there are 10 or more check-ins, use the last 10; otherwise, use all available data
    graph_data = checkin_history[-10:] if len(checkin_history) >= 10 else checkin_history
    weight_labels = [entry["created_at"] for entry in graph_data]
    weight_values = [entry["weight"] for entry in graph_data]

    # 6. Caloric Intake Chart – prepare data for the current week
    calorie_days = []
    calorie_values = []
    for row in daily_data:
        try:
            dt = datetime.strptime(row["day"], "%Y-%m-%d")
            # Format the date to display the weekday name
            weekday = dt.strftime("%A")
        except Exception:
            weekday = row["day"]
        calorie_days.append(weekday)
        calorie_values.append(row["total_calories"])
    # Retrieve the user's daily calorie goal
    calorie_goal = user.get("daily_calorie_goal", 0)

    # Render the dashboard template with all the calculated metrics and graph data
    return render_template(
        "dashboard/dashboard.html",
        user_name=user_name,
        latest_weight=latest_weight,
        average_caloric_intake=average_caloric_intake,
        total_sessions=total_sessions,
        progress=progress,
        weight_labels=weight_labels,
        weight_values=weight_values,
        calorie_days=calorie_days,
        calorie_values=calorie_values,
        calorie_goal=calorie_goal,
        start_of_week=start_str
    )




@app.route("/checkin", methods=["GET", "POST"])
@login_required
def checkin():
    # Retrieve the current user's ID from the session
    user_id = session.get("user_id")

    if request.method == "POST":
        # Get form inputs for energy and sleep
        energy = request.form.get("energy")
        sleep = request.form.get("sleep")

        # Validate and convert the weight input to a float
        try:
            weight = float(request.form.get("weight"))
        except ValueError:
            return render_template("dashboard/checkin.html", error="Weight must be a number")

        # Validate the energy input as an integer between 1 and 10
        try:
            energy = int(energy)
            if not 1 <= energy <= 10:
                raise ValueError
        except ValueError:
            return render_template("dashboard/checkin.html", error="Energy must be a number between 1 and 10.")

        # Validate the sleep input as a float between 0 and 24
        try:
            sleep = float(sleep)
            if not 0 <= sleep <= 24:
                raise ValueError
        except ValueError:
            return render_template("dashboard/checkin.html", error="Sleep must be a number between 0 and 24.")

        # Insert the check-in data into the check_ins table
        db.execute(
            "INSERT INTO check_ins (user_id, weight, energy, sleep) VALUES (?, ?, ?, ?)",
            user_id, weight, energy, sleep
        )

        # Fetch existing user data needed for BMR and calorie calculations
        user_data = db.execute("SELECT age, gender, height, training_days, goal_type FROM users WHERE id = ?", user_id)
        if not user_data:
            return render_template("dashboard/checkin.html", error="User not found")
        user = user_data[0]

        # Calculate BMR (Basal Metabolic Rate) using the new weight and user's data
        age = user["age"]
        gender = user["gender"]
        height = float(user["height"])
        training_days = int(user["training_days"])
        goal_type = user["goal_type"]

        if gender == "Male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # Calculate calorie intake based on the number of training days
        if 1 <= training_days <= 3:
            calorie_intake = bmr * 1.375
        elif 4 <= training_days <= 5:
            calorie_intake = bmr * 1.55
        else:
            calorie_intake = bmr * 1.725

        # Adjust calorie intake based on the user's goal (lose/gain weight)
        if goal_type == "lose weight":
            calorie_intake = round(calorie_intake - 500)
        elif goal_type == "gain weight":
            calorie_intake = round(calorie_intake + 500)
        else:
            calorie_intake = round(calorie_intake)

        # Update the user's record with the new weight and calculated daily calorie goal
        db.execute(
            "UPDATE users SET weight = ?, daily_calorie_goal = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            weight, calorie_intake, user_id
        )

        # Redirect to the check-in page to reflect the new data
        return redirect("/checkin")

    else:
        # GET request: Retrieve all check-in data for the current user
        checkin_data = db.execute(
            "SELECT weight, energy, sleep, date(created_at) as created_at FROM check_ins WHERE user_id = ?",
            user_id
        )

        # Retrieve the user's name from the users table for personalized display
        user = db.execute("SELECT name FROM users WHERE id = ?", user_id)
        if user:
            user_name = user[0]["name"]
        else:
            user_name = "User"

        # Calculate averages for weight, energy, and sleep if check-in data exists
        if checkin_data:
            total_weight = sum(entry["weight"] for entry in checkin_data)
            total_energy = sum(entry["energy"] for entry in checkin_data)
            total_sleep  = sum(entry["sleep"] for entry in checkin_data)
            count = len(checkin_data)

            avg_weight = round(total_weight / count, 1)
            avg_energy = round(total_energy / count, 1)
            avg_sleep  = round(total_sleep / count, 1)
        else:
            avg_weight = avg_energy = avg_sleep = "No data yet"

        # Render the check-in page with average values and history data
        return render_template(
            "dashboard/checkin.html",
            avg_weight=avg_weight,
            avg_energy=avg_energy,
            avg_sleep=avg_sleep,
            checkin_data=checkin_data,
            user_name=user_name
        )



@app.route("/weight")
@login_required
def weight_progress():
    user_id = session.get("user_id")

    # Fetch all check-ins for the user (ordered chronologically, oldest first)
    checkin_data = db.execute(
        "SELECT weight, date(created_at) as created_at FROM check_ins WHERE user_id = ? ORDER BY created_at ASC",
        user_id
    )

    # Fetch the user's information including name, start_weight, goal_weight, and goal_type
    user = db.execute("SELECT name, start_weight, goal_weight, goal_type FROM users WHERE id = ?", user_id)
    if user:
        user_info   = user[0]
        user_name   = user_info["name"]
        start_weight = user_info.get("start_weight")  # Expected to be numeric
        goal_weight  = user_info.get("goal_weight")
        goal_type    = user_info.get("goal_type", "stay at current weight")
    else:
        user_name = "User"
        start_weight = None
        goal_weight = None
        goal_type = "stay at current weight"

    # Determine current weight from the most recent check-in
    if checkin_data:
        current_weight = checkin_data[-1]["weight"]
    else:
        current_weight = None

    default_text = "No data yet"

    # Calculate weight change (to be displayed in the central card)
    if start_weight is not None and current_weight is not None:
        if goal_type.lower() == "lose weight":
            weight_change = round(start_weight - current_weight, 1)
        elif goal_type.lower() == "gain weight":
            weight_change = round(current_weight - start_weight, 1)
        elif goal_type.lower() == "stay at current weight":
            # Calculate the actual deviation from the starting weight, which can be both positive or negative.
            weight_change = round(current_weight - start_weight, 1)
        else:
            weight_change = None
    else:
        weight_change = None

    if weight_change is not None:
        if weight_change > 0:
            # If there is an increase (or a loss in case of "lose weight", which should be positive)
            sign = "-" if goal_type.lower() == "lose weight" else "+"
            weight_change_display = sign + str(abs(weight_change))
        else:
            # If there is a decrease (or negative change for "gain weight")
            sign = "-" if goal_type.lower() == "lose weight" else "+"
            weight_change_display = sign + str(abs(weight_change))
    else:
        weight_change_display = default_text

    # Choose an appropriate label based on the goal type
    if goal_type.lower() == "lose weight":
        weight_change_label = "Weight Lost"
    elif goal_type.lower() == "gain weight":
        weight_change_label = "Weight Gain"
    elif goal_type.lower() == "stay at current weight":
        weight_change_label = "Weight Change"
    else:
        weight_change_label = "Weight Change"

    # Calculate the average change per week based on the entire period of check-ins
    if checkin_data and start_weight is not None:
        first_entry = checkin_data[0]
        last_entry  = checkin_data[-1]
        try:
            first_date = datetime.strptime(first_entry["created_at"], "%Y-%m-%d")
            last_date  = datetime.strptime(last_entry["created_at"], "%Y-%m-%d")
        except Exception:
            first_date = last_date = datetime.now()

        diff_days = (last_date - first_date).days
        # If the period is less than 7 days, assume the data covers 1 week
        weeks = diff_days / 7 if diff_days >= 7 else 1

        if goal_type.lower() == "lose weight":
            total_change = start_weight - last_entry["weight"]
        elif goal_type.lower() == "gain weight":
            total_change = last_entry["weight"] - start_weight
        elif goal_type.lower() == "stay at current weight":
            total_change = last_entry["weight"] - start_weight
        else:
            total_change = 0

        avg_change_per_week = round(total_change / weeks, 1)
    else:
        avg_change_per_week = None

    if avg_change_per_week is not None:
        if avg_change_per_week > 0:
            sign = "-" if goal_type.lower() == "lose weight" else "+"
            avg_change_display = sign + str(abs(avg_change_per_week))
        else:
            sign = "-" if goal_type.lower() == "lose weight" else "+"
            avg_change_display = sign + str(abs(avg_change_per_week))
    else:
        avg_change_display = default_text

    # Calculate progress percentage – how much of the goal has been achieved
    if start_weight is not None and goal_weight is not None and current_weight is not None:
        if goal_type.lower() == "lose weight":
            progress = ((start_weight - current_weight) / (start_weight - goal_weight)) * 100
        elif goal_type.lower() == "gain weight":
            progress = ((current_weight - start_weight) / (goal_weight - start_weight)) * 100
        elif goal_type.lower() == "stay at current weight":
            progress = 0
        else:
            progress = 0
        progress = min(max(round(progress, 1), 0), 100)
    else:
        progress = None

    # Calculate the weight log: compare each check-in with the previous one to compute the change
    weight_log = []
    for i, entry in enumerate(checkin_data):
        if i == 0:
            change = "-"  # No previous check-in
        else:
            prev_weight = checkin_data[i-1]["weight"]
            diff = round(entry["weight"] - prev_weight, 1)
            if diff > 0:
                change = f"+{diff}"
            else:
                change = f"{diff}"
        weight_log.append({
            "date": entry["created_at"],
            "weight": entry["weight"],
            "change": change
        })
    # Limit the weight log to the 10 most recent check-ins
    if len(weight_log) > 10:
        weight_log = weight_log[-10:]

    # Select graph data: use the last 10 check-ins (if there are at least 10)
    graph_data = checkin_data[-10:] if len(checkin_data) >= 10 else checkin_data

    return render_template(
        "dashboard/weight.html",
        user_name=user_name,
        current_weight=current_weight if current_weight is not None else default_text,
        weight_lost=weight_change_display,
        weight_change_label=weight_change_label,
        avg_loss_per_week=avg_change_display,
        progress=progress if progress is not None else 0,
        weight_log=weight_log,
        graph_data=graph_data,
        start_weight=start_weight if start_weight is not None else default_text,
        goal_weight=goal_weight if goal_weight is not None else default_text
    )


@app.route("/calories")
@login_required
def calories():
    # Retrieve the current user's ID from the session
    user_id = session.get("user_id")

    # Fetch the user's daily calorie goal and name from the "users" table
    user_data = db.execute("SELECT name, daily_calorie_goal FROM users WHERE id = ?", user_id)
    if user_data:
        user_name = user_data[0]["name"]
        calorie_goal = user_data[0]["daily_calorie_goal"]
    else:
        user_name = "User"
        calorie_goal = 0

    from datetime import datetime, timedelta
    today = datetime.today()
    # Calculate the start of the week (assuming Monday as the first day)
    start_of_week = today - timedelta(days=today.weekday())
    start_str = start_of_week.strftime("%Y-%m-%d")

    # Retrieve daily nutrition data from the food_log for complete days (i.e., before today)
    daily_data = db.execute(
        """
        SELECT DATE(created_at) AS day,
               SUM(calories) AS total_calories,
               SUM(proteins) AS total_proteins,
               SUM(carbohydrates) AS total_carbohydrates,
               SUM(fats) AS total_fats
        FROM food_log
        WHERE user_id = ?
          AND DATE(created_at) BETWEEN ? AND DATE('now', 'localtime')
          AND DATE(created_at) < DATE('now', 'localtime')
        GROUP BY day
        ORDER BY day ASC
        """,
        user_id, start_str
    )

    # Calculate average daily intake and average protein intake for the week
    if daily_data:
        total_calories_week = sum([row["total_calories"] for row in daily_data])
        average_daily_intake = round(total_calories_week / len(daily_data), 1)
        total_proteins_week = sum([row["total_proteins"] for row in daily_data])
        avg_protein_intake = round(total_proteins_week / len(daily_data), 1)
    else:
        average_daily_intake = "No data yet"
        avg_protein_intake = "No data yet"

    # Calculate Planned vs. Actual calories for the latest complete day
    if daily_data:
        latest_day_data = daily_data[-1]
        actual_intake = latest_day_data["total_calories"]
    else:
        actual_intake = 0
    planned_vs_actual = round(calorie_goal - actual_intake)

    # Add a weekday label to each row in daily_data for display purposes
    from datetime import datetime
    for row in daily_data:
        try:
            dt = datetime.strptime(row["day"], "%Y-%m-%d")
            row["weekday"] = dt.strftime("%A")
        except Exception:
            row["weekday"] = row["day"]

    # Identify the day with the lowest and highest calorie consumption
    best_day = min(daily_data, key=lambda row: row["total_calories"]) if daily_data else None
    worst_day = max(daily_data, key=lambda row: row["total_calories"]) if daily_data else None

    # Render the calories dashboard template with the calculated values and data
    return render_template(
        "dashboard/calories.html",
        user_name=user_name,
        average_daily_intake=average_daily_intake,
        planned_vs_actual=planned_vs_actual,
        calorie_goal=calorie_goal,
        avg_protein_intake=avg_protein_intake,
        daily_data=daily_data,
        best_day=best_day,
        worst_day=worst_day,
        start_of_week=start_str
    )


@app.route("/training")
@login_required
def training():
    # Retrieve the current user's ID from the session
    user_id = session.get("user_id")

    from datetime import datetime, timedelta
    today = datetime.today()
    # Calculate start (Monday) and end (Sunday) of the current week
    start_of_week = today - timedelta(days=today.weekday())  # Monday of this week
    end_of_week = start_of_week + timedelta(days=6)            # Sunday of this week
    start_str = start_of_week.strftime("%Y-%m-%d")
    end_str = end_of_week.strftime("%Y-%m-%d")

    # Helper function: Convert a week label (e.g., "2023-14") to a date range string
    def format_week_range(week_label):
        dt = datetime.strptime(week_label + '-1', "%Y-%W-%w")
        week_start = dt.strftime("%Y-%m-%d")
        week_end = (dt + timedelta(days=6)).strftime("%Y-%m-%d")
        return f"{week_start} - {week_end}"

    # Retrieve total training sessions for the current week by counting distinct timestamps
    sessions = db.execute(
        """
        SELECT COUNT(DISTINCT created_at) AS session_count
        FROM TrainingLogs
        WHERE user_id = ?
          AND DATE(created_at) BETWEEN ? AND DATE('now', 'localtime')
        """,
        user_id, start_str
    )
    total_sessions = sessions[0]["session_count"] if sessions else 0

    # Retrieve total sets performed this week
    sets_data = db.execute(
        """
        SELECT SUM(sets) AS total_sets
        FROM TrainingLogs
        WHERE user_id = ?
          AND DATE(created_at) BETWEEN ? AND DATE('now', 'localtime')
        """,
        user_id, start_str
    )
    total_sets = sets_data[0]["total_sets"] if sets_data and sets_data[0]["total_sets"] is not None else 0

    # Beregn gennemsnitlig vægtstigning baseret på træningsloggene: sammenlign nuværende uge med sidste uge
    last_week_start = start_of_week - timedelta(days=7)
    last_week_end   = start_of_week - timedelta(days=1)
    last_start_str  = last_week_start.strftime("%Y-%m-%d")
    last_end_str    = last_week_end.strftime("%Y-%m-%d")

    current_weights = db.execute(
        """
        SELECT exercise_name, AVG(weight) AS avg_weight
        FROM TrainingLogs
        WHERE user_id = ?
          AND DATE(created_at) BETWEEN ? AND DATE('now', 'localtime')
        GROUP BY exercise_name
        """,
        user_id, start_str
    )
    last_weights = db.execute(
        """
        SELECT exercise_name, AVG(weight) AS avg_weight
        FROM TrainingLogs
        WHERE user_id = ?
          AND DATE(created_at) BETWEEN ? AND ?
        GROUP BY exercise_name
        """,
        user_id, last_start_str, last_end_str
    )
    diffs = []
    for cw in current_weights:
        for lw in last_weights:
            if cw["exercise_name"] == lw["exercise_name"] and cw["avg_weight"] is not None and lw["avg_weight"] is not None:
                diff = cw["avg_weight"] - lw["avg_weight"]
                diffs.append(diff)
    avg_weight_increase = round(sum(diffs) / len(diffs), 1) if diffs else 0

    # Calculate total training volume per muscle group, excluding the "core" group
    volume_data = db.execute(
        """
        SELECT pe.muscle, SUM(tl.weight * tl.sets) AS total_volume
        FROM TrainingLogs tl
        JOIN program_exercises pe ON tl.exercise_name = pe.exercise_name AND tl.day_id = pe.day_id
        WHERE tl.user_id = ?
          AND DATE(tl.created_at) BETWEEN ? AND DATE('now', 'localtime')
          AND pe.muscle <> 'core'
        GROUP BY pe.muscle
        """,
        user_id, start_str
    )

    # Retrieve training frequency for the last 4 weeks
    freq_data = db.execute(
        """
        SELECT strftime('%Y-%W', created_at) AS week, COUNT(DISTINCT created_at) AS sessions
        FROM TrainingLogs
        WHERE user_id = ?
        GROUP BY week
        ORDER BY week ASC
        """,
        user_id
    )
    for row in freq_data:
        row["week_range"] = format_week_range(row["week"])

    # Group session data by date and day_name for an overview of training sessions
    sessions_overview = db.execute(
        """
        SELECT DATE(created_at) AS session_date, day_name, COUNT(*) AS exercises_count
        FROM TrainingLogs
        WHERE user_id = ?
          AND DATE(created_at) BETWEEN ? AND DATE('now', 'localtime')
        GROUP BY created_at, day_name
        ORDER BY created_at DESC
        """,
        user_id, start_str
    )

    return render_template(
        "dashboard/training.html",
        total_sessions=total_sessions,
        total_sets=total_sets,
        avg_weight_increase=avg_weight_increase,
        volume_data=volume_data,
        freq_data=freq_data,
        sessions_overview=sessions_overview,
        start_of_week=start_str,
        end_of_week=end_str
    )




@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    # Retrieve the current user's ID from the session
    user_id = session.get("user_id")

    # Fetch the current user data so that existing values can be used if no new value is provided
    user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    if not user_data:
        return render_template("dashboard/settings.html", error="User not found.", user={})
    user = user_data[0]

    if request.method == "POST":
        # For each field: if a new value is provided, use it; otherwise, keep the existing value

        # Age
        age_input = request.form.get("age")
        if age_input:
            try:
                age = int(age_input)
            except ValueError:
                return render_template("dashboard/settings.html", error="Please enter a valid number for age.", user=user)
        else:
            age = user["age"]

        # Gender
        gender_input = request.form.get("gender")
        if gender_input:
            if gender_input not in ["Male", "Female"]:
                return render_template("dashboard/settings.html", error="Please select a valid gender", user=user)
            gender = gender_input
        else:
            gender = user["gender"]

        # Height and Goal Weight
        height_input = request.form.get("height")
        goal_weight_input = request.form.get("goal_weight")
        try:
            height = float(height_input) if height_input else float(user["height"])
            goal_weight = float(goal_weight_input) if goal_weight_input else float(user["goal_weight"])
        except ValueError:
            return render_template("dashboard/settings.html", error="Height and goal weight must be numbers", user=user)

        # Goal Type
        goal_type_input = request.form.get("goal_type")
        if goal_type_input:
            if goal_type_input not in ["lose weight", "gain weight", "stay at current weight"]:
                return render_template("dashboard/settings.html", error="Please select a valid goal", user=user)
            goal_type = goal_type_input
        else:
            goal_type = user["goal_type"]

        # Experience Level
        experience_level_input = request.form.get("experience_level")
        if experience_level_input:
            if experience_level_input not in ["Beginner", "Intermediate", "Advanced"]:
                return render_template("dashboard/settings.html", error="Please select a valid experience level", user=user)
            experience_level = experience_level_input
        else:
            experience_level = user["experience_level"]

        # Training Days
        training_days_input = request.form.get("training_days")
        if training_days_input:
            try:
                training_days = int(training_days_input)
                if not (1 <= training_days <= 7):
                    return render_template("dashboard/settings.html", error="Training days must be between 1 and 7.", user=user)
            except ValueError:
                return render_template("dashboard/settings.html", error="Training days must be a number", user=user)
        else:
            training_days = user["training_days"]

        # Use the existing weight from the database (the user does not update their weight here)
        weight = float(user["weight"])

        # Calculate BMR based on the current values using the Mifflin-St Jeor equation
        if gender == "Male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # Calculate calorie intake based on the number of training days
        if 1 <= training_days <= 3:
            calorie_intake = bmr * 1.375
        elif 4 <= training_days <= 5:
            calorie_intake = bmr * 1.55
        else:
            calorie_intake = bmr * 1.725

        # Adjust the calorie intake based on the goal type
        if goal_type == "lose weight":
            calorie_intake = round(calorie_intake - 500)
        elif goal_type == "gain weight":
            calorie_intake = round(calorie_intake + 500)
        else:
            calorie_intake = round(calorie_intake)

        # Update the user's data in the database, including the new calorie intake.
        # Note: The weight remains unchanged.
        db.execute(
            """
            UPDATE users
            SET age = ?,
                gender = ?,
                height = ?,
                goal_weight = ?,
                goal_type = ?,
                experience_level = ?,
                training_days = ?,
                daily_calorie_goal = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            age,
            gender,
            height,
            goal_weight,
            goal_type,
            experience_level,
            training_days,
            calorie_intake,
            user_id
        )

        return redirect("/settings")

    # GET-request: Return the current user data with an empty error message
    return render_template("dashboard/settings.html", user=user, error=None)



@app.route("/mealplan", methods=["GET", "POST"])
@login_required
def mealplan():
    # Get the current logged-in user's ID from the session
    user_id = session["user_id"]

    # Define maximum allowed values for macronutrients
    MAX_PROTEIN = 125
    MAX_CARBS = 250
    MAX_FAT = 87

    def select_data(user_id):
        """
        Retrieve meal plans and their associated meals for the given user.
        """

        # Fetch all meal plans for the current user, ordered by creation date (most recent first)
        meal_plans = db.execute(
            """
            SELECT id, name, calories, protein, carbohydrates, fat
            FROM meal_plans
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            user_id
        )

        # Fetch all meals linked to the user's meal plans
        meals = db.execute(
            """
            SELECT meal_id, meal_plan_id, title, source_url, ready_in_minutes, imagetype
            FROM meal_plan_meals
            WHERE meal_plan_id IN (SELECT id FROM meal_plans WHERE user_id = ?)
            """,
            user_id
        )

        # Organize meals by their corresponding meal plan ID for easier access
        meals_by_plan = {}
        for meal in meals:
            meal_plan_id = meal["meal_plan_id"]
            if meal_plan_id not in meals_by_plan:
                meals_by_plan[meal_plan_id] = []
            meals_by_plan[meal_plan_id].append(meal)

        return meal_plans, meals_by_plan

    def calculate_macronutrients(calorie_goal, goal_type):
        """
        Calculate minimum amounts of protein, carbohydrates, and fat based on the user's calorie goal and goal type.
        - For weight loss, use a 35/30/35 split.
        - For muscle gain, use a 40/40/20 split.
        - For maintenance, use a 30/40/30 split.

        Each macronutrient is then capped at its maximum value.
        """
        if goal_type == "weight_loss":
            protein_ratio, carb_ratio, fat_ratio = 0.35, 0.30, 0.35
        elif goal_type == "muscle_gain":
            protein_ratio, carb_ratio, fat_ratio = 0.40, 0.40, 0.20
        else:  # maintenance
            protein_ratio, carb_ratio, fat_ratio = 0.30, 0.40, 0.30

        # Convert calorie percentages to grams:
        # - 1 gram of protein or carbohydrates provides 4 kcal.
        # - 1 gram of fat provides 9 kcal.
        protein = min(calorie_goal * protein_ratio / 4, MAX_PROTEIN)
        carbs = min(calorie_goal * carb_ratio / 4, MAX_CARBS)
        fat = min(calorie_goal * fat_ratio / 9, MAX_FAT)
        return round(protein), round(carbs), round(fat)

    # Handle POST requests for adding or deleting meal plans
    if request.method == "POST":
        action = request.form.get("action")

        if action == "delete":
            # Retrieve the meal plan ID from the form data
            plan_id = request.form.get("plan_id")
            if plan_id:
                # First, delete all meals associated with this meal plan
                db.execute("DELETE FROM meal_plan_meals WHERE meal_plan_id = ?", plan_id)
                # Then, delete the meal plan itself (ensuring it belongs to the current user)
                db.execute("DELETE FROM meal_plans WHERE id = ? AND user_id = ?", plan_id, user_id)
            # Redirect back to the meal plan page after deletion
            return redirect("/mealplan")

        elif action == "add":
            # Validate that a meal plan name has been provided
            if not request.form.get("plan_name"):
                # Use flash to display an error message to the user
                flash("Please enter a meal plan name.", "error")
                return redirect("/mealplan")

            # Retrieve the user's daily calorie goal and goal type from the database
            user_data = db.execute("SELECT daily_calorie_goal, goal_type FROM users WHERE id = ?", user_id)[0]
            calorie_goal = user_data["daily_calorie_goal"]

            # Define the maximum calorie value that can be handled
            MAX_CALORIES = 3443
            if calorie_goal > MAX_CALORIES:
                # Cap the calorie goal and inform the user via a warning message
                calorie_goal = MAX_CALORIES
                flash(
                    "Your daily calorie goal exceeds the maximum we can generate a plan for (3440 kcal). "
                    "We have created a plan with the highest available calorie value.",
                    "warning"
                )
            goal_type = user_data["goal_type"]

            # Calculate total macronutrients for the entire meal plan
            total_protein, total_carbs, total_fat = calculate_macronutrients(calorie_goal, goal_type)
            # Distribute approximately 70% of one-third of each macronutrient to each meal
            meal_protein = round(total_protein / 3 * 0.70)
            meal_carbs = round(total_carbs / 3 * 0.70)
            meal_fat = round(total_fat / 3 * 0.70)
            # Divide the total calorie goal equally among three meals
            calorie_goal = calorie_goal / 3

            # Set up parameters for calling the Spoonacular API to fetch recipes
            # The plan includes breakfast, lunch, and dinner (using 'main course' for lunch and dinner)
            meal_types = ["breakfast", "main course", "main course"]
            meals = []
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            offset = 0  # Offset is used to fetch different meals for each API call

            # Loop through each meal type and fetch one meal that meets the nutritional criteria
            for meal_type in meal_types:
                url = "https://api.spoonacular.com/recipes/complexSearch"
                params = {
                    "apiKey": spoonacular_api_key,
                    "type": meal_type,
                    # Set a calorie range around the target for each meal (with some buffer)
                    "minCalories": min(calorie_goal - 100, 1100),
                    "maxCalories": min(calorie_goal + 100, 1300),
                    "addRecipeNutrition": True,
                    "number": 1,  # Fetch one recipe per meal type
                    "offset": offset,
                    "instructionsRequired": True,
                    "minProtein": meal_protein,
                    "minCarbs": meal_carbs,
                    "minFat": meal_fat
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    result = response.json().get("results", [])
                    if result:
                        # Select the first (and only) recipe result
                        meal = result[0]
                        meals.append(meal)
                        offset += 1  # Increase offset to get a different meal for the next API call
                        # Extract nutrient details from the recipe and accumulate the totals
                        nutrients = meal.get("nutrition", {}).get("nutrients", [])
                        total_calories += next((n["amount"] for n in nutrients if n["name"] == "Calories"), 0)
                        total_protein += next((n["amount"] for n in nutrients if n["name"] == "Protein"), 0)
                        total_carbs += next((n["amount"] for n in nutrients if n["name"] == "Carbohydrates"), 0)
                        total_fat += next((n["amount"] for n in nutrients if n["name"] == "Fat"), 0)
                else:
                    # If the API request fails, notify the user and redirect back to the meal plan page
                    flash(f"Failed to fetch {meal_type}. Try again.", "error")
                    return redirect("/mealplan")

            # Ensure that exactly three meals have been retrieved to form a complete meal plan
            if not meals or len(meals) != 3:
                flash("Could not generate a complete meal plan. Try again.", "error")
                return redirect("/mealplan")

            # Insert the new meal plan into the database and obtain its generated ID
            meal_plan_id = db.execute(
                """
                INSERT INTO meal_plans (user_id, name, calories, protein, carbohydrates, fat)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                user_id, request.form.get("plan_name"), round(total_calories), round(total_protein), round(total_carbs), round(total_fat)
            )

            # Insert each individual meal associated with this meal plan into the database
            for meal in meals:
                db.execute(
                    """
                    INSERT INTO meal_plan_meals (meal_id, meal_plan_id, title, source_url, ready_in_minutes, imagetype)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    meal["id"], meal_plan_id, meal["title"], meal["sourceUrl"], meal.get("readyInMinutes", 0), meal["imageType"]
                )
            # After adding the meal plan and its meals, redirect to the GET view of the meal plan page
            return redirect("/mealplan")

    # For GET requests, retrieve the user's meal plans and their corresponding meals
    meal_plans, meals_by_plan = select_data(user_id)
    # Render the mealplan HTML template, passing the retrieved data for display
    return render_template("mealplan.html", meal_plans=meal_plans, meals_by_plan=meals_by_plan)



