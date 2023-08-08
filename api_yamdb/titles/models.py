from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(models.Model):

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


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

    name = models.CharField(max_length=16)
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