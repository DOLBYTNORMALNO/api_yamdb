from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import UserViewSet, SignUpView, ObtainTokenView

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    CommentViewSet,
    ReviewViewSet
)


routers = DefaultRouter()
routers.register(r'titles', TitleViewSet, basename='TitleSet')
routers.register(r'genres', GenreViewSet, basename='GenreSet')
routers.register(r'categories', CategoryViewSet, basename='CategorySet')
routers.register(r'users', UserViewSet, basename='UserSet')
routers.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews_set'
)
routers.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments_set'
)


urlpatterns = [
    path('', include(routers.urls)),
    path('auth/signup/', SignUpView, name='signup'),
    path('auth/token/', ObtainTokenView, name='token'),
]
