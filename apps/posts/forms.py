from django import forms
from django.utils.translation import get_language
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'required': True
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = get_language() or 'uk'
        if lang == 'ru':
            self.fields['content'].widget.attrs['placeholder'] = 'Что у вас нового?'
        else:
            self.fields['content'].widget.attrs['placeholder'] = 'Що у вас нового?'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'required': True
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = get_language() or 'uk'
        if lang == 'ru':
            self.fields['text'].widget.attrs['placeholder'] = 'Напишите комментарий...'
        else:
            self.fields['text'].widget.attrs['placeholder'] = 'Написати коментар...'

