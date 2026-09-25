# Завдання 3 — Організація коду в модулі та пакети

## Запуск

Із кореневої директорії проєкту:

```bash
python -m shop_package
```

Потрібен Python 3.9+.

## Структура

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

## Імпорти

У проєкті використано:
1. абсолютний імпорт цілого модуля:
   `import shop_package.utils.formatting as formatting`;
2. вибірковий імпорт:
   `from shop_package.models import Cart, Product`;
3. відносний імпорт:
   `from .product import Product` та `from ..models import Cart`.

Залежності між модулями організовані без циклічних імпортів.
