from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.relations import SlugRelatedField

from .serializers import CommetSerializer, ReviewSerializer
from reviews.models import Review


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommetSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        new_queryset = get_object_or_404(Review, pk=title_id).comments.all()
        return new_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(author=self.request.user, title_id=title_id)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all
    serializer_class = ReviewSerializer
    author = SlugRelatedField(slug_field='username', read_only=True)
