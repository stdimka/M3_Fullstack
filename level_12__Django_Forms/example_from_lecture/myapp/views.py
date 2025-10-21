from django.views.generic import ListView
from myapp.models import Book


class BookView(ListView):
    model = Book

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        context['active_page'] = 'myapp'
        return context

