# Реєстрація на події — Flask

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export SECRET_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(50))')"          # Windows: set ...
flask --app app run --debug         # http://127.0.0.1:5000/
python -m unittest discover -v      # автотести, у т.ч. перевірка CSRF
```
Сторінки: `/` (головна), `/events` (список), `/register` (форма).
