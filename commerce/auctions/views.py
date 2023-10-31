from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Category

class NewListingForm(forms.Form):
    title = forms.CharField(max_length=24, widget=forms.TextInput(
        attrs={"class": "form-control mb-3", "placeholder": "Title"}
    ))
    description = forms.CharField(max_length=100, widget=forms.Textarea(
        attrs={"class": "form-control mb-3", "placeholder": "Description", "rows": "4"}
    ))
    starting_bid = forms.DecimalField(max_digits=12, decimal_places=2, widget=forms.NumberInput(
        attrs={"class": "form-control mb-3", "placeholder": "Starting Bid: $(0.00)"}
    ))
    image_url = forms.URLField(required=False, widget=forms.URLInput(
        attrs={"class": "form-control mb-3", "placeholder": "(Optional) Image URL"}
    ))
    category = forms.CharField(max_length=24, required=False, widget=forms.TextInput(
        attrs={"class": "form-control mb-3", "placeholder": "(Optional) Category"}
    ))


class BidForm(forms.Form):
    bid = forms.DecimalField(max_digits=12, decimal_places=2, widget=forms.NumberInput(
        attrs={"class": "form-control mb-3", "placeholder": "Bid ($)"}
    ))

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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
                "message": "Invalid username and/or password.",
                "alert": "alert alert-danger"
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
                "message": "Passwords must match.",
                "alert": "alert alert-danger"
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
                "alert": "alert alert-danger"
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
    
@login_required(login_url="login")
def create_listing(request):
    if request.method == "POST":
        # Take in data from form
        form = NewListingForm(request.POST)

        # Check if form data is valid
        if form.is_valid():

            # Isolate all important info from form
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]

            # Check if optional info was added
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            
            # Add info to listing
            new_listing = Listing(owner=request.user, title=title, description=description, starting_bid=starting_bid, image_url=image_url, current_price=starting_bid)

            # Add new category (if category was inputted)
            if category != "":
                # Catch error if trying to create another category with the same name
                try:
                    new_category = Category(category=category)
                    new_category.save()
                except IntegrityError:
                    new_category = Category.objects.get(category=category)

                # Add new listing's category
                new_listing.category = new_category
                new_listing.save()
            
            else:
                new_listing.save()

            # For now return the same route with a message
            return render(request, "auctions/index.html", {
                "message": "Listing created!",
                "alert": "alert alert-success",
                "listings": Listing.objects.all()
            })

        else:
            return render(request, "auctions/create.html", {
                "message": "Make sure to fill all required fields!",
                "alert": "alert alert-danger",
                "form": NewListingForm()
            })

    else:
        return render(request, "auctions/create.html", {
            "form": NewListingForm()
        })
    

def listing_view(request, id):
    # Get the listing object
    listing = Listing.objects.get(pk=id)
    # Get the comments
    comments = Comment.objects.filter(listing=listing)

    # If user submitted a form
    if request.method == "POST":
        
        # Else check if all information on form are valid
        form = BidForm(request.POST)
        if form.is_valid():
            # Get bid
            bid = form.cleaned_data["bid"]

            # Check if this is the first bid
            if listing.bids.all().count() == 0:

                # Check if bid is at least greater than the starting bid
                if bid >= listing.starting_bid:
                    # Add bid
                    new_bid = Bid(user=request.user, listing=listing, bid=bid)
                    new_bid.save()

                    # Update listing current winner, current price, and number of bids
                    listing.current_price = bid
                    listing.current_winner = request.user

                    listing.save()

                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "form": BidForm(initial={"bid": listing.current_price}),
                        "message": "Bid placed!",
                        "alert": "alert alert-success",
                        "comments": comments
                    })
                    
                else:
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "form": BidForm(initial={"bid": listing.current_price}),
                        "message": "Your bid must be at least as large as the starting bid!",
                        "alert": "alert alert-danger",
                        "comments": comments
                    })
            

            # If not the first bid, check if bid is greater than current price
            if bid <= listing.current_price:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "form": BidForm(initial={"bid": listing.current_price}),
                    "message": "Your bid must be greater than any other bids that have been placed!",
                    "alert": "alert alert-danger",
                    "comments": comments
                })
            
            else:
                # Add bid
                new_bid = Bid(user=request.user, listing=listing, bid=bid)
                new_bid.save()

                # Update listing current winner, current price, and number of bids
                listing.current_price = bid
                listing.current_winner = request.user
                listing.save()

                return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "form": BidForm(initial={"bid": listing.current_price}),
                        "message": "Bid placed!",
                        "alert": "alert alert-success",
                        "comments": comments
                })

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "form": BidForm(initial={"bid": listing.current_price}),
        "comments": comments
    })


@login_required(login_url="login")
def close_listing(request, id):
    # If it was the owner closing the auction
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        comments = Comment.objects.filter(listing=listing)

        if listing.active:
            listing.active = False
            listing.save()

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "You closed this auction!",
                "alert": "alert alert-info",
                "comments": comments
            })

    # If method "GET", redirect to normal listing page
    return HttpResponseRedirect(reverse("listing", args=(id,)))


@login_required(login_url="login")
def add_comment(request, id):
    # Add comment to listing
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        comments = Comment.objects.filter(listing=listing)

        if request.POST["comment"] != "":
            comment = Comment(user=request.user, listing=listing, comment=request.POST["comment"])
            comment.save()

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "Comment added!",
                "form": BidForm(initial={"bid": listing.current_price}),
                "alert": "alert alert-success",
                "comments": comments
            })

        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "You need to type something to send a comment!",
                "form": BidForm(initial={"bid": listing.current_price}),
                "alert": "alert alert-danger",
                "comments": comments
            })
        
    return HttpResponseRedirect(reverse("listing", args=(id,)))


@login_required(login_url="login")
def watchlist_view(request):
    # Get user's watchlist
    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all()
    })


def categories_index(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category_view(request, id):
    category = Category.objects.get(pk=id)
    return render(request, "auctions/category.html", {
        "listings": Listing.objects.filter(category=category),
        "category": category,
        "n_items": len(category.listings.filter(active=True))
    })


@login_required(login_url="login")
def add_watchlist(request, id):
    # Get info for rendering template
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        comments = Comment.objects.filter(listing=listing)

        if listing not in request.user.watchlist.all():
            # Add listing to watchlist
            request.user.watchlist.add(listing)

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "Listing added to your watchlist!",
                "form": BidForm(initial={"bid": listing.current_price}),
                "alert": "alert alert-success",
                "comments": comments
            })
        else:
            # Remove listing from watchlist
            request.user.watchlist.remove(listing)

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "Listing removed from watchlist!",
                "form": BidForm(initial={"bid": listing.current_price}),
                "alert": "alert alert-success",
                "comments": comments
            })

 
    return HttpResponseRedirect(reverse("listing", args=(id,)))