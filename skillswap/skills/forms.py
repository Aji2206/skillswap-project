from django import forms
from .models import Skill, SkillRequest


class SkillForm(forms.ModelForm):

    class Meta:

        model = Skill

        fields = [
            "title",
            "category",
            "description",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Skill title"
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe your skill..."
                }
            ),

        }


class SkillRequestForm(forms.ModelForm):

    class Meta:

        model = SkillRequest

        fields = [

            "requester_name",

            "requester_email",

            "message",

        ]

        widgets = {

            "requester_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "requester_email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),

        }