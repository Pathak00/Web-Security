from django.db import models

# Create your models here.
<<<<<<< Updated upstream
class Signup_user(models.Model):
    Username =models.CharField(max_length=50)
    Email =models.CharField(max_length=50)
    Password =models.CharField(max_length=50)
    Conform_Password =models.CharField(max_length=50)
=======
class SignUp(models.Model):
    
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    
   

>>>>>>> Stashed changes
