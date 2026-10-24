-- Початкова схема; основний застосунок також може створити таблиці через SQLAlchemy.
CREATE TABLE IF NOT EXISTS departments (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  location VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS employees (
  id SERIAL PRIMARY KEY,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(254) UNIQUE NOT NULL,
  phone VARCHAR(20) NOT NULL,
  position VARCHAR(100) NOT NULL,
  salary NUMERIC(10,2) NOT NULL CHECK (salary > 0),
  department_id INTEGER NOT NULL REFERENCES departments(id)
);
