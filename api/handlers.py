from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from data.cameras import (
    get_camera_by_id,
    get_draft_camera,
    get_next_published_camera,
    get_published_cameras,
)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def get_cameras_catalog(
    request: Request,
    power_max: Optional[str] = Query(None),
):
    parsed_power: Optional[float] = None
    if power_max is not None and power_max != "":
        try:
            val = float(power_max)
            if val >= 0:
                parsed_power = val
        except (ValueError, TypeError):
            parsed_power = None

    cameras = get_published_cameras(power_max=parsed_power)
    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context={
            "cameras": cameras,
            "power_max": parsed_power,
            "active_tab": "catalog",
        },
    )


@router.get("/draft", response_class=HTMLResponse)
@router.get("/create", response_class=HTMLResponse)
def get_camera_draft(request: Request):
    draft = get_draft_camera()
    if not draft:
        raise HTTPException(status_code=404, detail="Not Found")

    return templates.TemplateResponse(
        request=request,
        name="create.html",
        context={
            "camera": draft,
            "active_tab": "create",
        },
    )


@router.get("/feed", response_class=HTMLResponse)
@router.get("/feed/{camera_id}", response_class=HTMLResponse)
def get_camera_feed(
    request: Request,
    camera_id: Optional[int] = None,
    next: bool = Query(False),
):
    published = get_published_cameras()
    if not published:
        raise HTTPException(status_code=404, detail="Not Found")

    if camera_id is None:
        camera = published[0]
    elif next:
        camera = get_next_published_camera(camera_id)
        if not camera:
            camera = published[0]
    else:
        camera = get_camera_by_id(camera_id)
        if not camera:
            camera = published[0]

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={
            "camera": camera,
            "current_camera_id": camera["id"],
            "active_tab": "feed",
        },
    )
