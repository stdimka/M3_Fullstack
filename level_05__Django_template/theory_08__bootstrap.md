Есть несколько вариантов скачать **CSS** и **JS** файлы из **Bootstrap**
---

## 🔹 Вариант 1: Скачивание с официального сайта

1. Перейдите на официальный сайт [https://getbootstrap.com](https://getbootstrap.com)

2. Нажмите кнопку **"Download"** (или «Скачать»):

   * Прямая ссылка: [https://getbootstrap.com/docs/5.3/getting-started/download/](https://getbootstrap.com/docs/5.3/getting-started/download/)

3. Там будут такие опции:

   * **Compiled CSS and JS** – уже скомпилированные файлы (это то, что тебе нужно для использования).
   * **Source files** – исходные файлы SCSS, если хочешь настраивать Bootstrap под себя.

4. Скачайте архив **Compiled CSS and JS**, распакуйте его.

5. Внутри будут папки:

   ```
   /css/
     bootstrap.min.css
   /js/
     bootstrap.bundle.min.js
   ```

Надо добавить их в Django-проект следующим образом:
```
project/
│
├── static/
│   ├── bootstrap/
│   │   ├── css/
│   │   │   └── bootstrap.min.css
│   │   └── js/
│   │       └── bootstrap.bundle.min.js
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── script.js

```

---

## 🔹 Вариант 2: Подключение через CDN (если скачивать не обязательно)

```html
<!-- CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- JS (включает Popper) -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
```

👉 Этот способ хорош для быстрого старта или тестов.

---

## 🔹 Вариант 3: Установка через npm (для проектов с Node.js)

```bash
npm install bootstrap
```

Затем в коде подключаешь так:

```js
// JS
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
// CSS
import 'bootstrap/dist/css/bootstrap.min.css';
```
