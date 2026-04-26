from django.urls import path
from . import views

app_name = "files"
urlpatterns = [
    path("", views.drive, name="drive"),
    path('drive/<int:folder_id>/', views.drive, name='drive_folder'),
    path("upload/files/", views.upload_files, name="upload_files"),
    path("upload/folder/", views.upload_folder, name="upload_folder"),
    path("download_file/<int:pk>/", views.download_file, name="download_file"),
    path("download_folder/<int:pk>/", views.download_folder, name="download_folder"),
    path("delete_file/<int:pk>/", views.delete_file, name="delete_file"),
    path("delete_folder/<int:pk>/", views.delete_folder, name="delete_folder"),
]
