# TripNavigator

TripNavigator is a comprehensive web application designed to help users plan and manage their entire trip. The application combines features such as flight and hotel search, day planning, budgeting, document storage, map navigation, and an AI-based chat assistant that offers personalized travel suggestions and advice. With its intuitive and mobile-responsive design, TripNavigator ensures that all essential travel functions are available in one modern, unified platform.

## Features

- **Flight, Hotel & Experience Search:** Easily find the best flights, hotels, and experiences for your destination.
- **AI Chat Assistant:** An integrated ChatGPT-powered assistant (using GPT-3.5-turbo) provides dynamic travel suggestions and expert travel advice.
- **Travel Planning:** Create, edit, and share travel plans, including managing activities and daily itineraries.
- **Budget Management:** Keep track of your expenses with a dedicated budget dashboard that visualizes spending across different categories.
- **Document Management:** Upload and store important travel documents directly within the application.
- **Map Navigation:** Use interactive maps for navigating your planned activities with integrated geocoding.
- **User and Profile Settings:** Manage your account details, update profile settings, and change your password easily.

## Distinctiveness and Complexity

### Distinctiveness
TripNavigator stands apart from previous projects by focusing exclusively on travel planning and management, rather than serving as a social network or e-commerce site. The application offers a unique blend of features:
- **AI-Powered Travel Assistance:** By integrating OpenAI's GPT-3.5-turbo, the system delivers dynamic, personalized travel suggestions to help users make informed decisions.
- **Extensive API Integrations:** Data is pulled from multiple external sources, including TripAdvisor for detailed attraction information and OpenCage for geolocation, ensuring real-time and relevant travel data.
- **Interactive Daily Planning:** Users can build detailed day-by-day itineraries with the ability to add, update, and remove activities through an engaging, user-friendly interface.

### Complexity
This project demonstrates a high degree of technical complexity and meets course requirements by:
- **Utilizing Django for the Backend:** Django is employed to handle business logic, database management, user authentication, and REST API endpoints.
- **Integrating JavaScript for Enhanced User Experience:** Frontend dynamics, such as AJAX-based updates and interactive elements, are implemented using JavaScript to improve usability.
- **Implementing Multiple API Integrations:** External APIs (OpenAI, TripAdvisor, OpenCage) are integrated to provide advanced features and real-time data.
- **Ensuring Mobile Responsiveness:** The design is fully responsive, ensuring optimal functionality on both desktop and mobile devices.
- **Comprehensive Documentation and Error Handling:** Detailed code comments and thorough documentation ensure maintainability and robust error handling across the application.

## File Structure and Description

- **views.py:** Contains the logic for handling user requests, including authentication, travel planning, AI chat interactions, day planning, budgeting, document management, and external API integrations.
- **models.py:** Defines the database models representing users, travel plans, activities, documents, expenses, and shared travel plans.
- **forms.py:** Contains forms used for creating and editing travel plans, expenses, documents, and user profile settings.
- **templates/**: Holds the HTML templates for various pages, such as login, registration, dashboard, day planning, budget overview, document management, and map navigation.
- **static/**: Contains CSS, JavaScript, and image files that ensure a modern, mobile-friendly user interface.
- **requirements.txt:** Lists all the necessary Python packages (including Django, djangorestframework, decouple, openai, requests, and others) required for the project to run.

## How to Run the Application

- **1.** cd into webproject 
- **2.** install the requirements from requirements.txt
- **3.** Run "python manage.py runserver"
