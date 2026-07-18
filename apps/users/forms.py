from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        # By default, first user is admin, others are users
        if CustomUser.objects.count() == 0:
            user.role = 'admin'
            user.is_staff = True
            user.is_superuser = True
        else:
            user.role = 'user'
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'bio', 'status_message', 'avatar', 'cover_image', 'birth_date', 'location', 'website')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'bio', 'status_message', 'avatar', 'cover_image', 'birth_date', 'location', 'website')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Расскажите о себе...'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'status_message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Чем вы занимаетесь сегодня?'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город, Страна'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        }
