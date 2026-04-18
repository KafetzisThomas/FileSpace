import os
import uuid
from django.db import models
from django.conf import settings

def user_file_path(instance, filename):
    """
    Store user files with UUID filenames to avoid collisions, isolated per user.
    """
    file_extension = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    return f"user_{instance.owner.id}/{unique_filename}"


class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="folders")

    def __str__(self):
        return self.name


class File(models.Model):
    file = models.FileField(upload_to=user_file_path)
    name = models.CharField(max_length=255, blank=True)
    size = models.BigIntegerField(blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='files')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="files")

    def __str__(self):
        return self.name
