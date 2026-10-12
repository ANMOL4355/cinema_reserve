from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    profile_image = models.ImageField( upload_to="profile_images/",blank=True,null=True)
    phone = models.CharField(max_length=20,blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=500,blank=True)
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(blank=True,null=True)
    
    def __str__(self):
        return self.user.username
    
    
class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_otps")
    email = models.EmailField()  
    code_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)  

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.user.username} ({self.email})"