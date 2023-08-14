from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet, TitleViewSet, UserViewSet, SignUpView, ObtainTokenView

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
    r'titles/(?P<title_id>\d=)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='CommentSet'
)
routers.register(
    r'titles/(?P<title_id>\d+)/reviews/',
    ReviewViewSet,
    basename='ReviewSet'
)


urlpatterns = [
    path('', include(routers.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/jwt/', include('djoser.urls.jwt')),
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/token/', ObtainTokenView.as_view(), name='token'),
]
