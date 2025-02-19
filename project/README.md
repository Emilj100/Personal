# Health & Fitness Tracker

#### Video Demo: [https://your-video-demo-url.com](https://your-video-demo-url.com)

#### Description:

The Health & Fitness Tracker is a comprehensive web-based application designed to help users manage and monitor their fitness journey. Built with Python and Flask, the project provides an integrated platform for tracking workouts, monitoring calorie intake, logging training sessions, planning meals, and even interacting with an AI fitness coach. The application leverages multiple external APIs to enhance functionality, including Nutritionix for nutritional data, Spoonacular for meal planning, and OpenAI for the AI fitness coach feature.

## Project Overview

The project is structured as a full-stack web application with clearly defined backend and frontend components. The backend, written in Python using Flask, handles user authentication, session management, data validation, and interactions with an SQLite database via CS50’s SQL module. On the frontend, Jinja2 templates render the user interface, while custom CSS and JavaScript, in combination with Bootstrap, provide styling and interactivity.

### Key Features:

1. **User Registration and Login:**
   The registration process is divided into two parts to collect user details in a structured manner. In the first part, users provide basic details such as name, email, and password. The second part collects additional data like age, gender, height, weight, goal weight, training days per week, and experience level. Passwords are securely handled using salted hash functions, and sessions are properly managed to keep users authenticated throughout their interactions.

2. **Calorie Tracker:**
   The calorie tracker allows users to log their daily food intake. By integrating with the Nutritionix API, the application can automatically fetch nutritional information based on user input. The system then aggregates these details to display daily macro-nutrient totals (proteins, carbohydrates, fats) and overall caloric intake. Users can also delete mistakenly added items, with the interface dynamically updating to reflect the current state.

3. **Training Log and Sessions:**
   Users can view a personalized training log that outlines their scheduled workout days and detailed exercises. Each training session allows the logging of weights, sets, and reps for each exercise. The application stores this data in the TrainingLogs table and uses it to generate summaries and graphs showing workout frequency, weight progress, and session history. The training log also offers historical insights over the past week, providing users with a clear view of their progress.

4. **Meal Planner:**
   The meal planner feature generates daily meal plans based on the user’s calorie goals and macronutrient requirements. By interfacing with the Spoonacular API, the application retrieves recipes for breakfast, lunch, and dinner that fit within the calculated nutritional ranges. Users can also delete or add meal plans, and the system ensures that the nutritional breakdown is maintained according to the specified limits.

5. **AI Fitness Coach Chat:**
   A unique aspect of the project is the integrated AI fitness coach chat. This feature uses the OpenAI API (GPT-4) to provide personalized fitness advice and answer user queries. Users can interact with the chat widget to get tips on training, nutrition, or general goal setting. The conversation history is stored in the user’s session, and the system ensures that only the most recent messages are sent to the API for context.

6. **Dashboard and Analytics:**
   The dashboard aggregates data from various sources to provide users with key metrics such as:
   - Latest check-in weight and average weekly calorie intake.
   - Graphs displaying weight progress over time.
   - Training session counts and volume metrics.
   - Comparative analyses between planned and actual calorie intake.
   This data is visualized using interactive charts and tables, making it easy for users to understand their fitness progress at a glance.

## File and Module Overview

- **app.py:**
  The main application file that initializes the Flask app, configures sessions, and defines all routes. It contains the core business logic for user authentication, registration, logging food and training data, meal planning, and interfacing with external APIs.

- **Templates Folder:**
  Contains Jinja2 template files (HTML) for rendering various pages such as the index, registration, login, dashboard, calorie tracker, training log, training session, meal plan, check-in, and settings pages. Each template is designed to be responsive and user-friendly.

- **Static Folder (CSS & JS):**
  - **CSS Files:**
    Custom styles for the application, including styling for forms, buttons, tables, dashboards, and animations. The project also leverages Bootstrap for responsive design and pre-built UI components.
  - **JavaScript Files:**
    Provide client-side interactivity, including dynamic updates to charts, chat widget functionalities, and form validations. For example, `chat.js` handles the interaction with the AI fitness coach, and Bootstrap’s JavaScript components enhance the UI behavior.

- **Database (SQLite):**
  The SQLite database (health.db) stores all user data, training logs, food logs, check-ins, meal plans, and other relevant information. Parameterized queries are used throughout to ensure protection against SQL injection.

## Design Choices and Security Considerations

Several design choices were made to enhance both the functionality and security of the project:

- **Session Management and Security:**
  Sessions are stored in the filesystem, and sensitive data is managed securely. User sessions are cleared upon login and logout to avoid stale data. Additional cookie security settings can be configured to further protect sessions.

- **Input Validation:**
  Input validation is implemented rigorously across all forms. Regular expressions are used for email validation, numeric checks ensure valid input for weight, age, and other metrics, and logical checks confirm that fields like training days fall within acceptable ranges. These measures help prevent both accidental user errors and malicious inputs.

- **Password Security:**
  Passwords are hashed using industry-standard methods before being stored in the database, ensuring that even if the database were compromised, raw passwords would not be exposed.

- **Error Handling:**
  The project implements basic error handling by validating user inputs and providing informative error messages. This not only enhances the user experience but also helps prevent unintended behavior during data processing.

## Future Enhancements

While the current implementation meets the project requirements, several areas could be further improved:
- **CSRF Protection:** Integrating CSRF tokens into forms would help prevent cross-site request forgery attacks.
- **Enhanced UI/UX:** Additional client-side validation and a more polished interface could be implemented for an even better user experience.
- **Scalability:** For larger deployments, migrating from SQLite to a more robust database solution and enhancing session management could be beneficial.

In summary, the Health & Fitness Tracker is a robust and feature-rich application that allows users to manage every aspect of their fitness journey. With thoughtful design, comprehensive input validation, secure session management, and the use of modern UI frameworks like Bootstrap, this project provides a solid foundation for further development and potential real-world deployment.

