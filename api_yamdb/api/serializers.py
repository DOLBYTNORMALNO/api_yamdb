from django.shortcuts import get_object_or_404
from rest_framework import serializers
from users.models import CustomUser
from reviews.models import (
    Title,
    Category,
    Genre,
    Review,
    Comment,
)

from rest_framework.relations import SlugRelatedField

from django.contrib.auth.tokens import default_token_generator
from django.core.validators import RegexValidator


class ObtainTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        if not all([username, confirmation_code]):
            raise serializers.ValidationError(
                "Both username and confirmation code are required."
            )

        user = get_object_or_404(CustomUser, username=username)

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError("Invalid confirmation code.")

        return data


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]+\Z')]
    )

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError('Username "me" is restricted.')

        if CustomUser.objects.filter(username=value).exists():
            user = CustomUser.objects.get(username=value)
            if user.email != self.initial_data.get("email"):
                raise serializers.ValidationError(
                    "Username already exists with a different email."
                )
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            user = CustomUser.objects.get(email=value)
            if user.username != self.initial_data.get("username"):
                raise serializers.ValidationError(
                    "Email already exists with a different username."
                )
        return value


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
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

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        user = super().create(validated_data)
        confirmation_code = default_token_generator.make_token(user)
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
    rating = serializers.IntegerField(read_only=True)

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
    author = SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field="username",
    )

    class Meta:
        fields = (
            "id",
            "text",
            "author",
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
