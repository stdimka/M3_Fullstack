### 1 Обновляем форму регистрации

По сути, нам нужно только добавить новое поле

`accounts/forms.py`

```python
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

```

На всякий случай, вот обновлённая форма полностью: 

```python
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
```

---

### 2 Обновляем вью регистрации

Все поля формы, кроме добавленного поля `phone` связаны с моделью `User`.  
Поэтому, для них мы используем `user.save()` (кроме `password`!)

А phone "вручную" записываем через `objects.create()`

`accounts/views.py`

```python

from .models import UserProfile

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # обновляем UserProfile сразу с телефоном
            # почему ОБНОВЛЯЕМ, а не СОЗДАЁМ?!!!
            # потому что после user.save() сигналы автоматически создают пустой профиль этому пользователю!!! 
            phone = form.cleaned_data.get('phone')
            user.userprofile.phone = phone
            # user.userprofile.save()
            
            # Благодаря сигналу мы можем сохранять изменения в UserProfile, сохраняя User
            user.save()

            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})
```

### 3 Самое важное!!!


В Django (и вообще в MVC-архитектуре) общая форма для редактирования для `User`, и `UserProfile` технически возможна,   
но считается **не очень хорошей практикой**, потому что:
- **Разные сущности** 
  - `User` отвечает за аутентификацию и базовые данные, 
  - а `UserProfile` — за расширенную информацию. 
  - Разделение облегчает поддержку.
  
- **Разные права доступа** 
  - например, `is_verified` обычно редактирует админ/модератор, а не сам пользователь. 
  - Если включить это поле в общую форму — можно случайно дать пользователю возможность менять то, что нельзя.
  - 
-  **Валидация** 
  - у `User` и `UserProfile` могут быть разные правила валидации. 
  - Отдельные формы позволяют их разделить и не перегружать одну большую форму кучей логики.

- **Гибкость** 
  - отдельные формы проще повторно использовать (например, регистрация, редактирование профиля, админская панель).

---

#### Как обычно делают

* **Форма регистрации** 
  * может включать часть полей из `User` + `UserProfile` (например, username, email, пароль, телефон).
* **Форма редактирования профиля** 
  * обычно отдельная форма, которая редактирует `UserProfile` (например, `phone`, аватар и т.п.).
* **Форма редактирования пользователя** 
  * если нужно, то отдельная (например, смена email, имени).



