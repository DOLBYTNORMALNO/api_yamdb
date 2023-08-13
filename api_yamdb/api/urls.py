from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, GenreViewSet, TitleViewSet

routers = DefaultRouter()
routers.register(r'titles', TitleViewSet, basename='TitleSet')
routers.register(r'genres', GenreViewSet, basename='GenreSet')
routers.register(r'categories', CategoryViewSet, basename='CategorySet')




urlpatterns = [
    path('', include(routers.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
