from django.contrib.auth import get_user_model
from django import forms

from .models import Post


User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {'text': 'Текст поста', 'group': '  Group'}
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }
