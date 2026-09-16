from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.handlers import router as cameras_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Система видеонаблюдения - Расчет энергопотребления")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(cameras_router)


@app.get("/")
def read_root():
    return RedirectResponse(url="/cameras")
