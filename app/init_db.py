from app.db import Base, SessionLocal, engine
from app.models import Department, Employee


def initialize() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        if session.query(Department).count() == 0:
            departments = [
                Department(name="ІТ", location="Львів"),
                Department(name="Бухгалтерія", location="Київ"),
                Department(name="Кадри", location="Одеса"),
                Department(name="Продажі", location="Харків"),
                Department(name="Маркетинг", location="Дніпро"),
            ]
            session.add_all(departments)
            session.commit()
        if session.query(Employee).count() == 0:
            departments = session.query(Department).order_by(Department.id).all()
            positions = ["Розробник", "Аналітик", "Менеджер", "Бухгалтер", "Тестувальник"]
            employees = []
            for i in range(60):
                employees.append(
                    Employee(
                        full_name=f"Працівник Тестовий {i + 1:02d}",
                        email=f"employee{i + 1:02d}@example.com",
                        phone=f"+38050123{i:04d}",
                        position=positions[i % len(positions)],
                        salary=18000 + (i % 15) * 1200,
                        department_id=departments[i % len(departments)].id,
                    )
                )
            session.add_all(employees)
            session.commit()
    print("Ініціалізацію завершено. Створено таблиці та щонайменше 60 працівників.")


if __name__ == "__main__":
    initialize()
