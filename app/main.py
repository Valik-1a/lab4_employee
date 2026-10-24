from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import get_role, require_admin
from app.cache import clear_cache, get_cached, set_cached
from app.db import Base, engine, get_session
from app.models import AuditLog, Department, Employee
from app.rate_limit import rate_limit
from app.repository import EmployeeRepository
from app.schemas import DepartmentIn, EmployeeIn, EmployeeOut

repo = EmployeeRepository()
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Employee API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/departments")
def list_departments(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.scalars(select(Department).order_by(Department.id)).all()
    return [{"id": d.id, "name": d.name, "location": d.location} for d in rows]


@app.post("/departments", status_code=201)
def create_department(
    data: DepartmentIn, session: Session = Depends(get_session), role: str = Depends(get_role)
) -> dict:
    require_admin(role)
    item = Department(name=data.name, location=data.location)
    session.add(item)
    session.commit()
    session.refresh(item)
    return {"id": item.id, "name": item.name, "location": item.location}


@app.get("/employees", response_model=list[EmployeeOut], dependencies=[Depends(rate_limit)])
def list_employees(
    response: Response,
    session: Session = Depends(get_session),
    role: str = Depends(get_role),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Employee]:
    cached = get_cached(f"employees:{limit}:{offset}")
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return cached
    items = repo.list(session)[offset : offset + limit]
    set_cached(f"employees:{limit}:{offset}", items)
    response.headers["X-Cache"] = "MISS"
    return items


@app.get("/employees/{employee_id}", response_model=EmployeeOut, dependencies=[Depends(rate_limit)])
def get_employee(
    employee_id: int, session: Session = Depends(get_session), role: str = Depends(get_role)
) -> Employee:
    item = repo.get(session, employee_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Працівника не знайдено")
    return item


@app.post(
    "/employees", response_model=EmployeeOut, status_code=201, dependencies=[Depends(rate_limit)]
)
def create_employee(
    data: EmployeeIn, session: Session = Depends(get_session), role: str = Depends(get_role)
) -> Employee:
    require_admin(role)
    if session.get(Department, data.department_id) is None:
        raise HTTPException(status_code=422, detail="Вказаний відділ не існує")
    item = repo.create(session, data.model_dump())
    session.add(AuditLog(action="CREATE", resource="employee", resource_id=str(item.id)))
    session.commit()
    clear_cache()
    return item


@app.put("/employees/{employee_id}", response_model=EmployeeOut, dependencies=[Depends(rate_limit)])
def update_employee(
    employee_id: int,
    data: EmployeeIn,
    session: Session = Depends(get_session),
    role: str = Depends(get_role),
) -> Employee:
    require_admin(role)
    item = repo.get(session, employee_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Працівника не знайдено")
    if session.get(Department, data.department_id) is None:
        raise HTTPException(status_code=422, detail="Вказаний відділ не існує")
    updated = repo.update(session, item, data.model_dump())
    session.add(AuditLog(action="UPDATE", resource="employee", resource_id=str(employee_id)))
    session.commit()
    clear_cache()
    return updated


@app.delete("/employees/{employee_id}", status_code=204, dependencies=[Depends(rate_limit)])
def delete_employee(
    employee_id: int, session: Session = Depends(get_session), role: str = Depends(get_role)
) -> Response:
    require_admin(role)
    item = repo.get(session, employee_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Працівника не знайдено")
    session.add(AuditLog(action="DELETE", resource="employee", resource_id=str(employee_id)))
    repo.delete(session, item)
    session.commit()
    clear_cache()
    return Response(status_code=204)


@app.get("/report")
def report(session: Session = Depends(get_session)) -> Response:
    employee_count = session.scalar(select(func.count()).select_from(Employee)) or 0
    department_count = session.scalar(select(func.count()).select_from(Department)) or 0
    avg_salary = session.scalar(select(func.avg(Employee.salary))) or 0
    payload = {
        "employees": employee_count,
        "departments": department_count,
        "average_salary": round(float(avg_salary), 2),
    }
    import json

    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return Response(
        content=body, media_type="application/json", headers={"X-Report-Bytes": str(len(body))}
    )


@app.get("/audit")
def audit(session: Session = Depends(get_session), role: str = Depends(get_role)) -> list[dict]:
    require_admin(role)
    rows = session.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(100)).all()
    return [
        {
            "id": r.id,
            "action": r.action,
            "resource": r.resource,
            "resource_id": r.resource_id,
            "created_at": str(r.created_at),
        }
        for r in rows
    ]


@app.get("/admin", response_class=HTMLResponse)
def admin_page() -> str:
    return """<!doctype html><html lang='uk'><meta charset='utf-8'>
    <title>Адміністрування працівників</title><body style='font-family:Arial;max-width:900px;margin:30px auto'>
    <h1>Система обліку працівників</h1>
    <p>Вставте admin API key, щоб переглядати та додавати записи.</p>
    <label>API key <input id='key' value='admin-demo-key' style='width:220px'></label>
    <button onclick='loadEmployees()'>Завантажити працівників</button>
    <h2>Додати працівника</h2>
    <p>ПІБ <input id='name' value='Кононова Валентина'></p>
    <p>Email <input id='email' value='valya.new@example.com'></p>
    <p>Телефон <input id='phone' value='+380501234567'></p>
    <p>Посада <input id='position' value='Розробник'></p>
    <p>Зарплата <input id='salary' type='number' value='25000'></p>
    <p>ID відділу <input id='dept' type='number' value='1'></p>
    <button onclick='addEmployee()'>Додати</button><pre id='out'></pre>
    <script>
    async function loadEmployees(){let r=await fetch('/employees',{headers:{'X-API-Key':document.getElementById('key').value}});
    document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2);}
   async function addEmployee(){
    let d = {
        full_name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        position: document.getElementById('position').value,
        salary: Number(document.getElementById('salary').value),
        department_id: Number(document.getElementById('dept').value)
    };
    let r = await fetch('/employees', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': document.getElementById('key').value
        },
        body: JSON.stringify(d)
    });
    let result = await r.json();
    document.getElementById('out').textContent =
        r.status + ' ' + JSON.stringify(result, null, 2);
}
    </script></body></html>"""
