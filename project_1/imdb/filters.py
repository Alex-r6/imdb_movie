import django_filters
from django.forms import TextInput, Select, SelectMultiple

from .models import *


class MovieFilter(django_filters.FilterSet):
    rating_min = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='gte',
        label='min rating',
        widget=TextInput(attrs={'class': 'form-control'})
    )
    rating_max = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='lte',
        label='max rating',
        widget=TextInput(attrs={'class': 'form-control'})
    )
    director = django_filters.ModelChoiceFilter(
        queryset=Director.objects.all(),
        widget=Select(attrs={'class': 'form-select'})
    )
    genres = django_filters.ModelMultipleChoiceFilter(
        queryset=Genre.objects.all(),
        conjoined=True,
        widget=SelectMultiple(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Movie
        fields = ['rating_min', 'rating_max', 'director', 'genres']


class ActorFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        field_name='first_name',
        lookup_expr='icontains',
        label="Actor name",
        widget=TextInput(attrs={'class': 'form-control'})
    )
    birth_date = django_filters.CharFilter(
        field_name='birth_date',
        lookup_expr='icontains',
        label='birth_date',
        widget=TextInput(attrs={'class': 'form-control'})
    )

    movie = django_filters.ModelChoiceFilter(
        queryset=Movie.objects.order_by('title'),
        widget=Select(attrs={'class': 'form-select'}),
        label='select movie',
        field_name='movies'
    )

    director = django_filters.ModelChoiceFilter(
        queryset=Director.objects.order_by('last_name'),
        widget=Select(attrs={'class': 'form-select'}),
        label='select director',
        field_name='movies__director'
    )

    class Meta:
        model = Actor
        fields = ['first_name', 'birth_date', 'movie', 'director']


class ActorFilterByName(django_filters.FilterSet):
    pattern = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')

    class Meta:
        model = Actor
        fields = ['pattern']
