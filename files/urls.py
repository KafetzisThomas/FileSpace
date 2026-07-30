from django.urls import path
from . import views

app_name = "files"
urlpatterns = [
    path("", views.drive, name="drive"),
    path('drive/<int:folder_id>/', views.drive, name='drive_folder'),

    path("upload/files/", views.upload_files, name="upload_files"),
    path("upload/folder/", views.upload_folder, name="upload_folder"),

    path("files/<int:pk>/view", views.preview_file, name="file_preview"),
    path('file/<int:pk>/view/pdf/', views.preview_pdf, name='preview_pdf'),
    path("files/<int:pk>/download", views.download_file, name="file_download"),
    path("files/<int:pk>/delete", views.delete_file, name="file_delete"),

    path("folders/<int:pk>/download", views.download_folder, name="folder_download"),
    path("folders/<int:pk>/delete", views.delete_folder, name="folder_delete"),
]
