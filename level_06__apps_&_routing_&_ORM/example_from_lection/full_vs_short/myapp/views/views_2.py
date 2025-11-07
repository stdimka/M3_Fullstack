__all__ = ["MyAppListView2"]


from django.views.generic import ListView
from ..models import MyappModel


class MyAppListView2(ListView):
    model = MyappModel

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        context['active_page'] = 'myapp2'
        return context
