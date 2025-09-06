from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import routers  # importa la lista de routers definida en __init__.py

app = FastAPI(
    title="ERP System",
    description="Backend ERP con FastAPI",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory="app/templates/views/static"),
    name="static"
)
# incluir todos los routers automáticamente
for r in routers:
    app.include_router(r)

@app.get("/")
def root():
    return {"msg": "API funcionando 🚀"}
