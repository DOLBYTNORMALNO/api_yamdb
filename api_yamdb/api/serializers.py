from rest_framework import serializers

from reviews.models import Review, Comment


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'user', 'title', 'score')
        model = Review


class CommetSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'user', 'title')
        model = Comment