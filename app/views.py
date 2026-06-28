from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from .forms import RegistrationForm, PostCreationForm
from .models import Post, CustomUser
from django.views import View


class RegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("main")
        return render(request, "register.html", {"form": form})


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("main")
        return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("main")


class PostListView(View):
    def get(self, request):
        posts = Post.objects.all().order_by("-created_at")
        return render(request, "main.html", {"posts": posts})


class PostDetailView(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        return render(request, "post_detail.html", {"post": post})


class PostCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = PostCreationForm()
        return render(request, "post_create.html", {"form": form})

    def post(self, request):
        form = PostCreationForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            return redirect("main")
        return render(request, "post_create.html", {"form": form})


class PostUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user and not request.user.is_staff:
            raise PermissionDenied
        form = PostCreationForm(instance=post)
        return render(request, "post_update.html", {"form": form, "post": post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user and not request.user.is_staff:
            raise PermissionDenied
        form = PostCreationForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("main")
        return render(request, "post_update.html", {"form": form, "post": post})


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if post.author != request.user and not request.user.is_staff:
            raise PermissionDenied

        return render(request, "post_delete.html", {"post": post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user and not request.user.is_staff:
            raise PermissionDenied
        post.delete()
        return redirect("main")


class UsersProfileView(View):
    def get(self, request, username):
        profile_user = get_object_or_404(CustomUser, username=username)
        user_posts = Post.objects.filter(author=profile_user).order_by("-created_at")
        return render(
            request, "profile.html", {"user": profile_user, "posts": user_posts}
        )


class UpdateAvatarView(LoginRequiredMixin, View):
    def post(self, request):
        if "photo" in request.FILES:
            user = request.user
            user.photo = request.FILES["photo"]
            user.save()
        return redirect("profile", username=user.username)
