from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Post
from django import forms


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ["username", "email"]


class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "image"]


