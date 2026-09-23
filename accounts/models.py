from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    profile_image = models.ImageField( upload_to="profile_images/",blank=True,null=True)
    phone = models.CharField(max_length=20,blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=500,blank=True)

    def __str__(self):
        return self.user.username