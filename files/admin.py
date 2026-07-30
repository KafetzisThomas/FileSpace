from django.contrib import admin
from .models import Folder, File

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "parent", "created_at")
    list_filter = ("owner", "created_at")
    search_fields = ("name", "owner__username")


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "folder", "size", "uploaded_at")
    list_filter = ("owner", "uploaded_at")
    search_fields = ("name", "owner__username")
