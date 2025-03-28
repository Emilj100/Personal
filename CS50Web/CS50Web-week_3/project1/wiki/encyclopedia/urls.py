from django.urls import path

from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("search", views.search, name="search"),
    path("new_page", views.new_page, name="new_page"),
    path("wiki/<str:title>/edit", views.edit_page, name="edit_page"),
    path("random_page", views.random_page, name="random_page")
    

]
