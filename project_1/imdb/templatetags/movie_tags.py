from django import template
from ..models import *
from ..forms import *

register = template.Library()


@register.simple_tag(name='statistics')
def get_statistics():
    n1 = Movie.objects.count()
    n2 = Actor.objects.count()
    n3 = Director.objects.count()
    return {
        'num_movies': n1,
        'num_actors': n2,
        'num_directors': n3,
    }


@register.inclusion_tag(filename='imdb/search_form.html', name='search_form_tag')
def search_form_tag():
    return {
        'search_form': SearchForm()
    }
