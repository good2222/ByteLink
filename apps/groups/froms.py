from django import forms

class GroupForm(forms.Form):
    title = forms.CharField(max_length=200, label='Название группы', widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), label='Описание группы')
    avatar = forms.ImageField(required=False, label='Аватар группы', widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))
    cover_image = forms.ImageField(required=False, label='Обложка группы', widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))