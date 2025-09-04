from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# URL de conexión, ej:
# postgresql+psycopg2://usuario:password@localhost:5432/mi_base
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear motor de conexión
engine = create_engine(
    DATABASE_URL,
    echo=True,            # Muestra las consultas SQL en consola (útil en desarrollo)
    future=True           # Usa la API moderna de SQLAlchemy
)

# Sesión para interactuar con la DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Clase base para modelos (tablas)
Base = declarative_base()

# Dependencia para usar en FastAPI (inyectar sesión en endpoints)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
