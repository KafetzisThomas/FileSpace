from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    enable_2fa = models.BooleanField(default=False, verbose_name="Enable 2FA")
    otp_secret = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return self.username
