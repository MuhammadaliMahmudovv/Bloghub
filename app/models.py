from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    photo = models.ImageField(
        upload_to="avatar/", blank=True, null=True, default="avatar/default.jpg"
    )
    email = models.EmailField(blank=False, null=False, unique=True)

    def __str__(self):
        return self.username


class Post(models.Model):
    image = models.ImageField(upload_to="post_photo/", blank=True, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
