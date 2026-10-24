import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9 ()-]{7,20}$")


class EmployeeIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(max_length=254)
    phone: str = Field(max_length=20)
    position: str = Field(min_length=2, max_length=100)
    salary: float = Field(gt=0, le=10000000)
    department_id: int = Field(gt=0)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        if not EMAIL_RE.fullmatch(value):
            raise ValueError("Некоректний email")
        return value.lower()

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value: str) -> str:
        if not PHONE_RE.fullmatch(value):
            raise ValueError("Некоректний номер телефону")
        return value


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: str
    phone: str
    position: str
    salary: float
    department_id: int


class DepartmentIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=100)
