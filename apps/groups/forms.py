from django import forms
from .models import Group


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'description', 'avatar', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'required': True
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils.translation import get_language
        lang = get_language() or 'uk'
        if lang == 'ru':
            self.fields['title'].widget.attrs['placeholder'] = 'Название группы'
            self.fields['description'].widget.attrs['placeholder'] = 'Расскажите, о чём ваша группа...'
        else:
            self.fields['title'].widget.attrs['placeholder'] = 'Назва групи'
            self.fields['description'].widget.attrs['placeholder'] = 'Розкажіть, про що ваша група...'

