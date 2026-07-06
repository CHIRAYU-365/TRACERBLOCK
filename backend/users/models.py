from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MANUFACTURER', 'Manufacturer'),
        ('DISTRIBUTOR', 'Distributor'),
        ('RETAILER', 'Retailer'),
        ('LOGISTICS', 'Logistics Provider'),
        ('QA', 'Quality Assurance'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ADMIN')
    organization = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.role}"
