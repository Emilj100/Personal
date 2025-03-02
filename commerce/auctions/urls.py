from django.urls import path
from django.conf import settings


from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("<int:auction_id>", views.listing, name="listing"),
    path("<int:auction_id>/bid", views.bid, name="bid"),
    path("<int:auction_id>/close", views.close, name="close"),
    path("<int:auction_id>/comment", views.comment, name="comment"),
    path("<int:auction_id>/add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<str:name>/category", views.category, name="category"),
    path("all_categories", views.all_categories, name="all_categories")
] 

