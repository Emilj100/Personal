from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages

from .models import User, Post, Like, Follow

class Create(forms.Form):
    text = forms.CharField(label="Text")


def index(request):
    return render(request, "network/index.html", {
        "posts": Post.objects.all().order_by("-created_at"),
        "form": Create()
    })

def create(request):
    if request.method == "POST":
        form = Create(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
        else:
            messages.warning(request, "Something went wrong")
            return HttpResponseRedirect(reverse("index"))

        Post.objects.create(
            the_creator=request.user,
            text=text
        )

        return HttpResponseRedirect(reverse("index"))

def profile(request, username):
    


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
