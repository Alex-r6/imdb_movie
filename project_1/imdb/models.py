from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from embed_video.fields import EmbedVideoField


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='user_imgs/', blank=True)


sex_choises = [('M', 'Male'), ('F', 'Female')]


class Actor(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    birth_date = models.DateField(blank=True)
    photo = models.ImageField(upload_to='actor_imgs', blank=True)
    sex = models.CharField(max_length=1, choices=sex_choises, blank=True)
    actors_by_user = models.ManyToManyField(User, related_name='favourite_actors', blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_absolute_url(self):
        return reverse("imdb:actor-detail", kwargs={"pk": self.id})


class Movie(models.Model):
    title = models.CharField(max_length=100)
    poster = models.ImageField(upload_to='movie_posters', blank=True)
    rating = models.FloatField(default=5.0)
    date = models.DateField(default=timezone.now)
    trailer = EmbedVideoField(blank=True)
    plot = models.TextField(blank=True)
    actors = models.ManyToManyField(Actor, related_name='movies', blank=True)
    slug = models.SlugField()
    director = models.ForeignKey('Director', related_name='movies', blank=True, on_delete=models.SET_NULL, null=True)
    users_to_watch = models.ManyToManyField(User, related_name='watchlist', blank=True)
    user_rated_this_movie = models.ManyToManyField(User, related_name='movies_rated_this_user',  through="UserMovieRating")
    genres = models.ManyToManyField('Genre', related_name='movies', blank=True)
    imdb_id = models.CharField(max_length=12, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.title} ({self.date.year})'

    def get_absolute_url(self):
        return reverse("imdb:movie-detail", kwargs={"slug": self.slug})
        # return reverse('imdb:movie-detail', kwargs={"pk": self.id})

    def genres_str(self):
        return ' '.join(self.genres.values_list('name', flat=True).order_by("name"))


class Director(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    birth_date = models.DateField(blank=True)
    photo = models.ImageField(upload_to='director_imgs', blank=True)
    sex = models.CharField(max_length=1, choices=sex_choises, blank=True)
    directors_by_user = models.ManyToManyField(User, related_name='favourite_directors', blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_absolute_url(self):
        return reverse("imdb:director-detail", kwargs={"pk": self.id})


class MovieComment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name='comments', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']


class ActorComment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='actor_comments', on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, related_name='comments', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class DirectorComment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='director_comments', on_delete=models.CASCADE)
    director = models.ForeignKey(Director, related_name='comments', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class PersonalMovieList(models.Model):
    name = models.CharField(max_length=60)
    user = models.ForeignKey(User, related_name='lists', on_delete=models.CASCADE)
    movies = models.ManyToManyField(Movie, related_name='lists', blank=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Personal lists'


class UserMovieRating(models.Model):
    user = models.ForeignKey(User, related_name='movie_ratings', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name='user_ratings', on_delete=models.CASCADE)
    value = models.FloatField(default=5.0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.value:.1f}'

    class Meta:
        ordering = ['-created']


class Genre(models.Model):
    name = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    author = models.ForeignKey(User, related_name='send_messages', on_delete=models.CASCADE)
    addressee = models.ForeignKey(User, related_name='income_messages', on_delete=models.CASCADE)
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)