from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ReviewViewSet

routers = DefaultRouter()
routers.register(r'titles', TitleViewSet, basename='TitleSet')
routers.register(r'genres', GenreViewSet, basename='GenreSet')
routers.register(r'categories', CategoryViewSet, basename='CategorySet')
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
    path('auth/', include('djoser.urls.jwt')),
]