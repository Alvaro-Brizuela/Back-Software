from fastapi import FastAPI
from fastapi import Request
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routers import routers  # importa la lista de routers definida en __init__.py

app = FastAPI(
    title="ERP System",
    description="Backend ERP con FastAPI",
    version="1.0.0"
)
origins = [
    "http://localhost:5173",   # Vite/React local
    "http://127.0.0.1:5500",   # live server
    "https://tu-front.netlify.app",  # producción
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# incluir todos los routers automáticamente
for r in routers:
    app.include_router(r)

@app.get("/")
def root():
    return {"msg": "API funcionando 🚀"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger = logging.getLogger("uvicorn")
    logger.info(f"➡️ {request.method} {request.url} desde {request.client.host}")

    response = await call_next(request)

    logger.info(f"⬅️ {response.status_code} {request.method} {request.url}")
    return response
