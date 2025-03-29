from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404

from decouple import config
import requests
import json
from rest_framework.decorators import api_view
from decouple import config
import openai
import datetime

from .forms import CreateTravelPlanForm, DocumentForm, ExpenseForm, TripForm, ProfileSettingsForm
from .models import User, TravelPlanShare, TravelPlan, Document, Expense, Activity

openai.api_key = config("OPENAI_API_KEY")

def index(request):
    return render(request, "tripnavigator/index.html")

def flight(request):
    return render(request, "tripnavigator/flight.html")

def hotel(request):
    return render(request, "tripnavigator/hotel.html")

def experience(request):
    return render(request, "tripnavigator/experience.html")

def ai_chat(request):
    return render(request, 'tripnavigator/ai_chat.html')

@require_POST
def get_ai_response(request):
    """
    Handles an AJAX request for an AI response.
    Receives the user's message, sends it to ChatGPT via the OpenAI API,
    and returns the generated response.
    """
    # Get the user's message from the POST data
    user_message = request.POST.get('message')
    if not user_message:
        # If no message is provided, return an error response with status 400
        return JsonResponse({"error": "No message provided."}, status=400)

    try:
        # Call the OpenAI API to generate a response using the GPT-3.5-turbo model
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful travel assistant for TripNavigator, an all-in-one platform that helps users plan and manage their entire trip. "
                        "TripNavigator offers flight search, hotel booking, day planning, budgeting, document storage, AI-based suggestions for experiences, "
                        "and more. Provide friendly, expert advice about traveling, flights, hotels, experiences, budgeting, day planning, or how to use "
                        "TripNavigator's features effectively. Always be concise, helpful, and polite."
                    )
                },
                # Include the user's message as part of the conversation
                {"role": "user", "content": user_message}
            ]
        )
        # Retrieve the AI's message from the API response
        ai_message = response.choices[0].message.content
        # Return the AI's message as a JSON response
        return JsonResponse({"message": ai_message})
    except Exception as e:
        # In case of an error, return an error message with status 500
        return JsonResponse({"error": str(e)}, status=500)

    
@login_required
def trip_overview(request, trip_id):
    # Retrieve the travel plan and check if the user has access (owner or shared)
    trip = get_object_or_404(TravelPlan, pk=trip_id)
    if trip.user != request.user:
        if not TravelPlanShare.objects.filter(travel_plan=trip, shared_email=request.user.email).exists():
            raise Http404("Trip not found.")
    
    # Get the first 5 activities as selected activities
    selected_activities = trip.activities.all()[:5]
    
    # Prepare context data and render the overview template
    context = {
        'trip': trip,
        'selected_activities': selected_activities,
        'opencage_api_key': config('OPENCAGE_API_KEY'),
    }
    return render(request, "tripnavigator/dashboard/overview.html", context)



def suggestions(request, trip_id):
    # Retrieve the travel plan and render the suggestions page.
    trip = get_object_or_404(TravelPlan, id=trip_id)
    return render(request, "tripnavigator/dashboard/suggestions.html", {"trip": trip})


@csrf_exempt
def generate_suggestions(request, trip_id):
    if request.method == "POST":
        # Retrieve trip details to build the API prompt.
        trip = get_object_or_404(TravelPlan, id=trip_id)
        destination = trip.destination
        start_date = trip.start_date
        end_date = trip.end_date
        category = trip.category
        description = trip.description or "No additional description provided."
        
        prompt = f"""
        Based on the following trip details:
        Destination: {destination}
        Start Date: {start_date}
        End Date: {end_date}
        Category: {category}
        Description: {description}

        Generate 6 travel activity suggestions in JSON format.
        Each suggestion should include:
        - title
        - description
        - extra (e.g. price or rating)
        - icon (Bootstrap Icons class, e.g. 'bi-boat', 'bi-palette')
        - color (Bootstrap color name, e.g. 'danger', 'primary', etc.)
        Return only a valid JSON array with 6 objects and no additional text.
        """
        
        try:
            # Call the OpenAI API with the prompt and parse the JSON response.
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
            )
            content = response.choices[0].message.content.strip()
            suggestions = json.loads(content)
        except Exception as e:
            return JsonResponse({"suggestions": []})
        
        return JsonResponse({"suggestions": suggestions})


@csrf_exempt
def add_suggestion_to_plan(request, trip_id):
    """
    Create a new unassigned activity using the suggested title.
    """
    if request.method == "POST":
        trip = get_object_or_404(TravelPlan, id=trip_id)
        suggestion_title = request.POST.get("title")
        if not suggestion_title:
            return JsonResponse({"success": False, "error": "No title provided."}, status=400)
        try:
            # Create a new activity with no assigned date.
            new_activity = Activity.objects.create(
                travel_plan=trip,
                title=suggestion_title,
                date=None
            )
            return JsonResponse({"success": True, "activity_id": new_activity.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False}, status=400)




def day_planner(request, travel_plan_id):
    # Retrieve the travel plan by ID; return 404 if not found.
    travel_plan = get_object_or_404(TravelPlan, pk=travel_plan_id)
    
    # Create a list of dates for the timeline based on the travel plan dates.
    timeline_days = []
    if travel_plan.start_date and travel_plan.end_date:
        delta = (travel_plan.end_date - travel_plan.start_date).days
        timeline_days = [travel_plan.start_date + datetime.timedelta(days=i) for i in range(delta + 1)]
    
    # Get all activities for the travel plan and separate them into assigned and unassigned.
    all_activities = Activity.objects.filter(travel_plan=travel_plan)
    assigned_activities = all_activities.filter(date__isnull=False)
    unassigned_activities = all_activities.filter(date__isnull=True)
    
    # Organize assigned activities by date.
    activities_by_date = {}
    for activity in assigned_activities:
        activities_by_date.setdefault(activity.date, []).append(activity)
    
    # Build timeline data: each day with its list of activities.
    timeline_data = []
    for d in timeline_days:
        timeline_data.append({
            'date': d,
            'activities': activities_by_date.get(d, [])
        })
    
    # Handle new activity creation via POST request.
    if request.method == "POST":
        activity_name = request.POST.get('activityName')
        activity_date_str = request.POST.get('activityDay')
        start_time = request.POST.get('activityStartTime') or None
        end_time = request.POST.get('activityEndTime') or None
        address = request.POST.get('activityAddress') or ""
        
        # Parse the date if provided.
        chosen_date = parse_date(activity_date_str) if activity_date_str else None
        
        # Create the new activity.
        new_activity = Activity.objects.create(
            travel_plan=travel_plan,
            date=chosen_date,
            title=activity_name,
            start_time=start_time,
            end_time=end_time,
            address=address
        )
        # Return JSON response for AJAX requests.
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({"success": True, "activity_id": new_activity.id})
        else:
            return HttpResponseRedirect(reverse('day-planner', kwargs={'travel_plan_id': travel_plan_id}))
    
    # Prepare context for rendering the day planner template.
    context = {
        'travel_plan': travel_plan,
        'trip': travel_plan,
        'timeline_days': timeline_days,
        'timeline_data': timeline_data,
        'unassigned_activities': unassigned_activities,
    }
    return render(request, "tripnavigator/dashboard/day-planner.html", context)


def update_activity_date(request):
    """Update an activity's date via an AJAX POST request."""
    if request.method == "POST":
        activity_id = request.POST.get("activity_id")
        date_str = request.POST.get("date")
        activity = get_object_or_404(Activity, pk=activity_id)
        if date_str:
            try:
                # Parse the date string in the expected format.
                parsed_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                activity.date = parsed_date
                activity.save()
                return JsonResponse({"success": True})
            except ValueError:
                return JsonResponse({"success": False, "error": "Invalid date format."}, status=400)
        else:
            # If no date provided, unassign the activity.
            activity.date = None
            activity.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


def delete_activity(request):
    """Delete an activity via an AJAX POST request."""
    if request.method == "POST":
        activity_id = request.POST.get("activity_id")
        try:
            activity = Activity.objects.get(pk=activity_id)
            activity.delete()
            return JsonResponse({"success": True})
        except Activity.DoesNotExist:
            return JsonResponse({"success": False, "error": "Activity not found."}, status=404)
    return JsonResponse({"success": False}, status=400)





@login_required
def documents(request, trip_id):
    # Retrieve the travel plan; redirect if not found or if the user doesn't have access.
    trip = get_object_or_404(TravelPlan, pk=trip_id)
    if trip.user != request.user:
        if not TravelPlanShare.objects.filter(travel_plan=trip, shared_email=request.user.email).exists():
            return HttpResponseRedirect(reverse("trip-planner"))
    
    # Get all documents for this trip, ordered by most recent upload.
    docs = Document.objects.filter(travel_plan=trip).order_by('-uploaded_at')
    
    # Initialize an empty form for uploading new documents.
    form = DocumentForm()
    
    context = {
         'trip': trip,
         'documents': docs,
         'form': form,
    }
    return render(request, "tripnavigator/dashboard/documents.html", context)


@login_required
def upload_document(request, trip_id):
    # Retrieve the travel plan and check user access.
    trip = get_object_or_404(TravelPlan, pk=trip_id)
    if trip.user != request.user:
        if not TravelPlanShare.objects.filter(travel_plan=trip, shared_email=request.user.email).exists():
            raise Http404("Trip not found.")
    
    if request.method == "POST":
        # Process the submitted document upload form.
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.travel_plan = trip
            doc.save()
            messages.success(request, "Document uploaded successfully!")
            return HttpResponseRedirect(reverse("documents", args=[trip.id]))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DocumentForm()
    
    context = {
        "form": form,
        "trip": trip,
    }
    return render(request, "tripnavigator/dashboard/upload_document.html", context)



def budget(request, trip_id):
    # Retrieve the travel plan and its expenses
    trip = get_object_or_404(TravelPlan, id=trip_id)
    expenses = Expense.objects.filter(travel_plan=trip).order_by('-date')

    # Calculate budget statistics
    total_budget = trip.budget if hasattr(trip, 'budget') else 0
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    spent_percentage = round((total_spent / total_budget) * 100, 2) if total_budget else 0
    remaining = total_budget - total_spent

    # Prepare category data for charts
    category_data = (
        expenses
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    category_labels = [item['category'] for item in category_data]
    category_totals = [float(item['total']) for item in category_data]

    # Process expense form submission
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            new_expense = form.save(commit=False)
            new_expense.travel_plan = trip
            new_expense.save()
            return HttpResponseRedirect(reverse('budget', kwargs={'trip_id': trip.id}))
    else:
        form = ExpenseForm()

    # Render the budget dashboard template with all calculated data
    return render(request, "tripnavigator/dashboard/budget.html", {
        "trip": trip,
        "expenses": expenses,
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining": remaining,
        "spent_percentage": spent_percentage,
        "category_labels": json.dumps(category_labels),
        "category_totals": json.dumps(category_totals),
        "form": form,
    })

def delete_expense(request, trip_id, expense_id):
    # Retrieve the specific expense and delete it on POST request
    expense = get_object_or_404(Expense, id=expense_id, travel_plan_id=trip_id)
    if request.method == 'POST':
        expense.delete()
    return HttpResponseRedirect(reverse('budget', kwargs={'trip_id': trip_id}))



OPENCAGE_API_KEY = config('OPENCAGE_API_KEY')

def map_navigation(request, trip_id):
    # Retrieve the travel plan using the provided trip_id; 404 if not found.
    travel_plan = get_object_or_404(TravelPlan, pk=trip_id)
    
    # Get all activities for the travel plan, ordered by date and start time.
    all_activities = Activity.objects.filter(travel_plan=travel_plan).order_by('date', 'start_time')
    
    # Filter activities for today.
    today = datetime.date.today()
    todays_activities = all_activities.filter(date=today)
    
    # Prepare context data to pass to the map navigation template.
    context = {
        'travel_plan': travel_plan,
        'trip': travel_plan,  # Alias for compatibility in templates.
        'todays_activities': todays_activities,
        'all_activities': all_activities,
        'opencage_api_key': OPENCAGE_API_KEY,  # Pass the API key for geocoding.
    }
    return render(request, "tripnavigator/dashboard/map-navigation.html", context)


def update_hotel_address(request, travel_plan_id):
    # This view updates the hotel address via an AJAX POST request.
    if request.method == 'POST':
        # Ensure the travel plan belongs to the current user.
        travel_plan = get_object_or_404(TravelPlan, id=travel_plan_id, user=request.user)
        try:
            data = json.loads(request.body)
            new_address = data.get('hotel_address', '').strip()
            if new_address:
                travel_plan.hotel_address = new_address
                travel_plan.save()
                return JsonResponse({'message': 'Hotel address has been updated.'}, status=200)
            else:
                return JsonResponse({'error': 'Please enter a valid address.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)


@login_required
def settings(request, trip_id):
    # Retrieve the travel plan for the given trip_id or return a 404 if not found.
    trip = get_object_or_404(TravelPlan, id=trip_id)
    
    if request.method == "POST":
        # Bind the submitted data and files to the form using the existing trip instance.
        form = TripForm(request.POST, request.FILES, instance=trip)
        if form.is_valid():
            # Save the updated trip settings.
            form.save()
            messages.success(request, "Trip settings updated successfully.")
            # Redirect to the settings page to reflect changes.
            return HttpResponseRedirect(reverse("settings", kwargs={"trip_id": trip.id}))
    else:
        # Initialize the form with the current trip settings.
        form = TripForm(instance=trip)
    
    # Render the settings template with the trip and form context.
    return render(request, "tripnavigator/dashboard/settings.html", {
        "trip": trip,
        "form": form,
    })

def trip_planner(request):
    # Retrieve all travel plans created by the current user
    my_trips = request.user.travel_plans.all()
    # Retrieve travel plans that have been shared with the user via their email
    shared_trips = TravelPlanShare.objects.filter(shared_email=request.user.email)

    # Render the trip planner template with the user's trips and shared trips
    return render(request, "tripnavigator/trip-planner.html", {
        "my_trips": my_trips,
        "shared_trips": shared_trips
    })




def create_travelplan(request):
    if request.method == "POST":
        # Process form submission to create a new travel plan
        form = CreateTravelPlanForm(request.POST, request.FILES)
        if form.is_valid():
            travelplan = form.save(commit=False)
            travelplan.user = request.user
            travelplan.save()
            
            # Handle optional share_email field to share the travel plan
            share_email = form.cleaned_data.get("share_email")
            if share_email:
                shared_name = travelplan.user.first_name or travelplan.user.email
                TravelPlanShare.objects.create(
                    travel_plan=travelplan,
                    shared_email=share_email,
                    shared_name=shared_name
                )
            
            return HttpResponseRedirect(reverse("trip-planner"))
    else:
        form = CreateTravelPlanForm()
    
    # Render the create travel plan page with the form
    return render(request, "tripnavigator/create-travelplan.html", {
        "form": form
    })



@login_required
def profile_settings(request):
    # Get the current user
    user = request.user

    if request.method == "POST":
        # Process form submission and update user details
        form = ProfileSettingsForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get("new_password")
            if new_password:
                user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Profile updated successfully.")
            return HttpResponseRedirect(reverse("profile_settings"))
    else:
        form = ProfileSettingsForm(instance=user)
    
    # Render the profile settings page with the form
    return render(request, "tripnavigator/profile_settings.html", {
        "form": form,
    })


# Retrieve API keys and base configuration for TripAdvisor API requests
API_KEY = config("TRIPADVISOR_API_KEY")
BASE_URL = "https://api.content.tripadvisor.com/api/v1"
REFERER_DOMAIN = config("TRIPADVISOR_REFERER_DOMAIN")

# Set up HTTP headers required for the TripAdvisor API
HEADERS = {
    "accept": "application/json",
    "Referer": REFERER_DOMAIN
}

# Function to search for locations (attractions) in a given city.
def location_search(city, category="attractions", language="en"):
    url = f"{BASE_URL}/location/search"
    params = {
        "searchQuery": city,
        "category": category,
        "language": language,
        "key": API_KEY
    }
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

# Function to get detailed information for a specific location using its ID.
def location_details(location_id, language="en", currency="USD"):
    url = f"{BASE_URL}/location/{location_id}/details"
    params = {
        "language": language,
        "currency": currency,
        "key": API_KEY
    }
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

# Function to fetch photos for a specific location.
def location_photos(location_id, language="en"):
    url = f"{BASE_URL}/location/{location_id}/photos"
    params = {
        "language": language,
        "key": API_KEY
    }
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

@api_view(['GET'])
def experience_search(request):
    """
    API endpoint that receives a 'city' parameter and returns a list of attractions.
    For each attraction, additional details and a photo URL are fetched,
    and a 'web_url' is included for a "Learn more" link.
    """
    # Get the 'city' parameter from the query string
    city = request.GET.get("city")
    if not city:
        return JsonResponse({"error": "City parameter is required."}, status=400)
    
    # Search for attractions in the specified city
    search_result = location_search(city)
    if not search_result or "data" not in search_result:
        return JsonResponse({"error": "No attractions found or an error occurred."}, status=500)
    
    attractions = search_result["data"]
    enhanced_attractions = []
    
    # Process each attraction to enrich with details and photos
    for attraction in attractions:
        location_id = attraction.get("location_id")
        if not location_id:
            continue  # Skip attractions with no location_id
        
        # Fetch detailed information and photos for this attraction
        details = location_details(location_id)
        photos = location_photos(location_id)
        photo_url = None
        
        # Try to extract the URL of the first available photo
        if photos and "data" in photos and len(photos["data"]) > 0:
            try:
                photo_url = photos["data"][0]["images"]["original"]["url"]
            except KeyError:
                photo_url = None
        
        # Extract description and web URL from the detailed info
        description = details.get("description", "") if details else ""
        web_url = details.get("web_url", "") if details else ""
        
        # Build an enhanced attraction object with extra fields
        enhanced_attraction = {
            "name": attraction.get("name"),
            "details": description,
            "photo_url": photo_url,
            "web_url": web_url
        }
        enhanced_attractions.append(enhanced_attraction)
    
    # Return the list of enhanced attractions as a JSON response
    return JsonResponse({"data": enhanced_attractions})


def login_view(request):
    if request.method == "POST":
        # Retrieve credentials from POST data and attempt authentication
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Log the user in and redirect to the homepage
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            # Render the login page with an error message
            return render(request, "tripnavigator/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        # Render the login page for GET requests
        return render(request, "tripnavigator/login.html")


def logout_view(request):
    # Log the user out and redirect to the homepage
    logout(request)
    return HttpResponseRedirect(reverse("index"))



def register(request):
    if request.method == "POST":
        # Retrieve registration data from the POST request
        email = request.POST["email"]
        first_name = request.POST.get("first_name", "").strip()
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Check if password and confirmation match
        if password != confirmation:
            return render(request, "tripnavigator/register.html", {
                "message": "Passwords must match."
            })

        try:
            # Create and save the new user
            user = User.objects.create_user(email=email, password=password, username=email, first_name=first_name)
            user.save()
        except IntegrityError:
            # Handle duplicate registration attempts
            return render(request, "tripnavigator/register.html", {
                "message": "Email is already registered."
            })
        # Log the user in and redirect to the homepage
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "tripnavigator/register.html")

