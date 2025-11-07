## Подготовка к практической работе с проектом

### Создание (перенос) проекта

1. Создаём папку проекта
1. Копируем файлы из [example_from_lecture](./example_from_lecture) 
1. Переименовываем `db.sqlite3--` в `db.sqlite3`
1. Создаём виртуальное окружение `pyton3 -m venv .venv`
1. Активируем его `source .venv/bin/activate`
1. Устанавливаем пакеты `pip install -r requirements.txt`

### БД 

1. Заполнены модели авторов, книг, детализации и жанров
1. Зарегистрирован супер-администратор `root` с паролем `123`


### Данные Models, Urls, Forms, Views:

`myapp/models.py`

```python
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=200)
    year_published = models.IntegerField()
    is_deleted = models.BooleanField(default=False)


class BookDetail(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='detail')
    summary = models.TextField()
    page_count = models.IntegerField()


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    books = models.ManyToManyField(Book, related_name='genres')
```

`myapp/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookView.as_view(), name='book_list'),

    path('book/add-cbv/', views.BookCreateView.as_view(), name='book_create'),
    path('book/<int:pk>/edit-cbv/', views.BookUpdateView.as_view(), name='book_update'),
    path('book/<int:pk>/cbv/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<int:pk>/delete-cbv/', views.BookDeleteView.as_view(), name='book_delete'),

    path('author-list/', views.AuthorListView.as_view(), name='author_list'),
    path('author-edit/<int:pk>/', views.author_edit, name='author_edit'),

    path("edit_all_books/", views.edit_all_books, name="edit_all_books"),
]
```

`myapp/forms.py`

```python
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
```

`myapp/views.py`

```python
class BookView(LoginRequiredMixin, ListView):
    model = Book


class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'myapp/book_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_form'] = BookForm(self.request.POST or None)
        context['detail_form'] = BookDetailForm(self.request.POST or None)
        context['form_action'] = 'Создать'
        return context

    def form_valid(self, form):
        detail_form = BookDetailForm(self.request.POST)
        if detail_form.is_valid():
            book = form.save()
            detail = detail_form.save(commit=False)
            detail.book = book
            detail.save()
            return redirect('book_list')
        return self.form_invalid(form)


class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'myapp/book_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        detail = getattr(self.object, 'detail', None)
        context['book_form'] = BookForm(self.request.POST or None, instance=self.object)
        context['detail_form'] = BookDetailForm(self.request.POST or None, instance=detail)
        context['form_action'] = 'Обновить'
        return context

    def form_valid(self, form):
        detail = getattr(self.object, 'detail', None)
        detail_form = BookDetailForm(self.request.POST, instance=detail)
        if detail_form.is_valid():
            book = form.save()
            detail = detail_form.save(commit=False)
            detail.book = book
            detail.save()
            messages.success(self.request, "Форма успешно отправлена!")
            return redirect('book_list')
        return self.form_invalid(form)


class BookDetailView(DetailView):
    model = Book
    template_name = 'myapp/book_detail.html'
    context_object_name = 'book'


class BookDeleteView(DeleteView):
    model = Book
    template_name = 'myapp/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')
    context_object_name = 'book'


class AuthorListView(ListView):
    model = Author
    template_name = 'myapp/author_list.html'
    context_object_name = 'authors'
    
    
from .forms import AuthorForm, BookFormSet, BookModelFormSet


@login_required()
def author_edit(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        formset = BookFormSet(request.POST, instance=author)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()  # сохраняются все книги вместе
            return redirect('author_list')
    else:
        form = AuthorForm(instance=author)
        formset = BookFormSet(instance=author)
    return render(request, 'myapp/author_edit.html', {'form': form, 'formset': formset})


def edit_all_books(request):
    if request.method == "POST":
        formset = BookModelFormSet(request.POST, queryset=Book.objects.all())
        if formset.is_valid():
            formset.save()
            return redirect("edit_all_books")  # Перезагрузка страницы после сохранения
    else:
        formset = BookModelFormSet(queryset=Book.objects.all())

    return render(request, "myapp/edit_all_books.html", {"formset": formset})
```
