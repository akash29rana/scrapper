# movies/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import MovieViewSet
from . import views

router = DefaultRouter()
router.register(r'movies', views.MovieViewSet, basename='movie')

urlpatterns = [
    path('api/', include(router.urls)),
    path('search/', views.search_movies, name='search_movies'),
    path('get-scraping-progress/', views.get_scraping_progress, name='get_scraping_progress'),
    
]
