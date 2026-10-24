"""Навчальна демонстрація на локальній тимчасовій БД SQLite; не підключається до production."""

import sqlite3


def run_demo() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE employees (id INTEGER PRIMARY KEY, full_name TEXT)")
    connection.executemany(
        "INSERT INTO employees (full_name) VALUES (?)",
        [("Олена Працівник",), ("Іван Працівник",)],
    )
    malicious = "' OR '1'='1"
    vulnerable_query = f"SELECT id, full_name FROM employees WHERE full_name = '{malicious}'"
    safe_query = "SELECT id, full_name FROM employees WHERE full_name = ?"
    print("Вразливий запит повертає:", connection.execute(vulnerable_query).fetchall())
    print(
        "Параметризований запит повертає:", connection.execute(safe_query, (malicious,)).fetchall()
    )
    connection.close()


if __name__ == "__main__":
    run_demo()
