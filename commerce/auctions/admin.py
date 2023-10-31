from django.contrib import admin
from .models import User, Listing, Bid, Comment, Category

class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "current_price")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("comment", "user", "listing")

class BidAdmin(admin.ModelAdmin):
    list_display = ("user", "bid", "listing")

# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category)