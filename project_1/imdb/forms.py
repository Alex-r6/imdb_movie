from django.contrib.auth import get_user_model
from django.forms import ModelForm, ImageField, CharField, Form, Textarea
from django.contrib.auth.forms import UserCreationForm
from .models import *

# User = get_user_model()


class CommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = MovieComment
        fields = ['text',]
        widgets = {
            'text': Textarea(attrs={'cols':10, 'rows':3})
        }


class ActorCommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = ActorComment
        fields = ['text',]
        widgets = {
            'text': Textarea(attrs={'cols': 10, 'rows': 3})
        }


class DirectorCommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = DirectorComment
        fields = ['text',]
        widgets = {
            'text': Textarea(attrs={'cols': 10, 'rows': 3})
        }


class CreateNewActorForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Actor
        fields = ['first_name','last_name', 'birth_date', 'photo', 'sex']


class MyUserCreationForm(UserCreationForm):
    first_name = CharField()
    last_name = CharField()
    img = ImageField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class PersonalMovieListForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = PersonalMovieList
        fields = ['name',]


class SearchForm(Form):
    pattern = CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['pattern'].label = ""


class UserRatingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = UserMovieRating
        fields = ['value',]


class SendMessageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user.is_authenticated:
            self.fields['addressee'].queryset = User.objects.exclude(id=user.id)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Message
        fields = ['addressee','text']


class ReplyMessageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Message
        fields = ['text']