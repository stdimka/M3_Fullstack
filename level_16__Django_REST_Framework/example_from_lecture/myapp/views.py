from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DetailView, DeleteView)
from myapp.models import Author, Book
from .forms import BookForm, BookDetailForm
from django.contrib import messages


class BookView(LoginRequiredMixin, ListView):
    model = Book

    # def get(self, request, *args, **kwargs):
    #     messages.info(request, "Это сообщение для GET-запроса.")
    #     messages.debug(request, "Это сообщение для GET-запроса.")
    #     messages.success(request, "Это сообщение для GET-запроса.")
    #     messages.warning(request, "Это сообщение для GET-запроса.")
    #     messages.error(request, "Это сообщение для GET-запроса.")
    #     return super().get(request, *args, **kwargs)


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


