# Лабораторна робота №4 — «Працівник»

## Запуск у Windows PowerShell
1. `uv sync`
2. `docker compose up -d`
3. `uv run python -m app.init_db`
4. `uv run uvicorn app.main:app --reload`
5. Відкрити `http://127.0.0.1:8000/docs` та `http://127.0.0.1:8000/admin`.

Демо-ключі: `admin-demo-key` (роль admin), `read-demo-key` (роль reader).
Перед будь-яким реальним розгортанням замініть ключі та пароль БД, не публікуйте `.env`.
Демонстрація SQL-ін'єкції міститься в `app/sql_injection_demo.py` і працює лише на локальних тестових даних.
