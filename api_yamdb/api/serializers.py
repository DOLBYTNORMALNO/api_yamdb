from django.db.models import Avg
from rest_framework import serializers
from reviews.models import (
    CustomUser,
    Title,
    Category,
    Genre,
    GenreTitle,
    Review,
    Comment,
)
import random
import string
from rest_framework.relations import SlugRelatedField
from django.core.validators import RegexValidator


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(r"^[\w.@+-]+\Z")],
        required=True,
        allow_blank=False,
    )

    role = serializers.ChoiceField(
        choices=CustomUser.ROLE_CHOICES, default=CustomUser.USER
    )

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "role",
            "first_name",
            "last_name",
            "bio",
        )
        extra_kwargs = {
            "username": {
                "max_length": 150,
                "required": True,
                "allow_blank": False,
            },
            "email": {
                "max_length": 254,
                "required": True,
                "allow_blank": False,
            },
            "role": {"read_only": True},
        }

    def create(self, validated_data):
        confirmation_code = "".join(
            random.choices(string.ascii_letters + string.digits, k=10)
        )

        user = super().create(validated_data)
        user.confirmation_code = confirmation_code
        user.save()

        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ["id"]
        model = Category
        lookup_field = "slug"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ["id"]
        model = Genre
        lookup_field = "slug"


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = [
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        ]

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg("score")).get("score__avg")
        if not rating:
            return rating
        return round(rating, 1)


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="slug"
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field="slug", many=True
    )

    class Meta:
        fields = "__all__"
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field="id", queryset=Title.objects.all(), required=False
    )
    author = SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field="username",
    )

    class Meta:
        fields = (
            "id",
            "author",
            "text",
            "title",
            "score",
            "pub_date",
        )
        model = Review

    def validate_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                "Допустимое значение рейтинга от 1 до 10"
            )
        return value

    def validate(self, data):
        if self.context["request"].method == "POST":
            user = self.context["request"].user
            title_id = self.context["view"].kwargs.get("title_id")
            if Review.objects.filter(
                author_id=user.id, title_id=title_id
            ).exists():
                raise serializers.ValidationError("Отзыв уже оставлен.")
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field="username",
    )

    class Meta:
        exclude = ("review",)
        model = Comment
