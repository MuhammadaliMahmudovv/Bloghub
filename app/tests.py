from .models import Post, CustomUser, Like, Comment
from django.test import TestCase
from django.urls import reverse

"""
Анатомия теста (Правило AAA)

Каждый тест в мире программирования строится по одной и той же схеме, которая называется AAA (Arrange, Act, Assert):

Arrange (Подготовка): Создаем виртуальные данные в базе (например, фейкового пользователя и пост).

Act (Действие): Исполняем тестируемый код (например, отправляем GET-запрос на страницу поста).

Assert (Проверка): Сверяем результат. (Например: «Сервер вернул статус 200? На странице есть текст поста?»). Если всё совпало — тест пройден. Если нет — тест упал и указал на ошибку.
"""


class PostListViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="TestUser1",
            email="testuser1@gmail.com",
            password="securepassword123",
        )

        self.user2 = CustomUser.objects.create_user(
            username="TestUser2",
            email="testemail2@gmail.com",
            password="securepassword123",
        )

        self.post = Post.objects.create(
            title="test post",
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            author=self.user,
        )

    def test_authenticated_user_can_create_post(self):
        self.client.login(username="TestUser1", password="securepassword123")
        response = self.client.post(
            reverse("create"),
            {
                "title": "Test Post 1",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.all().count(), 2)
        new_post = Post.objects.order_by("-id").first()
        self.assertEqual(new_post.title, "Test Post 1")
        self.assertEqual(new_post.author, self.user)

    def test_anonymous_user_cannot_create_post(self):
        response = self.client.post(
            reverse("create"),
            {
                "title": "Test Post 2",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_user1_cannot_change_user2_post(self):
        self.client.login(username="TestUser2", password="securepassword123")
        response = self.client.post(
            reverse("update", args=[self.post.pk]),
            {
                "title": "Hacking",
                "context": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "test post")

    def test_user1_cannot_delete_user2_post(self):
        self.client.login(username="TestUser2", password="securepassword123")
        response = self.client.post(reverse("delete", args=[self.post.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_toggle_like_behavior(self):
        self.client.login(username="TestUser2", password="securepassword123")
        self.client.post(reverse("like_post", args=[self.post.pk]))
        self.assertEqual(Like.objects.all().count(), 1)

        self.client.post(reverse("like_post", args=[self.post.pk]))
        self.assertEqual(Like.objects.all().count(), 0)

    def test_user_cannot_like_own_post(self):
        self.client.login(username="TestUser1", password="securepassword123")
        response = self.client.post(reverse("like_post", args=[self.post.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Like.objects.all().count(), 0)

    def test_authenticated_user_can_add_comment(self):
        self.client.login(username="TestUser2", password="securepassword123")
        response = self.client.post(
            reverse("add_comment", args=[self.post.pk]),
            {"text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.all().count(), 1)

    def test_unauthorized_user_cannot_add_comment(self):
        response = self.client.post(
            reverse("add_comment", args=[self.post.pk]),
            {"text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.all().count(), 0)
