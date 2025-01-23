# movies/serializers.py
from rest_framework import serializers
from .models import Movie

class MovieSerializer(serializers.ModelSerializer):

    genres = serializers.SerializerMethodField()
    class Meta:
        model = Movie
        fields = ['title', 'release_year', 'imdb_rating', 'director', 'cast', 'plot_summary','genres']
    
    def get_genres(self, obj):
        return [genre.name for genre in obj.genres.all()]
