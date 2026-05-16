from django import forms
from .models import Worksheet, WorksheetPage


class WorksheetForm(forms.ModelForm):
    pdf_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'accept': '.pdf,application/pdf', 'class': 'hidden'}),
    )

    class Meta:
        model = Worksheet
        fields = ('title', 'description', 'subject', 'level', 'language', 'grading_system', 'tags', 'is_public')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Çalışma kağıdı başlığı'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            # grading_system: create.html'de hidden input ile gönderilir,
            # burada HiddenInput kullanarak form çakışmasını önlüyoruz
            'grading_system': forms.HiddenInput(),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'matematik, toplama, 2. sınıf'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }



class WorksheetPageForm(forms.ModelForm):
    class Meta:
        model = WorksheetPage
        fields = ('background_image', 'audio_file', 'audio_url', 'text_to_speech_text', 'text_to_speech_lang')
        widgets = {
            'audio_url': forms.URLInput(attrs={'class': 'form-input'}),
            'text_to_speech_text': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'text_to_speech_lang': forms.Select(attrs={'class': 'form-select'}),
        }
