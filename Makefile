.PHONY: run db-init models dev

# Cargar variables desde .env
include .env
export $(shell sed 's/=.*//' .env)

# 🚀 Levantar FastAPI
run:
	@echo "🔄 Iniciando servidor FastAPI en http://127.0.0.1:$(PORT) ..."
	poetry run uvicorn app.main:app --reload --port $(PORT)
	@echo "✅ Servidor detenido."

# 🛠️ Crear tablas en la base de datos
db-init:
	@echo "🛠️  Creando tablas en la base de datos..."
	poetry run python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
	@echo "✅ Tablas creadas con éxito."

# 🏗️ Generar modelos automáticamente con sqlacodegen
models:
	@echo "📦 Generando modelos con sqlacodegen-v2 desde Railway..."
	poetry run python -m sqlacodegen_v2 $${DATABASE_URL} --outfile app/models/generated.py
	@echo "✅ Modelos generados en app/models/generated.py"



# 👨‍💻 Desarrollo: todo junto (DB + modelos + servidor)
dev: db-init models run
