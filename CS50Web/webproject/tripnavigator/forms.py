# forms.py
from django import forms
from .models import TravelPlan, Document, Expense, User

class CreateTravelPlanForm(forms.ModelForm):
    share_email = forms.EmailField(
        required=False,
        label="Share with Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter recipient email'})
    )
    
    class Meta:
        model = TravelPlan
        fields = [
            'title',
            'destination',
            'image',
            'start_date',
            'end_date',
            'category',
            'budget',
            'description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter trip title'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Paris, France'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter budget in dollars'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional details'}),
        }
        
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter document title'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'amount', 'category', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount in dollars'}),
            'category': forms.Select(choices=[
                ('Food', 'Food'),
                ('Transport', 'Transport'),
                ('Accommodation', 'Accommodation'),
                ('Entertainment', 'Entertainment'),
                ('Other', 'Other')
            ], attrs={'class': 'form-select'}),
            'note': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter note (optional)'}),
        }

class TripForm(forms.ModelForm):
    class Meta:
        model = TravelPlan
        fields = ["title", "destination", "start_date", "end_date", "category", "budget", "description", "image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "destination": forms.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "budget": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

class ProfileSettingsForm(forms.ModelForm):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="New Password"
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }