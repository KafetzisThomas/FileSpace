import os
import uuid
from django.db import models
from django.conf import settings

def user_file_path(instance, filename):
    """
    Store user dirs and files with UUID filenames to avoid collisions, isolated per user.
    """
    instance.name = filename
    file_extension = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    base_dir = f"user_{instance.owner.id}"
    if instance.full_path:
        directory_path = os.path.dirname(instance.full_path)
        return os.path.join(base_dir, directory_path, unique_filename)

    # fallback for single files
    return os.path.join(base_dir, unique_filename)

class File(models.Model):
    file = models.FileField(upload_to=user_file_path)
    size = models.BigIntegerField(blank=True)
    full_path = models.CharField(max_length=1000, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="files")

    def __str__(self):
        return self.name
