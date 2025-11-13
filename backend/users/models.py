from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    csv_upload_limit = models.IntegerField(default=5)
    # Add any additional fields you want for your user model here
    # For example:
    # bio = models.TextField(max_length=500, blank=True)
    # location = models.CharField(max_length=30, blank=True)
    # birth_date = models.DateField(null=True, blank=True)

    pass