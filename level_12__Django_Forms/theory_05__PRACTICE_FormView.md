# View (представления) на основе FormView

Для работы с формами в Django использование CBV на основе `FormView` очень удобно.
Особенно если задача — просто 
- отобразить форму, 
- обработать её 
- и (при успешной валидации) 
  - перенаправить пользователя 
  - или показать сообщение.

---

### Достоинства `FormView`


1. Нет необходимости вручную писать логику GET/POST — CBV уже умеет:
   * При GET — рендерит форму.
   * При POST — валидирует форму и вызывает `form_valid` или `form_invalid`.
2. Можно легко редиректить пользователя после успешной отправки формы.
3. Легко подключать шаблоны (`template_name` и `success_url`).
4. Чистая структура — CBV разделяют логику на методы (`form_valid`, `form_invalid`).
5. Легко расширять — можно подключить миксины, логирование, проверку прав и т.д.


---

### Пример использования `FormView`

```python
# forms.py
from django import forms

class FeedbackForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
```

В базовом виде FeedbackFormView выглядит примерно так:

```python
# views.py
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import FeedbackForm

class FeedbackFormView(FormView):
    template_name = 'feedback/feedback.html'
    form_class = FeedbackForm
    success_url = reverse_lazy('feedback')

    def form_valid(self, form):
        # Здесь можно обработать данные формы, например отправить email
        print(form.cleaned_data)
        return super().form_valid(form)
```

Надо также не забыть изменить маршрут:
```python
from django.urls import path
from . import views

urlpatterns = [
    # path('', views.feedback_view, name='feedback'),
    path('', views.FeedbackFormView.as_view(), name='feedback'),
]
```

## Тестирование нового view

В качестве временной меры мы прописали в методе `form_valid()` печать  
полученных из формы значений.  
Разумеется, результат можно (и нужно!) сохранять в БД и т.д.

При тестировании видно, что в терминале вывадется словарь `cleaned_data`,  
А при удачной валидации данный view автоматически редиректит пользователя  
на указанный адрес `success_url = reverse_lazy('feedback')`  
(кстати, необязательный параметр).

Мы легко можем изменить адрес, скажем, на адрес домашней страницы:  
`success_url = reverse_lazy('home')`.


## Добавляем запись из формы в список запросов `results_list`

Давайте доработаем наше view, чтобы функционал был как прежде.
```python
class FeedbackFormView(FormView):

    def form_valid(self, form):
        # Добавляем новые данные в глобальный список results_list
        results_list.append(form.cleaned_data)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "feedback"
        context["results"] = results_list  # один раз собираем список
        return context

```



