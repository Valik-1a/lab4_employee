from fastapi import Header, HTTPException

from app.config import ADMIN_API_KEY, READ_API_KEY


def get_role(x_api_key: str | None = Header(default=None)) -> str:
    if x_api_key == ADMIN_API_KEY:
        return "admin"
    if x_api_key == READ_API_KEY:
        return "reader"
    raise HTTPException(status_code=401, detail="Потрібен коректний API-ключ")


def require_admin(role: str) -> None:
    if role != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав: потрібна роль admin")
