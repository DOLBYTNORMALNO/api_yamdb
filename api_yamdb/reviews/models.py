from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES_SCORE = [(i, i) for i in range(1, 11)]


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    confirmation_code = models.CharField(max_length=10, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return f'{self.name}'


class Genre(models.Model):
    class Meta:
        verbose_name = "genre"
        verbose_name_plural = "genres"

    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    class Meta:
        verbose_name = "title"
        verbose_name_plural = "titles"

    name = models.CharField(max_length=255)
    year = models.IntegerField()
    description = models.TextField()
    genres = models.ManyToManyField(
        Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles', blank=True, null=True)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    user = models.ForeignKey(

        User, on_delete=models.CASCADE

    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    score = models.IntegerField(choices=CHOICES_SCORE)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.title} {self.text} {self.score}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'title'],
                name='unique_user_title'
            )
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)


    def __str__(self):
        return f'{self.text}'
