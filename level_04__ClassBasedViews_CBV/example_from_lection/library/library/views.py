from django.views import generic
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from .forms import ContactForm
from .models import Book


class BookListView(generic.ListView):
    # model = Book
    # template_name = "library/book_list.html"  # по умолчанию: library/book_list.html
    context_object_name = "books"  # в шаблоне переменная будет books (вместо object_list)
    paginate_by = 10  # по 10 книг на страницу

    def get_queryset(self):
        # return Book.objects.filter(author__icontains="Толстой")
        return Book.objects.all()


class BookDetailView(generic.DetailView):
    model = Book
    # template_name = "library/book_detail.html"
    context_object_name = "book"


class BookCreateView(generic.CreateView):
    model = Book
    fields = ["title", "author", "year", "description"]
    template_name = "library/book_form.html"
    success_url = reverse_lazy("books")  # редирект после успешного добавления


class BookUpdateView(generic.UpdateView):
    model = Book
    fields = ["title", "author", "year", "description"]
    template_name = "library/book_form.html"  # тот же шаблон, что и у CreateView
    success_url = reverse_lazy("books")  # редирект после сохранения


class BookDeleteView(generic.DeleteView):
    model = Book
    template_name = "library/book_confirm_delete.html"
    success_url = reverse_lazy("books")
    context_object_name = "book"


class ContactFormView(FormView):
    template_name = "library/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact-success")

    def form_valid(self, form):
        # здесь можно отправить email, записать в лог, сохранить в БД и т.д.
        print("Сообщение отправлено:")
        print("Имя:", form.cleaned_data["name"])
        print("Email:", form.cleaned_data["email"])
        print("Сообщение:", form.cleaned_data["message"])

        # Только здесь и только для примера сохраним в лог-файле
        with open("contact_messages.log", "a", encoding="utf-8") as f:
            f.write(f"{form.cleaned_data['name']} — {form.cleaned_data['email']}\n")
            f.write(f"{form.cleaned_data['message']}\n\n")

        return super().form_valid(form)