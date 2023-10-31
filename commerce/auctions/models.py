from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", blank=True)
    pass


class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=24)
    description = models.CharField(max_length=100)
    starting_bid = models.DecimalField(max_digits=12, decimal_places=2)
    current_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_winner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True, null=True, related_name="listings")

    active = models.BooleanField(default=True)

    image_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} by {self.owner}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Bid: ${self.bid} by {self.user} on {self.listing.title}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by: {self.user} on Item: '{self.listing.title}'"


class Category(models.Model):
    category = models.CharField(max_length=24, unique=True)

    def __str__(self):
        return f"{self.category}"
