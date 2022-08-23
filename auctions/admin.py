from django.contrib import admin
from auctions.models import Bid, Auction_listing, User, Comment, Category

# Register your models here.
admin.site.register(Bid)
admin.site.register(Auction_listing)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Category)
