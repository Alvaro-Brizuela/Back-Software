# 🚀 Contaplus ERP - Backend

Backend del sistema ERP desarrollado en **FastAPI** con **PostgreSQL** como base de datos (Railway), gestionado con **Poetry** para dependencias y un **Makefile** para automatizar tareas.

---

## 📂 Estructura del proyecto

![Estructura del proyecto](image/structure.png)



---

## ⚙️ Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Contapluss/Back-end.git
   cd Back-End

2. instalar dependencias:
   ```bash
    poetry install

3. Crear archivo .env con tus credenciales (ejemplo usando Railway):
   ```bash
   DATABASE_URL=postgresql://postgres:TU_PASSWORD@usuarios123:12345/railway
   PORT=8000

### 🛠️ Uso con Makefile

# El proyecto incluye un Makefile para facilitar tareas comunes(linux):
   .PHONY: run db-init models dev

   include .env
   export $(shell sed 's/=.*//' .env)

   run:
	   poetry run uvicorn app.main:app --reload --port $(PORT)

   db-init:
	   poetry run python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

   models:
	   poetry run sqlacodegen $${DATABASE_URL} --outfile app/models/generated.py

   dev: db-init models run

   ### Comandos disponibles

1. Levantar servidor:
   ```bash
   make run

2. Inicializar base de datos(crear tablas)
   ```bash
   make db-init

3. Generar modelos automáticamente
   ```bash
   make models

4. Modo desarrollo (todo en uno)
   ```bash
   make dev

1. **Levantar servidor(windows)**
   ```bash
   poetry run uvicorn app.main:app --reload --port 8000
   poetry run python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"


### Base de datos

Motor: PostgreSQL (Railway).

Conexión definida en .env usando DATABASE_URL.

ORM: SQLAlchemy.

Schemas: Pydantic.

Migraciones futuras: Alembic.

## Pruebas

1. Para ver y probar los endpoint usar los siguiente link en su buscador favorito
   ```bash
   http://127.0.0.1:8000/docs
   http://127.0.0.1:8000/redoc