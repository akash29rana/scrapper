from django.db import models
# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255,primary_key=True)
    release_year = models.IntegerField(blank=True)
    imdb_rating = models.FloatField(null=True, blank=True)
    director = models.CharField(max_length=255,blank=True)
    cast = models.TextField(blank=True)
    plot_summary = models.TextField(blank=True)
    genres = models.ManyToManyField(Genre, related_name='movies')

    def __str__(self):
        return self.title
