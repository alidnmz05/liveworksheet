from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Classroom


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400',
               'placeholder': 'E-posta adresiniz'}
    ))
    first_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400',
               'placeholder': 'Adınız'}
    ))
    last_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400',
               'placeholder': 'Soyadınız'}
    ))
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'mr-2'})
    )
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400',
               'placeholder': 'Şifre'}
    ))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400',
               'placeholder': 'Şifre tekrar'}
    ))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'bio', 'school', 'country')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'school': forms.TextInput(attrs={'class': 'form-input'}),
            'country': forms.TextInput(attrs={'class': 'form-input'}),
        }


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Sınıf adı'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
