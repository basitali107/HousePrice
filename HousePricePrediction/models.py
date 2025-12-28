from django.db import models

class UserProfile(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.full_name