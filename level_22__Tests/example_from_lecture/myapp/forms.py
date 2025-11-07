from django import forms
from .models import Author, Book, BookDetail
from django.forms import inlineformset_factory, modelformset_factory


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'year_published', 'is_deleted']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'year_published': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_deleted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            # 'author': forms.RadioSelect(),

        }


class BookDetailForm(forms.ModelForm):
    class Meta:
        model = BookDetail
        fields = ['summary', 'page_count']
        widgets = {
            'summary': forms.Textarea(attrs={'class': 'form-control'}),
            'page_count': forms.NumberInput(attrs={'class': 'form-control'})
        }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя автора'
            })
        }


# InlineFormset для Book в контексте Author
BookFormSet = inlineformset_factory(
    Author,
    Book,
    fields=['title', 'year_published', 'is_deleted'],
    extra=1,
    can_delete=True,
    widgets={
        'title': forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Введите название книги'}),
        'year_published': forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'Введите год публикации книги'}),
        'is_deleted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)


# FormSet для массового редактирования записей модели Book
BookModelFormSet = modelformset_factory(
    Book,
    form=BookForm,
    extra=0,            # Не добавляем пустых форм
    can_delete=False    # Не даём удалять из формсета
)
