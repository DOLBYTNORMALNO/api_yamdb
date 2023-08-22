from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.http import Http404

from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated

from rest_framework.relations import SlugRelatedField

from reviews.models import CustomUser, Review, Comment
import random
import string
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer
from .permissions import IsAdminOrReadOnly, IsAdmin, IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin

from reviews.models import Category, Genre, Title, Review
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    CommentSerializer,
    ReviewSerializer
)


class ObtainTokenView(APIView):
    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        user = get_object_or_404(CustomUser, username=username, confirmation_code=confirmation_code)

        # Создание токена для пользователя
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({'token': access_token}, status=status.HTTP_200_OK)


class SignUpView(APIView):
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')

        # Проверка на имя пользователя "me"
        if username == "me":
            return Response({'detail': 'Username "me" is restricted.'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка на уникальность email
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            confirmation_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            user.confirmation_code = confirmation_code
            user.save()
            send_mail(
                'Подтверждение регистрации',
                f'Ваш код подтверждения: {confirmation_code}',
                'noreply@yamdb.com',
                [user.email],
                fail_silently=False,
            )
            data = {
                'email': email,
                'username': user.username
            }
            return Response(data, status=status.HTTP_200_OK)

        # Проверка на уникальность имени пользователя
        if CustomUser.objects.filter(username=username).exists():
            return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Генерация кода подтверждения
            confirmation_code = ''.join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )
            # Сохранение пользователя с ролью "user" и кодом подтверждения
            user = serializer.save(
                role=CustomUser.USER, confirmation_code=confirmation_code
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
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        if 'role' in request.data:
            return Response({'detail': 'Changing role is not allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')

        if CustomUser.objects.filter(email=email).exists():
            return Response({'detail': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(username=username).exists():
            return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        return super(UserViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]

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
    permission_classes = [IsAdminOrReadOnly]

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
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        category_slug = self.request.data.get('category')
        category = Category.objects.get(slug=category_slug)

        genres_slugs = self.request.data.getlist('genre')
        genres = Genre.objects.filter(slug__in=genres_slugs)

        title = serializer.save(category=category)
        title.genres.set(genres)

    def perform_update(self, serializer):
        category_slug = self.request.data.get('category')
        category = Category.objects.get(slug=category_slug)

        genres_slugs = self.request.data.getlist('genre')
        genres = Genre.objects.filter(slug__in=genres_slugs)

        title = serializer.save(category=category)
        title.genres.set(genres)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthorOrModeratorOrAdmin]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super(ReviewViewSet, self).get_permissions()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        # Проверка на наличие соответствующего заголовка
        title_exists = Title.objects.filter(id=title_id).exists()
        if not title_exists:
            # Если заголовка нет, добавляем ошибку в serializer, но не прерываем выполнение
            serializer._errors = {"title_id": ["Title with the given ID does not exist."]}
        else:
            serializer.save(author=self.request.user, title_id=title_id)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthorOrModeratorOrAdmin]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super(CommentViewSet, self).get_permissions()
