from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q, Exists, OuterRef
from .forms import RegistrationForm, PostCreationForm
from django.core.exceptions import PermissionDenied
from .models import Post, CustomUser, Like, Comment
from django.core.paginator import Paginator
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
        posts = (
            Post.objects.all()
            .select_related("author")
            .prefetch_related("likes")
            .annotate(comments_count=Count("comments"))
            .order_by("-created_at")
        )

        if request.user.is_authenticated:
            user_likes = Like.objects.filter(post=OuterRef("pk"), user=request.user)
            posts = posts.annotate(is_liked=Exists(user_likes))

        search_query = request.GET.get("search", "").strip()

        if search_query:
            posts = posts.filter(Q(title__icontains=search_query))
        else:
            search_query = None

        paginator = Paginator(posts, 5)
        page_num = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_num)

        return render(
            request, "main.html", {"page_obj": page_obj, "search_query": search_query}
        )


class PostDetailView(View):
    def get(self, request, pk):
        # post = get_object_or_404(Post.objects.select_related("author"), pk=pk)
        # comments = Comment.objects.filter(post=pk).select_related("user")
        # return render(request, "post_detail.html", {"post": post, "comments": comments})
        post = get_object_or_404(Post.objects.select_related("author"), pk=pk)

        if request.user.is_authenticated:
            is_liked = Like.objects.filter(post=post, user=request.user).exists()

        comments = Comment.objects.filter(post=pk).select_related("user")
        comments_count = len(comments)

        context = {
            "post": post,
            "comments": comments,
            "comments_count": comments_count,
            "is_liked": is_liked,
        }
        return render(request, "post_detail.html", context)


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
        user_posts = (
            Post.objects.filter(author=profile_user)
            .select_related("author")
            .prefetch_related("likes")
            .annotate(comments_count=Count("comments"))
            .order_by("-created_at")
        )
        return render(
            request, "profile.html", {"user": profile_user, "posts": user_posts}
        )


class UpdateAvatarView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        if "photo" in request.FILES:
            user.photo = request.FILES["photo"]
            user.save()
        return redirect("profile", username=user.username)


class LikePost(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        return redirect("post_detail", pk=post_id)


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)
        comment = request.POST.get("text", "").strip()

        if comment:
            Comment.objects.create(post=post, user=user, text=comment)
        return redirect("post_detail", pk=post_id)
