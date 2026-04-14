import os
import uuid
from django.db import models
from django.conf import settings

def user_file_path(instance, filename):
    """
    Store user files with UUID filenames to avoid collisions, isolated per user.
    """
    instance.name = filename
    file_extension = os.path.splitext(filename)[1]
    return f"user_{instance.owner.id}/{uuid.uuid4()}{file_extension}"


class File(models.Model):
    file = models.FileField(upload_to=user_file_path)
    name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="files")

    def __str__(self):
        return self.name
