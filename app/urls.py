from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.PostListView.as_view(), name="main"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]
