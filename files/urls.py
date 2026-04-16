from django.urls import path
from . import views

app_name = "files"
urlpatterns = [
    path("", views.drive, name="drive"),
    path("upload_files/", views.upload_files, name="upload_files"),
    path("upload_dir/", views.upload_dir, name="upload_dir"),
    path("download/<int:pk>/", views.download, name="download"),
    path("delete/<int:pk>/", views.delete, name="delete"),
]
