from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Employee


class EmployeeRepository:
    """Рівень доступу до даних; його можна замінити іншою реалізацією сховища."""

    def list(self, session: Session) -> list[Employee]:
        return list(session.scalars(select(Employee).order_by(Employee.id)).all())

    def get(self, session: Session, employee_id: int) -> Employee | None:
        return session.get(Employee, employee_id)

    def create(self, session: Session, values: dict) -> Employee:
        item = Employee(**values)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    def update(self, session: Session, item: Employee, values: dict) -> Employee:
        for key, value in values.items():
            setattr(item, key, value)
        session.commit()
        session.refresh(item)
        return item

    def delete(self, session: Session, item: Employee) -> None:
        session.delete(item)
        session.commit()
