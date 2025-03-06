from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from .models import User, Auction, Bid, Comment, Category

class Create(forms.Form):
    title = forms.CharField(label="Title", max_length=64)
    description = forms.CharField()
    price = forms.DecimalField(max_digits=19, decimal_places=2)
    image = forms.ImageField(required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Select a category", required=False)

class Make_bid(forms.Form):
    bid = forms.DecimalField(max_digits=19, decimal_places=2)

class Comments(forms.Form):
    comment = forms.CharField(label="Comment")

def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.exclude(is_active=False).all()
    })

def listing(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
    comments = Comment.objects.filter(auction=auction)

    if request.user == auction.the_creator and auction.is_active:
        close = True
    else:
        close = False

    if request.user == auction.winner and not auction.is_active:
        winner = True
    else:
        winner = False

    if auction in request.user.watchlist.all():
        in_watchlist = True
    else:
        in_watchlist = False

    return render(request, "auctions/listing.html", {
        "auction": auction,
        "bid": highest_bid,
        "form": Make_bid(),
        "comment_form": Comments(),
        "close": close,
        "winner": winner,
        "comments": comments,
        "watchlist": in_watchlist
    })

def category(request, name):
    category_object = Category.objects.get(name=name)
    auctions = Auction.objects.filter(category=category_object, is_active=True)
    return render(request, "auctions/category.html", {
        "auctions": auctions,
        "category": category_object
    })


def all_categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/all_categories.html", {
        "categories": categories
    })

@login_required
def watchlist(request):
    auction = request.user.watchlist.all()

    return render(request, "auctions/watchlist.html", {
        "auctions": auction
    })

@login_required
def add_to_watchlist(request, auction_id):
    if request.method == "POST":
        auction = Auction.objects.get(pk=auction_id)

        if auction in request.user.watchlist.all():
            request.user.watchlist.remove(auction)
            messages.success(request, "Listing removed from your watchlist.")
            return HttpResponseRedirect(reverse("listing", args=[auction_id]))
        else:
            request.user.watchlist.add(auction)
            messages.success(request, "Listing added to your watchlist.")
            return HttpResponseRedirect(reverse("listing", args=[auction_id]))

        
@login_required
def comment(request, auction_id):
    if request.method == "POST":
            auction = Auction.objects.get(pk=auction_id)
            form = Comments(request.POST)
            if form.is_valid():
                comment = form.cleaned_data["comment"]

            else:
                messages.warning(request, "Something went wrong")
                return HttpResponseRedirect(reverse("listing", args=[auction_id]))
            
            Comment.objects.create(
                comment=comment,
                commentator=request.user,
                auction=auction
            )
            return HttpResponseRedirect(reverse("listing", args=[auction_id]))

        
@login_required
def close(request, auction_id):
    if request.method == "POST":
        auction = Auction.objects.get(pk=auction_id)
        highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
        
        if highest_bid:
            auction.winner = highest_bid.bidder
        
        auction.is_active = False
        auction.save()
        
        return HttpResponseRedirect(reverse("listing", args=[auction_id]))


@login_required
def bid(request, auction_id):
    if request.method == "POST":
        form = Make_bid(request.POST)
        if form.is_valid():
            bid_value = form.cleaned_data["bid"]
            auction = Auction.objects.get(pk=auction_id)
            current_bid_object = Bid.objects.filter(auction=auction).order_by('-amount').first()

            if not current_bid_object:
                if bid_value < auction.startbid:
                    messages.warning(request, "Your bid must be at least the starting bid.")
                    return HttpResponseRedirect(reverse("listing", args=[auction_id]))
            else:
                if bid_value <= current_bid_object.amount:
                    messages.warning(request, "Please place a higher bid than the current bid.")
                    return HttpResponseRedirect(reverse("listing", args=[auction_id]))
                    
            Bid.objects.create(
                amount=bid_value,
                bidder=request.user,
                auction=auction
            )
            messages.success(request, "Your bid was placed")
            return HttpResponseRedirect(reverse("listing", args=[auction_id]))
        else:
            return render(request, "auctions/listing.html", {"form": form})



@login_required
def create(request):
    if request.method == "POST":
        form = Create(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
        
        Auction.objects.create(
        title=title,
        description=description,
        startbid=price,
        image=image,
        category=category,
        the_creator=request.user
        )
        messages.success(request, "Your auction was successfully created!")
        return HttpResponseRedirect(reverse("index"))


    return render(request, "auctions/create.html", {
        "form": Create()
    })

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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
