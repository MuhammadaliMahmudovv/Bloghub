from os import name
from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.PostListView.as_view(), name="main"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("posts/create/", views.PostCreateView.as_view(), name="create"),
    path("posts/<int:pk>/update/", views.PostUpdateView.as_view(), name="update"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="delete"),
    path("posts/<int:post_id>/like/", views.LikePost.as_view(), name="like_post"),
    path("posts/<int:post_id>/comment/", views.AddCommentView.as_view(), name="add_comment"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/update-avatar/", views.UpdateAvatarView.as_view(), name="update_avatar"),
    path("profile/<str:username>/", views.UsersProfileView.as_view(), name="profile"),
]
