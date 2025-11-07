from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


# Конфигурация по умолчанию (достаточно краткого пути)
class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'


# Кастомная конфигурация (необходим полный путь к MyappAutoInitConfig)
class MyappAutoInitConfig(MyappConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    verbose_name = 'My App with Auto Init'

    def ready(self):
        # Защитный импорт внутри метода (избегает проблем с ранним импортом)
        from .models import MyappModel

        try:
            # Проверка существования записи с кодом 'default'
            if not MyappModel.objects.filter(code='default').exists():
                MyappModel.objects.create(code='default', value='Автоматически добавлено')
        except (OperationalError, ProgrammingError) as e:
            # База может быть не готова (например, миграции ещё не применены)
            print(e)
