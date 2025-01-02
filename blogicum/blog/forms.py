from django import forms
from .models import Post, Comment
from django.contrib.auth import get_user_model


User = get_user_model()


class PostCreationForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'last_name', 'email', 'first_name')


class CommentCreationForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
