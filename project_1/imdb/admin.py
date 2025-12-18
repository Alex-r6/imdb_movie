from django.contrib import admin
from embed_video.admin import AdminVideoMixin
from .models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    pass


@admin.register(Movie)
class MovieAdmin(AdminVideoMixin, admin.ModelAdmin):
    list_display = ['title', 'genres_str', 'date', 'rating', 'imdb_id']
    prepopulated_fields = {"slug": ["title"]}


class MovieInLine(admin.TabularInline):
    model = Movie


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'birth_date']
    inlines = [MovieInLine]


@admin.register(MovieComment)
class MovieCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'movie', 'created']


@admin.register(DirectorComment)
class DirectorCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'director', 'created']


@admin.register(PersonalMovieList)
class PersonalMovieListAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created']


@admin.register(UserMovieRating)
class UserMovieRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'value', 'created']
    list_filter = ['user', 'movie']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name','created']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['author','addressee', 'is_read', 'created']