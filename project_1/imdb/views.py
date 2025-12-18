from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, YearArchiveView, UpdateView, DeleteView
from django.contrib import messages
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.views import FilterView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, CreateAPIView, DestroyAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser,IsAuthenticated

from .filters import *
from .forms import *
from .models import *
from .serializers import *

# def index(request):
#     return render(
#         request,
#         template_name='imdb/index.html'
#     )


class IndexView(TemplateView):
    template_name ='imdb/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_movies'] = Movie.objects.order_by('-rating')[:6]
        context['top_actors_male'] = Actor.objects.filter(sex='M').annotate(avg_rating=Avg('movies__rating')).order_by('-avg_rating')[:6]
        context['top_actors_female'] = Actor.objects.filter(sex='F').annotate(avg_rating=Avg('movies__rating')).order_by('-avg_rating')[:6]
        context['top_directors'] = Director.objects.annotate(avg_rating=Avg('movies__rating')).order_by('-avg_rating')[:6]
        context['all_movies'] = Movie.objects.order_by('date').distinct()
        context['all_years'] = Movie.objects.values(year=models.functions.Extract('date', 'year')).annotate(num=Count('id')).order_by('year')
        # context['search_form'] = SearchForm()
        return context


class ActorListView(ListView):
    # model = Actor
    queryset = Actor.objects.order_by('last_name').annotate(actor_rating=Avg('movies__rating', default=0.0))
    paginate_by = 6


class ActorDetailView(DetailView):
    model = Actor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actor_movies'] = self.object.movies.order_by('-date__year')
        context['actor_rating'] = self.object.movies.aggregate(Avg("rating"))['rating__avg']
        if self.object.movies.exists():
            context['actor_trailer'] = self.object.movies.values_list('trailer', flat=True).order_by('?')[0]
        else:
            context['actor_trailer'] = 'https://www.youtube.com/watch?v=D7VcGasH8pw'
        context['actor_comment'] = ActorCommentForm()
        return context


class MovieDetailView(DetailView):
    model = Movie

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movie_rating'] = Movie.objects.filter(id=self.object.id).aggregate(Avg("rating"))['rating__avg']
        context['comment_form'] = CommentForm()
        if self.request.user.is_authenticated:
            context['movie_count_in_lists'] = PersonalMovieList.objects.filter(movies=self.object).exclude(user=self.request.user).count()
            context['movie_count_in_myList'] = PersonalMovieList.objects.filter(movies=self.object, user=self.request.user).count()
            context['user_rating_form'] = UserRatingForm()
            if UserMovieRating.objects.filter(user=self.request.user, movie=self.object).exists():
                context['user_rating'] = UserMovieRating.objects.get(user=self.request.user, movie=self.object)
            else:
                context['user_rating'] = None
            context['similar_movies'] = Movie.objects.exclude(id=self.object.id).filter(genres__in=self.object.genres.all()).distinct().annotate(num_genres=Count('genres')).order_by('-num_genres')[:3]
        return context


class MovieListView(ListView):
    queryset = Movie.objects.order_by('title')
    context_object_name = 'movies'


class MovieYearArchiveView(YearArchiveView):
    queryset = Movie.objects.all()
    date_field = "date"
    make_object_list = True
    allow_future = True


class DirectorListView(ListView):
    # model = Director
    queryset = Director.objects.order_by('last_name', 'first_name').annotate(avg_rating=Avg('movies__rating', default=0.0), num_movies=Count('movies'))
    context_object_name = 'directors'
    paginate_by = 6


class DirectorDetailView(DetailView):
    model = Director

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['director_movies'] = self.object.movies.order_by('-date__year')
        context['director_rating'] = self.object.movies.aggregate(Avg("rating"))['rating__avg']
        context['director_comment'] = DirectorCommentForm()
        if self.object.movies.exists():
            context['director_trailer'] = self.object.movies.values_list('trailer', flat=True).order_by('?')[0]
        else:
            context['director_trailer'] = 'https://www.youtube.com/watch?v=D7VcGasH8pw'
        return context


def login_view(request):
    return render(
            request,
            template_name='imdb/authorization.html'
        )


def logout_view(request):
    logout(request)
    return redirect('imdb:index')


def login_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username and password:
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
        else:
            messages.add_message(request, messages.INFO, 'Enter valid username and password')
            return redirect('imdb:login-view')
    else:
        messages.add_message(request, messages.INFO, 'Enter all fields')
        return redirect('imdb:login-view')
    return redirect('imdb:index')


def add_new_comment2(request, pk):
    f = CommentForm(request.POST)
    movie = Movie.objects.get(id=pk)
    if f.is_valid():
        new_comment = f.save(commit=False)
        new_comment.movie = movie
        new_comment.author = request.user
        new_comment.save()
    return HttpResponseRedirect(reverse('imdb:movie-detail', kwargs={'slug': movie.slug}))


def add_new_comment(request, pk):
    author = request.user
    text = request.POST.get('text')
    movie = get_object_or_404(Movie, pk=pk)

    if author and text:
        MovieComment.objects.create(
            author=author,
            text=text,
            movie=movie
        )
    return HttpResponseRedirect(reverse('imdb:movie-detail', kwargs={'slug': movie.slug}))


def add_actor_comment(request,pk):
    f = ActorCommentForm(request.POST)
    actor = Actor.objects.get(id=pk)
    if f.is_valid():
        new_comment = f.save(commit=False)
        new_comment.actor = actor
        new_comment.author = request.user
        new_comment.save()
    return HttpResponseRedirect(reverse('imdb:actor-detail', kwargs={'pk': actor.id}))


def add_director_comment(request,pk):
    form = DirectorCommentForm(request.POST)
    director = Director.objects.get(id=pk)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.director = director
        new_comment.author = request.user
        new_comment.save()
    return HttpResponseRedirect(reverse('imdb:director-detail', kwargs={'pk': director.id}))


def create_actor_view(request):
    f = CreateNewActorForm()
    return render(
        request,
        template_name='imdb/add_actor.html',
        context={'f': f}
    )


def add_new_actor(request):
    f = CreateNewActorForm(request.POST, request.FILES)
    if f.is_valid():
        new_actor = f.save(commit=False)
        new_actor.photo = f.cleaned_data['photo']
        new_actor.save()
        return redirect(new_actor.get_absolute_url())
    else:
        print(f.errors)
    # return redirect('imdb:actor-list')
    return render(request, 'imdb/add_actor.html', {'f': f})


class CreateAccountView(TemplateView):
    template_name = 'imdb/create_account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['f'] = MyUserCreationForm()
        return context


def create_new_account(request):
    username = request.POST.get('username')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    img = request.FILES.get('img')
    if username and password1 and password1 == password2 and img and first_name and last_name:
        new_user = User.objects.create_user(username=username, password=password1, first_name=first_name,
                                            last_name=last_name)
        new_profile = Profile.objects.create(user=new_user, img=img)
        login(request,new_user)
        return redirect('imdb:index')
    else:
        messages.add_message(request, messages.INFO, 'You must fill all fields')
        return redirect('imdb:create-account-page')


def update_watchlist(request, pk):
    movie = Movie.objects.get(id=pk)
    user = request.user
    if user in movie.users_to_watch.all():
        movie.users_to_watch.remove(user)
    else:
        movie.users_to_watch.add(user)
    return HttpResponseRedirect(movie.get_absolute_url())


class PersonalMovieListsView(TemplateView):
    template_name = 'imdb/user_movie_lists.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['movie_list_list'] = user.lists.all()
        context['form'] = PersonalMovieListForm()
        return context


def add_personal_movie_list(request):
    form = PersonalMovieListForm(request.POST)
    if form.is_valid():
        new_lst = form.save(commit=False)
        new_lst.user = request.user
        new_lst.save()
    return HttpResponseRedirect(reverse('imdb:user-movie-lists'))


def add_movie_to_personal_movie_list(request, pk):
    movie = Movie.objects.get(id=pk)
    list_id = request.POST.get('list_id')
    if list_id != '0':
        lst = PersonalMovieList.objects.get(id=list_id)
        if movie not in lst.movies.all():
            lst.movies.add(movie)
    return HttpResponseRedirect(movie.get_absolute_url())


def remove_movie_from_personal_movie_list(request, pk1,pk2):
    movie = Movie.objects.get(id=pk1)
    lst = PersonalMovieList.objects.get(id=pk2)
    if movie in lst.movies.all():
        lst.movies.remove(movie)
    return HttpResponseRedirect(reverse('imdb:user-movie-lists'))


def search(request):
    pattern = request.POST.get('pattern')
    movie_list = Movie.objects.filter(title__istartswith=pattern)
    actor_list = Actor.objects.filter(Q(first_name__istartswith=pattern) | Q(last_name__istartswith=pattern)).annotate(avg_rating=Avg("movies__rating", default=0.0))
    director_list = Director.objects.filter(Q(first_name__istartswith=pattern) | Q(last_name__istartswith=pattern)).annotate(avg_rating=Avg("movies__rating", default=0.0))
    context = {}
    context['movie_list'] = movie_list
    context['actor_list'] = actor_list
    context['director_list'] = director_list
    context['pattern'] = pattern
    return render(request, template_name='imdb/search.html', context=context)


def set_user_rate(request, pk):
    form = UserRatingForm(request.POST)
    movie = Movie.objects.get(id=pk)
    if form.is_valid():
        new_rate = form.save(commit=False)
        new_rate.user = request.user
        new_rate.movie = movie
        new_rate.save()
    return HttpResponseRedirect(reverse('imdb:movie-detail', kwargs={'slug': movie.slug}))


class UserProfileView(UpdateView):
    model = User
    template_name = 'imdb/user_profile.html'
    context_object_name = 'current_user'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('imdb:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_message_num'] = Message.objects.filter(is_read=False, addressee=self.object).count()
        return context


class MovieByGenreView(DetailView):
    model = Genre
    template_name = 'imdb/movie_by_genre.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre'] = self.object
        context['movies_by_genre'] = Movie.objects.filter(genres=self.object)
        return context


class MovieCommentUpdateView(UpdateView):
    model = MovieComment
    fields = ['text']

    def get_success_url(self):
        return reverse('imdb:user-profile', kwargs={'pk':self.object.author.id})


class MovieCommentDeleteView(DeleteView):
    model = MovieComment

    def get_success_url(self):
        return reverse('imdb:user-profile', kwargs={'pk':self.object.author.id})


class ShowMessageView(LoginRequiredMixin, TemplateView):
    template_name = 'imdb/message_view.html'
    login_url = reverse_lazy('imdb:login-view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_form'] = SendMessageForm(user=self.request.user)
        return context


def send_message(request):
    form = SendMessageForm(request.POST)
    if form.is_valid():
        new_message = form.save(commit=False)
        new_message.author = request.user
        new_message.save()
    return HttpResponseRedirect(reverse('imdb:user-profile', kwargs={'pk': request.user.id}))


class MessageListView(ListView):
    model = Message
    template_name = 'imdb/message_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['income_message_list'] = Message.objects.filter(addressee=self.request.user)
        context['sent_message_list'] = Message.objects.filter(author=self.request.user)
        return context


class MessageDetailView(DetailView):
    model = Message

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.addressee == self.request.user:
            obj.is_read = True
            obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        created_str = self.object.created.strftime('%Y-%m-%d %H:%M:%S')
        context['reply_form'] = ReplyMessageForm(initial={'text':'\n' + '-' * 20 + f'\nreply to {self.object.author}\n{created_str}:\n{self.object.text}'})
        return context


def reply_message(request):
    form = ReplyMessageForm(request.POST)
    author_id = request.POST.get('author_id')
    addressee_id = request.POST.get('addressee_id')
    if form.is_valid():
        reply = form.save(commit=False)
        reply.author = User.objects.get(id=author_id)
        reply.addressee = User.objects.get(id=addressee_id)
        reply.save()
    return HttpResponseRedirect(reverse('imdb:message-list-view'))


def get_to_message_list(request):
    return redirect(reverse('imdb:message-list-view'))


class FilterMovieListView(FilterView, ListView):
    queryset = Movie.objects.order_by('title')
    # queryset = Movie.objects.order_by('title').filter(rating__lte=8)
    template_name = 'imdb/filter_movie_list.html'
    context_object_name = 'movies'
    filterset_class = MovieFilter


class FilterActorListView(FilterView, ListView):
    queryset = Actor.objects.all()
    template_name = 'imdb/filter_actor_list.html'
    filterset_class = ActorFilter


class DirectorListAPIView(ListAPIView):
    queryset = Director.objects.all()
    serializer_class = DirectorSerializer1


class ActorListAPIView(ListAPIView):
    queryset = Actor.objects.filter(sex='M')
    serializer_class = ActorSerializer


class MovieListAPIView(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class ActorDetailAPIView(RetrieveAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializerDetail


class DirectorUpdateAPIView(UpdateAPIView):
    queryset = Director.objects.all()
    serializer_class = DirectorSerializer1


class CreateMovieCommentAPIView(CreateAPIView):
    queryset = MovieComment.objects.all()
    serializer_class = CreateMovieCommentSerializer
    permission_classes = [IsAdminUser]


class CreateMovieCommentAPIView2(CreateAPIView):
    queryset = MovieComment.objects.all()
    serializer_class = CreateMovieCommentSerializer2
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class DestroyMovieCommentAPIView(DestroyAPIView):
    queryset = MovieComment.objects.all()
    serializer_class = CreateMovieCommentSerializer2
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы можете удалять только свои объекты.")
        instance.delete()


class MessageListAPIView(ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class CreateMessageAPIView(CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer2
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UpdateMessageAPIView(RetrieveUpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer2


class DestroyMessageAPIView(DestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer2
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы можете удалять только свои объекты.")
        instance.delete()


class PersonalMovieListAPIView(ListAPIView):
    queryset = PersonalMovieList.objects.all()
    serializer_class = PersonalMovieListSerializer


class UpdatePersonalMovieListAPIView(RetrieveUpdateAPIView):
    queryset = PersonalMovieList.objects.all()
    serializer_class = PersonalMovieListSerializer2
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class SinglePageActorsListAPIView(ListAPIView):
    queryset = Actor.objects.order_by('last_name').annotate(num_movies=Count('movies'), avg_rating=Avg('movies__rating', default=0.0))
    serializer_class = SinglePageActorsListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ActorFilterByName


class SinglePageMovieListAPIView(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = SinglePageMovieListSerializer

