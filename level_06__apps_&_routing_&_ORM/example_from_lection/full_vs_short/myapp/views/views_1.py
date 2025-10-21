__all__ = ["MyAppListView"]

from django.views.generic import ListView
from ..models import MyappModel


class MyAppListView(ListView):
    model = MyappModel

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        context['active_page'] = 'myapp'
        return context
