from django.db import models
from django.contrib.auth.models import AbstractUser


# VIGTIGT! Dette er ikke nødvendigvis de endelige modeller. Dette er blot som start hvor vi altid kan ændre på det med tiden

# 1. UserProfile
class User(AbstractUser):
    # Vi beholder username-feltet, men vi tvinger det til at være det samme som email
    email = models.EmailField('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # username kræves ikke

    def __str__(self):
        return self.email

 
CATEGORY_CHOICES = (
    ('none', 'None'),
    ('family', 'Family Trip'),
    ('romantic', 'Romantic Holiday'),
    ('adventure', 'Adventure Trip'),
    ('cultural', 'Cultural Journey'),
    ('wellness', 'Wellness & Spa'),
    ('road', 'Road Trip'),
    ('budget', 'Budget Travel'),
    ('luxury', 'Luxury Escape'),
    ('nature', 'Nature & Outdoor'),
    ('historical', 'Historical Tour'),
    ('other', 'Other'),
)


class TravelPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='travel_plans')
    title = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    image = models.ImageField(upload_to='trip_planner_images/', blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default=None)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    hotel_address = models.CharField(max_length=255, null=True, blank=True)  # New field for hotel address
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    
    
class TravelPlanShare(models.Model):
    travel_plan = models.ForeignKey(TravelPlan, on_delete=models.CASCADE, related_name='shares')
    shared_email = models.EmailField()
    shared_name = models.CharField(max_length=255)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shared with {self.shared_name} ({self.shared_email})"
    
# I models.py
class Document(models.Model):
    travel_plan = models.ForeignKey('TravelPlan', on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Expense(models.Model):
    travel_plan = models.ForeignKey(TravelPlan, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)  # eller med choices
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - ${self.amount}"
    

class Activity(models.Model):
    travel_plan = models.ForeignKey(TravelPlan, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    date = models.DateField(null=True, blank=True)  # Gemmer datoen direkte
    title = models.CharField(max_length=255)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title