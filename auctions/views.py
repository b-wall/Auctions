from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm, NumberInput, TextInput, Select, Textarea
from django.contrib import messages


from .models import Auction_listing, Category, User, Bid, Comment

# ModelForms


class NewListing(ModelForm):
    """Form to make a new listing"""
    class Meta:
        model = Auction_listing
        fields = ['item_name', 'item_description',
                  'item_image', 'item_initial_bid', 'item_category']
        widgets = {
            'item_name': TextInput(attrs={'class': 'form-control'}),
            'item_description': TextInput(attrs={'class': 'form-control'}),
            'item_image': TextInput(attrs={'class': 'form-control'}),
            'item_initial_bid': TextInput(attrs={'class': 'form-control'}),
            'item_category': Select(attrs={'class': 'form-control'})
        }


class BidOffer(ModelForm):
    """Form to create a bid on an item"""
    class Meta:
        model = Bid
        fields = ('amount', )
        widgets = {
            'amount': NumberInput(attrs={'class': 'form-control'})
        }
        labels = {
            'amount': ''
        }


class NewComment(ModelForm):
    """Form to create comments"""
    class Meta:
        model = Comment
        fields = ('comment_content', )
        widgets = {
            'comment_content': Textarea(attrs={'class': 'form-control', 'rows': '2', 'placeholder': 'Leave a comment'})
        }
        labels = {
            'comment_content': ''
        }

# Views


def index(request):
    """Displays all the current auction listings to user"""
    objects_list = Auction_listing.objects.all()
    return render(request, "auctions/index.html", {
        'objects': objects_list
    })


def login_view(request):
    """Handles login and authentication"""
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
    """Logs the user out"""
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """Registers a new user"""
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


@login_required
def new_auction(request):
    """Create a new auction listing"""
    # Display form
    if request.method == "GET":
        listing_form = NewListing()
        return render(request, "auctions/newlisting.html", {
            'listing_form': listing_form
        })
    # Post form and save data
    elif request.method == "POST":
        listing_form = NewListing(request.POST)
        if listing_form.is_valid():
            listing_object = listing_form.save(commit=False)
            listing_object.item_poster = request.user
            listing_form.save()

        return HttpResponseRedirect(reverse("index"))


def listing(request, item_id):
    """View and bid on a listing"""
    if request.method == "GET":
        # Display listing information, bid and comment form to user
        bidform = BidOffer()
        item_objects = Auction_listing.objects.filter(id=item_id)
        comments = Comment.objects.filter(auction_id=item_id)
        commentform = NewComment()
        return render(request, "auctions/listing.html", {"id": item_id, "auction_objects": item_objects, "bidform": bidform, "commentform": commentform, "comments": comments})
    if request.method == "POST":
        # Allow user to bid on item
        offer = BidOffer(request.POST)
        # Error checking
        if offer.is_valid():
            auction = Auction_listing.objects.get(id=item_id)
            # Make sure user is not the creator of the listing
            if auction.item_poster != request.user:
                processoffer = offer.save(commit=False)
                # Check to make sure the new bid offer is greater than the current bid
                if auction.item_current_bid == 0:
                    auction.item_current_bid = auction.item_initial_bid
                if auction.item_initial_bid and auction.item_current_bid < processoffer.amount:
                    # Save new data to database
                    auction.item_current_bid = processoffer.amount
                    auction.save()
                    processoffer.user = request.user
                    processoffer.auctions = auction
                    processoffer.save()
                    # Add item to users watchlist automatically if they successfully bid
                    if request.user not in auction.watchlist.all():
                        auction.watchlist.add(request.user)
                        messages.success(
                            request, "You've placed a bid! Listing added to your <strong>watchlist</strong>.")
                    elif request.user in auction.watchlist.all():
                        messages.success(
                            request, "You've placed a bid!")
                else:
                    messages.error(
                        request, 'Error: You must bid higher than the current value!')
                    return HttpResponseRedirect(reverse("listing", args=[item_id]))
            else:
                messages.error(
                    request, "Error: You can't bid on your own item!")
                return HttpResponseRedirect(reverse("listing", args=[item_id]))
    return HttpResponseRedirect(reverse("listing", args=[item_id]))


@login_required
def handle_watchlist(request, item_id):
    """Controls the watchlist functionality"""
    if request.method == "POST":
        listing = Auction_listing.objects.get(id=item_id)
        # check if exists, if not add
        if request.user in listing.watchlist.all():
            listing.watchlist.remove(request.user)
        else:
            # if exists, delete
            listing.watchlist.add(request.user)
        # redirect based on current url
        watchlist_url = request.META['HTTP_REFERER']
        if watchlist_url == request.build_absolute_uri(reverse("watchlist")):
            return HttpResponseRedirect(reverse("watchlist"))
        else:
            return HttpResponseRedirect(reverse("listing", args=[item_id]))


@login_required
def watchlist(request):
    """Displays the watchlist"""
    if request.method == "GET":
        # Retrieve the listing information
        listings = Auction_listing.objects.all()

        return render(request, "auctions/watchlist.html", {"listings": listings})
    if request.method == "POST":
        # redirect to the listing clicked form the watchlist
        return HttpResponseRedirect(reverse("watchlist"))


@login_required
def close_listing(request, item_id):
    """Closes the listing if you are the owner"""
    if request.method == "POST":
        # Retrieve the specific listing
        listing = Auction_listing.objects.get(id=item_id)
        # Checks if the listing is open or closed
        if listing.item_isactive == True:
            # Checks if the user is the creator of the listing
            if request.user == listing.item_poster:
                # Handle closing of the auction and assign the winner to the database
                listing.item_isactive = False
                buyer = Bid.objects.filter(auctions=listing).last()
                listing.item_buyer = buyer.user
                listing.save()
        return HttpResponseRedirect(reverse("listing", args=[item_id]))


@login_required
def handle_comment(request, item_id):
    """Handles posting of comments"""
    if request.method == "POST":
        # Obtains the listing information and the comment content
        listing = Auction_listing.objects.get(id=item_id)
        comment = NewComment(request.POST)
        # Checks validity of information
        if comment.is_valid():
            # Saves comment to listing
            processcomment = comment.save(commit=False)
            processcomment.comment_name = request.user
            processcomment.auction = listing
            processcomment.save()
            messages.success(request, "Comment posted")
            return HttpResponseRedirect(reverse("listing", args=[item_id]))
        else:
            messages.error(
                request, "Error: Please check that your comment is valid.")
    return HttpResponseRedirect(reverse("listing", args=[item_id]))


def categories(request):
    """Display categories for user"""
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/categories.html", {"categories": categories})


def handle_category(request, cat_id):
    """Show listings by category"""
    listings = Auction_listing.objects.filter(item_category__pk=cat_id)
    return render(request, "auctions/category.html", {"listings": listings})
