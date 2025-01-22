from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)

    # Allow non-unique username and set email as the USERNAME_FIELD
    username = models.CharField(max_length=150, blank=False)  # Non-unique username
    email = models.EmailField(unique=True)  # Ensure the email is unique

    # Set email as the USERNAME_FIELD
    USERNAME_FIELD = 'email'

    # Make sure `email` is NOT in REQUIRED_FIELDS
    REQUIRED_FIELDS = ['username']  # 'email' should NOT be here

    def __str__(self):
        return self.username
