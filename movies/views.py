from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Movie, Genre
from .serializers import MovieSerializer
from .scraper import scrape_with_playwright
from django.http import JsonResponse
import asyncio
from django.core.cache import cache
from django.db import transaction
import json
from asgiref.sync import sync_to_async


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer

    #api/movies/?search=some_movie_title
    def get_queryset(self):
        queryset = Movie.objects.all()
        title_query = self.request.query_params.get('title', None)
        genre_query = self.request.query_params.get('genre', None)
        if title_query:
            queryset = queryset.filter(title__icontains=title_query)  # Case-insensitive search
        if genre_query:
            genre_query = genre_query.split(",")
            queryset = queryset.filter(genres__name__in=genre_query)  # Case-insensitive search
        return queryset

    def destroy(self, request, *args, **kwargs):
        title = request.data.get('title', None)
        if title:
            try:
                movie = Movie.objects.get(title=title)
                movie.delete()  # Delete movie based on title
                return Response({"detail": "Movie deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            except Movie.DoesNotExist:
                return Response({"detail": "Movie not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Title is required."}, status=status.HTTP_400_BAD_REQUEST)



async def search_movies(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        genre = data.get('genre', '')
        cache.delete(f'scraping_progress_{genre}') 
        movies = []
        
        if genre:
            # Function for upating the progreess 
            def update_progress(progress,genre):
                cache.set(f'scraping_progress_{genre}', progress, timeout=3600) # Saving progress in cache     
                pass      
            
            movies = await (scrape_with_playwright(genre, update_progress))

            if(len(movies) > 0):
                await create_movies_in_bulk(movies,genre)

            return JsonResponse({'movies': movies})

    return render(request, 'search.html')


def get_scraping_progress(request):
    genre = request.GET.get('genre', '')
    # Retrieve progress from cache 
    progress = cache.get(f'scraping_progress_{genre}', 0) 
    return JsonResponse({'progress': progress})


@sync_to_async
def create_movies_in_bulk(movies_data, genre_str):
    genre_objs = get_or_create_genres(genre_str)  
    
    movie_objs = []
    for movie_data in movies_data:
        print("movie_data", movie_data)
        movie_obj = Movie(
            title=movie_data['title'],
            release_year=movie_data['year'],
            imdb_rating=movie_data.get('rating'),
            director=movie_data['director'],
            cast=movie_data['cast'],
            plot_summary=movie_data['description']
        )
        movie_objs.append(movie_obj)
    
    # Using bulk_create for efficient database insertion
    chunk_size_query = 10000
    with transaction.atomic():  # Ensure all operations are atomic (either all succeed or fail)
        for i in range(0, len(movie_objs), chunk_size_query):
            batch = movie_objs[i:i + chunk_size_query]
            Movie.objects.bulk_create(batch, ignore_conflicts=True)
    
    # After the movies are created, associate genres with the movies
    for movie_obj in movie_objs:
        movie_obj.genres.add(*genre_objs)  # Add all genres to the movies



def get_or_create_genres(genre_str):
    genres = genre_str.split(",")  # Split genres from comma-separated string
    genre_objs = []
    print("genre_objs",genre_objs)
    # Iterate over genres to either get or create
    for genre in genres:
        genre_obj, created = Genre.objects.get_or_create(name=genre.strip())
        genre_objs.append(genre_obj)
    
    print("genre_objs created ",created)
    return genre_objs


