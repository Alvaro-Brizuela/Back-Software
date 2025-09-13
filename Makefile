.PHONY: run db-init models dev debug

# Cargar variables desde .env
include .env
export $(shell sed 's/=.*//' .env)

# 🔍 Debug: mostrar todas las variables cargadas
debug:
	@echo "------ DEBUG VARIABLES ------"
	@echo "DATABASE_URL=$(DATABASE_URL)"
	@echo "PORT=$(PORT)"
	@echo "SECRET_KEY=$(SECRET_KEY)"
	@echo "-----------------------------"

# 🚀 Levantar FastAPI
run:
	@echo "🔄 Iniciando servidor FastAPI en http://127.0.0.1:$(PORT) ..."
	@echo "Usando DATABASE_URL=$(DATABASE_URL)"
	poetry run uvicorn app.main:app --reload --port $(PORT)
	@echo "✅ Servidor detenido."

# 🛠️ Crear tablas en la base de datos
db-init:
	@echo "🛠️  Creando tablas en la base de datos..."
	@echo "Usando DATABASE_URL=$(DATABASE_URL)"
	poetry run python -c "from app.database import Base, engine; print('Conectando a', engine.url); Base.metadata.create_all(bind=engine)"
	@echo "✅ Tablas creadas con éxito."

# 🏗️ Generar modelos automáticamente con sqlacodegen
models:
	@echo "📦 Generando modelos con sqlacodegen-v2 desde Railway..."
	@echo "Usando DATABASE_URL=$(DATABASE_URL)"
	@poetry run python -c "import os; print('Python ve DATABASE_URL=', os.getenv('DATABASE_URL'))"
	poetry run python -m sqlacodegen_v2 $(DATABASE_URL) --outfile app/models/generated.py
	@echo "✅ Modelos generados en app/models/generated.py"

# 👨‍💻 Desarrollo: todo junto (DB + modelos + servidor)
dev: db-init models run
