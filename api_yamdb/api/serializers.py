from django.db.models import Avg
from rest_framework import serializers
from reviews.models import CustomUser, Title, Category, Genre
import random
import string
from django.core.mail import send_mail
from django.core.validators import RegexValidator


class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]+\Z')],
        required=True,
        allow_blank=False
    )

    class Meta:
        model = CustomUser
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
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ['id']
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        if not rating:
            return rating
        return round(rating, 1)

