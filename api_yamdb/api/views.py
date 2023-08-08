from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from reviews.models import CustomUser
from .serializers import CustomUserSerializer
import random
import string


class SignUpView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            # Генерация кода подтверждения
            confirmation_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

            # Сохранение пользователя с ролью "user" и кодом подтверждения
            user = serializer.save(role=CustomUser.USER, confirmation_code=confirmation_code)

            # Отправка письма с кодом подтверждения
            send_mail(
                'Подтверждение регистрации',
                f'Ваш код подтверждения: {confirmation_code}',
                'noreply@yamdb.com',
                [user.email],
                fail_silently=False,
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
