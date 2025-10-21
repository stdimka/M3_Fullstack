from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import FeedbackForm

# Дла удобства будем хранить и отражать на странице
# результаты нескольких вводов в форму
results_list = []


# def feedback_view(request):
#     global results_list
#     if request.method == "POST":
#         form = FeedbackForm(request.POST)
#         if form.is_valid():
#             # Получаем данные
#             name = form.cleaned_data['name']
#             email = form.cleaned_data['email']
#             message = form.cleaned_data['message']
#
#             # Добавляем результат в список
#             results_list.append({
#                 "name": name,
#                 "email": email,
#                 "message": message
#             })
#
#             # Сброс формы
#             form = FeedbackForm()
#     else:
#         form = FeedbackForm()
#
#     return render(request, "feedback/feedback.html", {
#         "active_page": 'feedback',
#         "form": form,
#         "results": results_list  # передаём все результаты в шаблон
#     })


class FeedbackFormView(FormView):
    template_name = 'feedback/feedback.html'
    form_class = FeedbackForm
    success_url = reverse_lazy('feedback')

    def form_valid(self, form):
        # Добавляем новые данные в глобальный список results_list
        results_list.append(form.cleaned_data)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "feedback"
        context["results"] = results_list  # один раз собираем список
        return context
