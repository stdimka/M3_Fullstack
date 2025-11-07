

| Категория                  | Функция / Класс   | Импорт                                                  | Пример использования                                                                               |
| -------------------------- | ----------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **Выражения / Arithmetic** | F                 | `from django.db.models import F`                        | `annotate(discounted=F('price') - F('discount'))`                                                  |
|                            | ExpressionWrapper | `from django.db.models import ExpressionWrapper`        | `annotate(final_price=ExpressionWrapper(F('price') - F('discount'), output_field=DecimalField()))` |
|                            | Func              | `from django.db.models import Func`                     | `annotate(lower_name=Func(F('name'), function='LOWER'))`                                           |
|                            | Case / When       | `from django.db.models import Case, When`               | `annotate(status_code=Case(When(status='new', then=1), default=0))`                                |
|                            | Value             | `from django.db.models import Value`                    | `annotate(total_price=F('price') + Value(10))`                                                     |
|                            | Coalesce          | `from django.db.models import Coalesce`                 | `annotate(price=Coalesce(F('discount_price'), F('price')))`                                        |
|                            | Greatest / Least  | `from django.db.models import Greatest, Least`          | `annotate(max_price=Greatest(F('price'), F('discount_price')))`                                    |
| **Даты / Время**           | TruncYear         | `from django.db.models.functions import TruncYear`      | `annotate(year=TruncYear('created_at'))`                                                           |
|                            | TruncQuarter      | `from django.db.models.functions import TruncQuarter`   | `annotate(quarter=TruncQuarter('created_at'))`                                                     |
|                            | TruncMonth        | `from django.db.models.functions import TruncMonth`     | `annotate(month=TruncMonth('created_at'))`                                                         |
|                            | TruncWeek         | `from django.db.models.functions import TruncWeek`      | `annotate(week=TruncWeek('created_at'))`                                                           |
|                            | TruncDay          | `from django.db.models.functions import TruncDay`       | `annotate(day=TruncDay('created_at'))`                                                             |
|                            | TruncHour         | `from django.db.models.functions import TruncHour`      | `annotate(hour=TruncHour('created_at'))`                                                           |
|                            | TruncMinute       | `from django.db.models.functions import TruncMinute`    | `annotate(minute=TruncMinute('created_at'))`                                                       |
|                            | ExtractYear       | `from django.db.models.functions import ExtractYear`    | `annotate(year=ExtractYear('created_at'))`                                                         |
|                            | ExtractMonth      | `from django.db.models.functions import ExtractMonth`   | `annotate(month=ExtractMonth('created_at'))`                                                       |
|                            | ExtractDay        | `from django.db.models.functions import ExtractDay`     | `annotate(day=ExtractDay('created_at'))`                                                           |
|                            | ExtractWeek       | `from django.db.models.functions import ExtractWeek`    | `annotate(week=ExtractWeek('created_at'))`                                                         |
|                            | ExtractHour       | `from django.db.models.functions import ExtractHour`    | `annotate(hour=ExtractHour('created_at'))`                                                         |
|                            | ExtractMinute     | `from django.db.models.functions import ExtractMinute`  | `annotate(minute=ExtractMinute('created_at'))`                                                     |
|                            | ExtractSecond     | `from django.db.models.functions import ExtractSecond`  | `annotate(second=ExtractSecond('created_at'))`                                                     |
|                            | ExtractWeekDay    | `from django.db.models.functions import ExtractWeekDay` | `annotate(weekday=ExtractWeekDay('created_at'))`                                                   |
| **Строковые функции**      | Lower             | `from django.db.models.functions import Lower`          | `annotate(lower_name=Lower('name'))`                                                               |
|                            | Upper             | `from django.db.models.functions import Upper`          | `annotate(upper_name=Upper('name'))`                                                               |
|                            | Length            | `from django.db.models.functions import Length`         | `annotate(name_len=Length('name'))`                                                                |
|                            | Concat            | `from django.db.models.functions import Concat`         | `annotate(full_name=Concat('first_name', Value(' '), 'last_name'))`                                |
|                            | Substr            | `from django.db.models.functions import Substr`         | `annotate(code=Substr('sku', 1, 3))`                                                               |
|                            | Trim              | `from django.db.models.functions import Trim`           | `annotate(trimmed_name=Trim('name'))`                                                              |
|                            | Replace           | `from django.db.models.functions import Replace`        | `annotate(fixed_name=Replace('name', 'a', 'o'))`                                                   |
| **Агрегаты / Math**        | Count             | `from django.db.models import Count`                    | `annotate(num_orders=Count('id'))`                                                                 |
|                            | Sum               | `from django.db.models import Sum`                      | `annotate(total=Sum('amount'))`                                                                    |
|                            | Avg               | `from django.db.models import Avg`                      | `annotate(avg_price=Avg('price'))`                                                                 |
|                            | Max               | `from django.db.models import Max`                      | `annotate(max_price=Max('price'))`                                                                 |
|                            | Min               | `from django.db.models import Min`                      | `annotate(min_price=Min('price'))`                                                                 |
|                            | StdDev            | `from django.db.models import StdDev`                   | `annotate(std=StdDev('price'))`                                                                    |
|                            | Variance          | `from django.db.models import Variance`                 | `annotate(var=Variance('price'))`                                                                  |

---

Это классы (функции), которые используются как выражения для аннотаций (`annotate`) и вычислений в Django ORM.   
Их цель — преобразовывать, извлекать или агрегировать данные прямо на уровне базы данных, чтобы не обрабатывать их в Python.

Кратко по категориям:

---

### 1️⃣ Выражения / Arithmetic

* **F** – ссылается на поле модели для вычислений.
* **ExpressionWrapper** – оборачивает выражение, чтобы задать тип вывода (например, Decimal).
* **Func** – обёртка для произвольной SQL-функции.
* **Case / When** – условные выражения (`if/else`) на уровне SQL.
* **Value** – константа в выражении.
* **Coalesce** – возвращает первое ненулевое значение из списка.
* **Greatest / Least** – выбирает максимум/минимум из выражений.

---

### 2️⃣ Даты / Время

* **Trunc…** (Year, Month, Day…) – обрезает дату/время до указанного уровня (год, месяц, день…).
* **Extract…** (Year, Month, Day, WeekDay…) – извлекает часть даты/времени как число (например, номер месяца или день недели).

---

### 3️⃣ Строковые функции

* **Lower / Upper** – переводят строку в нижний/верхний регистр.
* **Length** – длина строки.
* **Concat** – объединение строк.
* **Substr** – подстрока.
* **Trim** – обрезает пробелы по краям.
* **Replace** – заменяет символы или подстроки.

---

### 4️⃣ Агрегаты / Math

* **Count** – подсчёт строк.
* **Sum** – сумма значений.
* **Avg** – среднее значение.
* **Max / Min** – максимум/минимум.
* **StdDev / Variance** – стандартное отклонение и дисперсия.


