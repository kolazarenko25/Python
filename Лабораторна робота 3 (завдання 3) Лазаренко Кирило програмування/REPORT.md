# Звіт до Завдання 3

## 1. Мета

Код організовано у пакет `shop_package` із двома підпакетами:
`models` для моделей предметної області та `utils` для допоміжних функцій.
Логіка розподілена між окремими модулями без сторонніх бібліотек.

## 2. Дерево файлів

```text
task3_package_project/
├── README.md
├── REPORT.md
├── requirements.txt
└── shop_package/
    ├── __init__.py
    ├── __main__.py
    ├── app.py
    ├── models/
    │   ├── __init__.py
    │   ├── product.py
    │   └── cart.py
    └── utils/
        ├── __init__.py
        └── formatting.py
```

Призначення:
- `shop_package/__init__.py` — ініціалізація пакета, реекспорт `Product`, `Cart`, визначення `__all__`.
- `shop_package/__main__.py` — точка входу для `python -m shop_package`.
- `shop_package/app.py` — складання демонстраційного сценарію та запуск програми.
- `models/__init__.py` — реекспорт моделей підпакета.
- `models/product.py` — модель `Product`.
- `models/cart.py` — модель `Cart` і розрахунок кількості/суми.
- `utils/__init__.py` — реекспорт утиліт та визначення `__all__`.
- `utils/formatting.py` — форматування грошей і формування чека.
- `requirements.txt` — фіксує відсутність зовнішніх залежностей.
- `README.md` — коротка інструкція із запуску.

## 3. Форми імпорту

Використано щонайменше три різні форми.

### Абсолютний імпорт цілого модуля

```python
import shop_package.utils.formatting as formatting
```

### Вибірковий імпорт конкретних імен

```python
from shop_package.models import Cart, Product
```

### Відносний імпорт

У `models/cart.py`:

```python
from .product import Product
```

У `utils/formatting.py`:

```python
from ..models import Cart
```

Ці залежності спрямовані від моделей до функціоналу, що їх використовує, тому циклічних імпортів немає.

## 4. `if __name__ == "__main__"`

У `app.py` є:

```python
if __name__ == "__main__":
    run_demo()
```

Цей блок виконується, коли `app.py` запускають безпосередньо як головний модуль. Під час імпорту `shop_package.app` змінна `__name__` має значення `shop_package.app`, тому демонстраційний запуск не виконується.

Основний рекомендований запуск у цьому проєкті — `python -m shop_package`. У такому випадку Python запускає `shop_package/__main__.py`, де також є перевірка `if __name__ == "__main__"`.

## 5. `__all__` та перевірка `from package import *`

У `shop_package/__init__.py` визначено:

```python
__all__ = ["Product", "Cart", "__version__"]
```

Отже, при:

```python
from shop_package import *
```

у простір імен імпортуються лише `Product`, `Cart` та `__version__`, а не довільні внутрішні імена модуля.

У робочому коді `import *` не використовується. Для перевірки можна виконати з кореня проєкту:

```bash
python -c "from shop_package import *; print(Product, Cart, __version__)"
```

Очікується виведення класів `Product`, `Cart` та версії `1.0.0`.

## 6. Відтворюваний запуск

Залежностей сторонніх бібліотек немає. Файл `requirements.txt` містить відповідний коментар.

Запуск із кореневої директорії:

```bash
python -m shop_package
```

Приклад результату:

```text
=== ЧЕК ===
Зошит: 2 x 45.50 грн = 91.00 грн
Ручка: 3 x 18.00 грн = 54.00 грн
Разом: 145.00 грн
Кількість товарів: 5
Загальна сума: 145.00 грн
```

## 7. Висновок

Проєкт відповідає вимогам: має два підпакети та більше чотирьох модулів, осмислені `__init__.py`, три форми імпорту, `if __name__ == "__main__"`, `__all__`, `requirements.txt`, запуск через `python -m shop_package` та не використовує сторонніх бібліотек.
