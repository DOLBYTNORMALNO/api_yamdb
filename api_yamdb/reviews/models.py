from django.db import models
from users.models import CustomUser

CHOICES_SCORE = [(i, i) for i in range(1, 11)]


class Category(models.Model):
    name = models.CharField(max_length=20, verbose_name="Name")
    slug = models.SlugField(unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.name}"


class Genre(models.Model):
    name = models.CharField(max_length=20, verbose_name="Name")
    slug = models.SlugField(unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "genre"
        verbose_name_plural = "genres"

    def __str__(self):
        return f"{self.name}"


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name="Name")
    year = models.IntegerField(verbose_name="Year")
    description = models.TextField(verbose_name="Description")
    genre = models.ManyToManyField(Genre, through="GenreTitle", verbose_name="Genres")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="titles",
        blank=True,
        null=True,
        verbose_name="Category",
    )

    class Meta:
        verbose_name = "title"
        verbose_name_plural = "titles"

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="Genre")
    title = models.ForeignKey(Title, on_delete=models.CASCADE, verbose_name="Title")

    class Meta:
        verbose_name = "genre title"
        verbose_name_plural = "genre titles"

    def __str__(self):
        return f"{self.genre} {self.title}"


class Review(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=False,
        verbose_name="Author",
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews", null=False, verbose_name="Title"
    )
    text = models.TextField(verbose_name="Text")
    score = models.IntegerField(choices=CHOICES_SCORE, verbose_name="Score")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Publication Date")

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("title", "author"),
                name="unique_title_author",
            ),
        )
        verbose_name = "review"
        verbose_name_plural = "reviews"

    def __str__(self):
        return f"{self.title} {self.text} {self.score}"


class Comment(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments", verbose_name="Author"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments", verbose_name="Review"
    )
    text = models.TextField(verbose_name="Text")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Publication Date")

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"

    def __str__(self):
        return f"{self.text}"
