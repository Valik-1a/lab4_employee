import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/employee_db",
)
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin-demo-key")
READ_API_KEY = os.getenv("READ_API_KEY", "read-demo-key")
