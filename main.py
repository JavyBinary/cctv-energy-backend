from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.handlers import router as cameras_router
from api.v1 import api_cameras_router, api_users_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Сервис расчета энергопотребления систем видеонаблюдения",
    description="REST API для управления моделями камер и веб-интерфейс",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(cameras_router)
app.include_router(api_cameras_router, prefix="/api")
app.include_router(api_users_router, prefix="/api")


@app.get("/")
def read_root():
    return RedirectResponse(url="/cameras")
