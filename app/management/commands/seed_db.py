import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from app.models import CustomUser, Post, Like, Comment

class Command(BaseCommand):
    help = "Наполняет базу данных PostgreSQL фейковыми пользователями, постами, лайками и комментариями"

    def add_arguments(self, parser):
        # Добавляем аргумент, чтобы можно было указывать количество постов из терминала
        parser.add_argument(
            "--posts",
            type=int,
            default=30,
            help="Количество постов для генерации (по умолчанию 30)"
        )

    def handle(self, *args, **options):
        fake = Faker(["ru_RU"])  # Генерируем данные на русском языке
        posts_count = options["posts"]

        self.stdout.write(self.style.WARNING("Начинаем сидирование базы данных..."))

        # Оборачиваем всё в транзакцию, чтобы база данных записала всё одним быстрым пакетом
        with transaction.atomic():
            
            # 1. Создаем авторов (пользователей)
            authors = []
            self.stdout.write("Создаем авторов...")
            for i in range(10):
                username = fake.unique.user_name()
                user = CustomUser.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password="securepassword123"
                )
                authors.append(user)

            # Получаем всех пользователей для лайков/комментов (включая уже созданного админа)
            all_users = list(CustomUser.objects.all())

            # 2. Создаем посты
            self.stdout.write(f"Создаем {posts_count} постов...")
            posts = []
            for _ in range(posts_count):
                post = Post.objects.create(
                    title=fake.sentence(nb_words=random.randint(3, 8)).rstrip("."),
                    content="\n\n".join(fake.paragraphs(nb=random.randint(4, 10))),
                    author=random.choice(authors)
                )
                posts.append(post)

            # 3. Генерируем случайные лайки и комментарии
            self.stdout.write("Генерируем лайки и комментарии...")
            for post in posts:
                # Лайки (каждый юзер может лайкнуть пост только 1 раз благодаря UniqueConstraint)
                potential_likers = random.sample(all_users, k=random.randint(0, len(all_users)))
                for user in potential_likers:
                    # Защита: автор не лайкает свой пост, как мы настроили во view
                    if post.author != user:
                        Like.objects.create(user=user, post=post)

                # Комментарии (один юзер может оставить несколько комментов к посту)
                for _ in range(random.randint(1, 5)):
                    Comment.objects.create(
                        user=random.choice(all_users),
                        post=post,
                        text=fake.paragraph(nb_sentences=random.randint(1, 4))
                    )

        self.stdout.write(self.style.SUCCESS(f"База данных успешно наполнена! Создано {posts_count} постов."))