# documents/forms.py
from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    # Arquivo não é obrigatório aqui (pois pode ser texto)
    file = forms.FileField(label="Arquivo (PDF, Imagem, etc)", required=False)
    
    # Campo de texto para criação direta
    text_content = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Digite aqui o conteúdo confidencial para criar um arquivo seguro automaticamente...',
            'rows': 5,
            'style': 'width: 100%;'
        }), 
        required=False, 
        label="Ou crie um documento de texto:"
    )

    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'text_content', 'classification']

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        text = cleaned_data.get('text_content')

        if not file and not text:
            raise forms.ValidationError("ERRO: Você deve anexar um arquivo OU digitar um texto.")
        
        return cleaned_data