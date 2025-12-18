from rest_framework import serializers
from .models import *


class DirectorSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = ['first_name', 'last_name', 'sex', 'photo', 'birth_date']


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['first_name', 'last_name', 'sex', 'photo', 'birth_date']


class MovieSerializerSmall(serializers.ModelSerializer):
    director = serializers.StringRelatedField()

    class Meta:
        model = Movie
        fields = ['title', 'poster', 'rating', 'date', 'director']


class ActorSerializerDetail(serializers.ModelSerializer):
    movies = MovieSerializerSmall(many=True)

    class Meta:
        model = Actor
        fields = ['first_name', 'last_name', 'sex', 'photo', 'birth_date', 'movies']


class MovieSerializer(serializers.ModelSerializer):
    director = serializers.StringRelatedField()
    # actors = serializers.StringRelatedField(many=True)
    actors = serializers.SlugRelatedField(slug_field='last_name', many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['title', 'poster', 'rating', 'date', 'trailer', 'plot', 'actors', 'slug', 'director', 'users_to_watch', 'user_rated_this_movie', 'genres']


class CreateMovieCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieComment
        fields = ['text', 'movie', 'author']


class CreateMovieCommentSerializer2(serializers.ModelSerializer):
    class Meta:
        model = MovieComment
        fields = ['text', 'movie']
        read_only_fields = ['author']


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    addressee = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = ['author', 'addressee', 'text', 'is_read', 'created']


class MessageSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['text', 'addressee']

    def validate_addressee(self, value):
        request = self.context.get('request')
        if request and request.user == value:
            raise serializers.ValidationError("Вы не можете отправить сообщение самому себе.")
        return value


class PersonalMovieListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    movies = serializers.StringRelatedField(many=True)

    class Meta:
        model = PersonalMovieList
        fields = ['name', 'user', 'movies', 'created']


class PersonalMovieListSerializer2(serializers.ModelSerializer):
    class Meta:
        model = PersonalMovieList
        fields = ['name']


class MovieCustomSerializer(serializers.ModelSerializer):
    url_detail = serializers.HyperlinkedIdentityField(view_name='imdb:movie-detail', lookup_field='slug')

    class Meta:
        model = Movie
        fields = ['__str__', 'url_detail', 'get_absolute_url']


class SinglePageActorsListSerializer(serializers.ModelSerializer):
    num_movies = serializers.IntegerField()
    # movies = serializers.StringRelatedField(many=True)
    movies = MovieCustomSerializer(many=True)
    avg_rating = serializers.FloatField()
    url_detail = serializers.HyperlinkedIdentityField(view_name='imdb:actor-detail', lookup_field='pk')

    class Meta:
        model = Actor
        fields = ['first_name', 'last_name', 'sex', 'photo', 'birth_date', 'movies', 'num_movies', 'avg_rating', 'url_detail']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']


class SinglePageMovieListSerializer(serializers.ModelSerializer):
    director = serializers.StringRelatedField()
    actors = serializers.StringRelatedField(many=True)
    user_rated_this_movie = serializers.SlugRelatedField(many=True, read_only=True, slug_field='username')
    users_to_watch = serializers.SlugRelatedField(many=True, read_only=True, slug_field='last_name')
    genres = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = ['title', 'poster', 'rating', 'date', 'trailer', 'plot', 'actors', 'slug', 'director', 'users_to_watch', 'user_rated_this_movie', 'genres']
