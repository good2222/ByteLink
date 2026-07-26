from django import forms
from .models import Group


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'description', 'avatar', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название группы',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите, о чём ваша группа...',
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
