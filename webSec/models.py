from django.db import models

# Create your models here.
class Signup_user(models.Model):
    Username =models.CharField(max_length=50)
    Email =models.CharField(max_length=50)
    Password =models.CharField(max_length=50)
    Conform_Password =models.CharField(max_length=50)