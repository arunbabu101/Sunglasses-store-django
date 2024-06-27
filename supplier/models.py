from django.db import models
from django.contrib.auth.models import User

class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    status = models.CharField(max_length=20, default='active')

    def __str__(self):
        return self.name