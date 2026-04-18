from django.urls import path
from . import views

app_name = "files"
urlpatterns = [
    path("", views.drive, name="drive"),
    path('drive/<int:folder_id>/', views.drive, name='drive_folder'),
    path("upload/files/", views.upload_files, name="upload_files"),
    path("upload/folder/", views.upload_folder, name="upload_folder"),
    path("download/<int:pk>/", views.download, name="download"),
    path("delete/<int:pk>/", views.delete, name="delete"),
]
