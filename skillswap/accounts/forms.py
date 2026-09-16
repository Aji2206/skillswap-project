from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            "profile_picture",
            "bio",
            "location",
            "skills_offered",
            "skills_wanted",
        ]

        widgets = {
            "bio": forms.Textarea(attrs={"rows":4}),
            "skills_offered": forms.Textarea(attrs={"rows":4}),
            "skills_wanted": forms.Textarea(attrs={"rows":4}),
        }