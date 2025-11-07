
Библиотека **`drf-yasg`** умеет использовать *docstrings* (строки документации)   
непосредственно из кода (из вью, сериализаторов и даже моделей),  
**но не всегда автоматически и не во всех местах**.


## Docstring у view или метода — да, используется

Если в классе или методе есть docstring, `drf-yasg` его подхватывает и отображает в Swagger UI.
Пример:

```python
from rest_framework.views import APIView
from rest_framework.response import Response

class AuthorViewSet(viewsets.ModelViewSet):
    """
    Этот endpoint возвращает информацию об Авторе.
    (будет повторено в КАЖДОМ эндпойнте, 
    если только в методе эндпойнта не будет своего собственного docstring)
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def list(self, request, *args, **kwargs):
        """А этот текст будет виден ТОЛЬКО в Authors GET
        И он полностью заменит текст из view docstring
        """
        return super().list(request, *args, **kwargs)
```

В Swagger UI:

* Описание класса появится **в верхней части раздела эндпоинта**.
* Описание метода появится **под кнопкой GET**, рядом с параметрами запроса.

---

## 2. При использовании `swagger_auto_schema` docstring можно переопределить

Если вы хотите изменить текст только для Swagger, без изменения реального docstring,
используйте параметр `operation_description` или `operation_summary`:

```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class BookViewSet(viewsets.ModelViewSet):

    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @swagger_auto_schema(
        operation_description="Получить список объектов Books",
        responses={200: openapi.Response("Список объектов")}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

Здесь **Swagger покажет только** `operation_description`,
а реальный docstring останется для IDE и автодокументации.

---

## 3. Docstring из сериализаторов и моделей

`drf-yasg` может использовать:

* описание из `help_text` в полях сериализатора / модели;
* `verbose_name` из модели.
* `extra_kwargs` из мета-класса сериализатора

Например:

```python
from rest_framework import serializers

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "year_published", "author"]
        extra_kwargs = {
            "title": {"help_text": "Название книги"},
            "year_published": {"help_text": "Год публикации"},
            "author": {"help_text": "Автор книги"},
        }

```

В Swagger эти подсказки появятся как описание параметров в теле запроса.

---

## 4. Поддержка GenericAPIView

Для `ViewSet` и `GenericAPIView` `drf-yasg` тоже считывает docstrings.
Если у вас, например, `ListAPIView`:

```python
class UserListView(ListAPIView):
    """
    Возвращает список пользователей с возможностью фильтрации.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

Swagger возьмёт этот docstring как описание для `GET /users/`.

---

## ⚠️ 5. Важно знать

* Если вы используете **mixins или viewsets**, и docstring не отображается —
  можно добавить `swagger_auto_schema` с `auto_schema=None`, чтобы указать вручную.
* `drf-yasg` не парсит *встроенные Python docstring форматы* (например, reStructuredText или Google-style) —
  он просто отображает текст как есть.

---

👉 **Вывод:**
Да, Swagger (через `drf-yasg`) может считывать docstrings,
но:

* для лучших результатов используйте `swagger_auto_schema`;
* используйте `help_text` и `verbose_name` для полей;
* при сложных структурах лучше комбинировать docstring + явное описание.

