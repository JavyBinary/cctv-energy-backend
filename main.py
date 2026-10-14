from pathlib import Path
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.handlers import router as cameras_router
from api.v1 import api_cameras_router, api_users_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Сервис расчета энергопотребления систем видеонаблюдения",
    description="REST API для управления моделями камер (ЛР3-ЛР4) и веб-интерфейс (ЛР1-ЛР2)",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(cameras_router, include_in_schema=False)
app.include_router(api_cameras_router, prefix="/api")
app.include_router(api_users_router, prefix="/api")


@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/cameras")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "cookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "session_id",
            "description": "Авторизация через сессионную куку session_id",
        },
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "description": "Авторизация через заголовок Authorization: Bearer <session_id>",
        },
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
