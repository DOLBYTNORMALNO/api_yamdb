from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SignUpView, ObtainTokenView
from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    CommentViewSet,
    ReviewViewSet,
)

v_1_router = DefaultRouter()

v_1_router.register(
    "titles",
    TitleViewSet,
    basename="TitleSet"
)
v_1_router.register(
    "genres",
    GenreViewSet,
    basename="GenreSet"
)
v_1_router.register(
    "categories",
    CategoryViewSet,
    basename="CategorySet"
)
v_1_router.register(
    "users",
    UserViewSet,
    basename="UserSet"
)
v_1_router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="CommentSet",
)
v_1_router.register(
    r"titles/(?P<title_id>\d+)/reviews",
    ReviewViewSet,
    basename="ReviewSet"
)

auth_patterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("token/", ObtainTokenView.as_view(), name="token"),
]

urlpatterns = [
    path("", include(v_1_router.urls)),
    path("auth/", include(auth_patterns)),
]
