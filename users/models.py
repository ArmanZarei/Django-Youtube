from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    class Role(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        ADMIN = "ADMIN", "Admin"
        OWNER = "OWNER", "Owner"

    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    role = models.CharField(
        max_length=8,
        choices=Role.choices,
        default=Role.NORMAL
    )

    is_approved = models.BooleanField(default=False)

    strike = models.BooleanField(default=False)
