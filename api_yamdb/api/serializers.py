
from django.db.models import Avg
from rest_framework import serializers
from reviews.models import User, Title, Category, Genre, GenreTitle, Review, Comment
import random
import string
from django.core.mail import send_mail
from django.core.validators import RegexValidator



class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]+\Z')],
        required=True,
        allow_blank=False
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'role', 'first_name', 'last_name', 'bio')  # Добавлены поля
        extra_kwargs = {
            'username': {'max_length': 150, 'required': True, 'allow_blank': False},
            'email': {'max_length': 254, 'required': True, 'allow_blank': False},

            'role': {'read_only': True}
        }

    def create(self, validated_data):
        # Генерация кода подтверждения
        confirmation_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        user = super().create(validated_data)
        user.confirmation_code = confirmation_code
        user.save()

        # Отправка письма с кодом подтверждения
        send_mail(
            'Подтверждение регистрации',
            f'Ваш код подтверждения: {confirmation_code}',
            'noreply@yamdb.com',
            [user.email],
            fail_silently=False,
        )
        return user


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ['id']
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ['id']
        model = Genre


#class TitleSerializer(serializers.ModelSerializer):
#    category = CategorySerializer()
#    genre = GenreSerializer(many=True)
#    rating = serializers.FloatField(read_only=True)
#
#    class Meta:
#        fields = '__all__'
#        model = Title
#
#    def get_rating(self, obj):
#        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
#        if not rating:
#            return rating
#        return round(rating, 1)


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genres = GenreSerializer(many=True, required=False)
    rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Title
        fields = '__all__'

    def create(self, validated_data):
        genres_data = validated_data.pop('genres', [])
        title = Title.objects.create(**validated_data)
        for genre_data in genres_data:
            genre = Genre.objects.get(**genre_data)
            title.genres.add(genre)
        return title

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        if not rating:
            return rating
        return round(rating, 1)

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'user', 'title', 'score')
        model = Review

    def validate_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                'Допустимое значение рейтинга от 1 до 10'
            )
        return value


class CommetSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'user', 'title')
        model = Comment

