from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("listings/<int:id>/", views.listing_view, name="listing"),
    path("listings/<int:id>/close", views.close_listing, name="close_listing"),
    path("listings/<int:id>/comment", views.add_comment, name="comment"),
    path("listings/<int:id>/add", views.add_watchlist, name="add"),
    path("watchlist/", views.watchlist_view, name="watchlist"),
    path("categories/", views.categories_index, name="categories"),
    path("categories/<int:id>", views.category_view, name="category")
]
