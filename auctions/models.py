from django.contrib.auth.models import AbstractUser
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.category}"

    class Meta:
        ordering = ['category']


class Auction_listing(models.Model):
    item_name = models.CharField(max_length=50)
    item_description = models.TextField(max_length=500)
    item_image = models.CharField(blank=True, max_length=200)
    item_initial_bid = models.DecimalField(
        blank=False, default=0.00, decimal_places=2, max_digits=14)
    item_current_bid = models.DecimalField(
        blank=True, null=True, default=0.00, decimal_places=2, max_digits=14)
    item_isactive = models.BooleanField(default=True)
    item_created = models.DateTimeField(auto_now_add=True)
    item_category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True, related_name="auction_category")
    item_poster = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_listings")
    item_buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="buyer", blank=True, null=True)
    watchlist = models.ManyToManyField(
        User, blank=True, related_name="watchlist")

    def bid_count(self):
        return self.auctionbids.all().count()

    def last_bid(self):
        try:
            return self.auctionbids.order_by('-date').first().date
        except AttributeError:
            return "No bids yet"

    def __str__(self):
        return f"{self.item_name}, Starting Bid: ${self.item_initial_bid}, Current Bid: ${self.item_current_bid} Created: {self.item_created}"


class Bid(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bidsuser")
    auctions = models.ForeignKey(
        Auction_listing, on_delete=models.CASCADE, related_name="auctionbids")
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(
        blank=True, null=True, default=0.00, decimal_places=2, max_digits=14)

    def __str__(self):
        return f"{self.auctions} | {self.date}"


class Comment(models.Model):
    comment_name = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="commentname")
    comment_content = models.TextField(max_length=2000)
    comment_timestamp = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey(
        Auction_listing, on_delete=models.CASCADE, related_name="commentlisting")

    def __str__(self):
        return f"{self.comment_content} | {self.auction}"

    class Meta:
        ordering = ['-comment_timestamp']
