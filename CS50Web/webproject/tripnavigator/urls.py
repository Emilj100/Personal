from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("flight", views.flight, name="flight"),
    path("hotel", views.hotel, name="hotel"),
    path("experience", views.experience, name="experience"),
    path("api/experience_search/", views.experience_search, name="experience_search"),
    path("trip-planner", views.trip_planner, name="trip-planner"),
    path('create/', views.create_travelplan, name='create_travelplan'),
    path('overview/<int:trip_id>/', views.trip_overview, name='overview'),
    path('travel-plan/<int:travel_plan_id>/day-planner/', views.day_planner, name='day-planner'),
    path('update-activity-date/', views.update_activity_date, name='update-activity-date'),
    path('delete-activity/', views.delete_activity, name='delete-activity'),
    path('documents/<int:trip_id>/', views.documents, name='documents'),
    path('upload_document/<int:trip_id>/', views.upload_document, name='upload_document'),
    path('budget/<int:trip_id>/', views.budget, name='budget'),
    path('budget/<int:trip_id>/delete-expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('travel-plan/<int:trip_id>/map-navigation/', views.map_navigation, name='map-navigation'),
    path('travel_plan/<int:travel_plan_id>/update-hotel-address/', views.update_hotel_address, name='update_hotel_address'),
    path('settings/<int:trip_id>/', views.settings, name='settings'),
    path('suggestions/<int:trip_id>/', views.suggestions, name='suggestions'),
    path("ai/generate/<int:trip_id>/", views.generate_suggestions, name="generate_suggestions"),
    path('ai/add-to-plan/<int:trip_id>/', views.add_suggestion_to_plan, name='add_suggestion_to_plan'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('ai/', views.ai_chat, name='ai_chat'),
    path('ai/get-response/', views.get_ai_response, name='get_ai_response'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
