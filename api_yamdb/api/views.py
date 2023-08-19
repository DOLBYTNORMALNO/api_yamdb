from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated

from rest_framework.relations import SlugRelatedField

from reviews.models import User
import random
import string
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer
from .permissions import IsAdminOrReadOnly, IsAdmin

from reviews.models import Category, Genre, Title, Review
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    CommetSerializer,
    ReviewSerializer
)


class ObtainTokenView(APIView):
    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        user = get_object_or_404(User, username=username, confirmation_code=confirmation_code)

        # Создание токена для пользователя
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({'token': access_token}, status=status.HTTP_200_OK)


class SignUpView(APIView):
    def post(self, request):
        username = request.data.get('username')
        if username == 'me':
            return Response({'detail': 'Username "me" is reserved.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Генерация кода подтверждения
            confirmation_code = ''.join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )
            # Сохранение пользователя с ролью "user" и кодом подтверждения
            user = serializer.save(
                role=User.USER, confirmation_code=confirmation_code
            )

            # Отправка письма с кодом подтверждения
            send_mail(
                'Подтверждение регистрации',
                f'Ваш код подтверждения: {confirmation_code}',
                'noreply@yamdb.com',
                [user.email],
                fail_silently=False,
            )

            # Возвращаем только email и username
            data = {
                'email': serializer.data['email'],
                'username': serializer.data['username']
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(
        detail=False, methods=['delete'],
        url_path=r'(?P<slug>\w+)',
        lookup_field='slug', url_name='category_slug'
    )
    def get_category(self, request, slug):
        category = self.get_object()
        serializer = CategorySerializer(category)
        category.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(
    detail=False, methods=['delete'],
    url_path=r'(?P<slug>\w+)',
    lookup_field='slug', url_name='genre_slug'
    )
    def get_genre(self, request, slug):
        genre = self.get_object()
        serializer = GenreSerializer(genre)
        genre.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('rating')
    serializer_class = TitleSerializer

    def perform_create(self, serializer):
        category = get_object_or_404(
            Category, slug=self.request.data.get('category')
        )
        genre = Genre.objects.filter(
            slug__in=self.request.data.getlist('genre')
        )
        serializer.save(category=category, genre=genre)

    def perform_update(self, serializer):
        self.perform_create(serializer)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommetSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        new_queryset = get_object_or_404(Review, title_id=title_id).comments.all()
        return new_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(author=self.request.user, title_id=title_id)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all
    serializer_class = ReviewSerializer
    author = SlugRelatedField(slug_field='username', read_only=True)

