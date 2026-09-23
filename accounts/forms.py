from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile

        fields = [
            "profile_image",
            "phone",
            "address",
            "date_of_birth",
            "bio",
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "rows": 3
                }
            ),

            "bio": forms.Textarea(
                attrs={
                    "rows": 4
                }
            ),
        }