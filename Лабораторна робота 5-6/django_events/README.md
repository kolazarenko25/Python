# Реєстрація на події — Django

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DJANGO_SECRET_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(50))')"   # Windows: set ...
python manage.py runserver          # http://127.0.0.1:8000/
python manage.py test -v 2          # автотести, у т.ч. перевірка CSRF
```
Сторінки: `/` (головна), `/events/` (список), `/register/` (форма).
