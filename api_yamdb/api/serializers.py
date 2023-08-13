from rest_framework import serializers
from reviews.models import CustomUser
import random
import string
from django.core.mail import send_mail

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'role')
        extra_kwargs = {
            'username': {'max_length': 150, 'pattern': r'^[\w.@+-]+\z'},
            'email': {'max_length': 254},
            'role': {'read_only': True}
        }

    def create(self, validated_data):
        # Генерация кода подтверждения
        confirmation_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        validated_data['confirmation_code'] = confirmation_code
        user = super().create(validated_data)

        # Отправка письма с кодом подтверждения
        send_mail(
            'Подтверждение регистрации',
            f'Ваш код подтверждения: {confirmation_code}',
            'noreply@yamdb.com',
            [user.email],
            fail_silently=False,
        )
        return user
