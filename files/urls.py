from django.urls import path
from . import views

app_name = "files"
urlpatterns = [
    path("", views.drive, name="drive"),
    path("new_file/", views.new_file, name="new_file"),
]
