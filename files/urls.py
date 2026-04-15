from django.urls import path
from . import views

app_name = "files"
urlpatterns = [
    path("", views.drive, name="drive"),
    path("upload/", views.new_file, name="new_file"),
    path("download/<int:pk>/", views.download_file, name="download_file"),
    path("delete/<int:pk>/", views.delete_file, name="delete_file"),
]
