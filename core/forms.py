from django import forms


class RegisterForm(forms.Form):
    username=forms.CharField(min_length=6)
    first_name=forms.CharField()
    last_name=forms.CharField()
    email=forms.EmailField()
    password=forms.CharField(min_length=8,max_length=16)