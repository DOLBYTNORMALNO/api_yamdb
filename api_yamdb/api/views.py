from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.core.mail import send_mail


from .mixins import ListCreateDestroyViewSet
from .filters import TitleFilter
from .permissions import (
    IsAdminOrReadOnly,
    IsAdmin,
    IsAuthenticatedOrReadOnly,
    IsAuthorOrModeratorOrAdmin,
)
from reviews.models import Category, Genre, Title, Review
from users.models import CustomUser
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleCreateSerializer,
    CommentSerializer,
    ReviewSerializer,
    UserSerializer,
    ObtainTokenSerializer,
    SignUpSerializer
)


class ObtainTokenView(APIView):
    def post(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = CustomUser.objects.get(
            username=serializer.validated_data['username'])
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response({"token": access_token}, status=status.HTTP_200_OK)


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        username = serializer.validated_data.get("username")

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "role": CustomUser.USER,
            },
        )

        token = default_token_generator.make_token(user)

        if not created:
            user.save()

        send_mail(
            "Подтверждение регистрации",
            f"Ваш код подтверждения: {token}",
            "noreply@yamdb.com",
            [user.email],
            fail_silently=False,
        )

        data = {"email": email, "username": username}
        return Response(data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ["username"]
    lookup_field = "username"

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        if "role" in request.data:
            return Response(
                {"detail": "Changing role is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == "PATCH":
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg("reviews__score")).order_by(
        "rating"
    )
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        title_id = int(self.kwargs.get("title_id"))
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all().order_by('pub_date')

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title_id=title_id)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        title_id = self.kwargs.get("title_id")
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        return review.comments.all().order_by('pub_date')

    def perform_create(self, serializer):
        review_id = self.kwargs.get("review_id")
        title_id = self.kwargs.get("title_id")
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        user = self.request.user
        serializer.save(author=user, review=review)
