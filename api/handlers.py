import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.session import get_db
from models.camera import Camera

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def get_cameras_catalog(
    request: Request,
    power_max: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    parsed_power: Optional[float] = None
    if power_max is not None and power_max != "":
        try:
            val = float(power_max)
            if val >= 0:
                parsed_power = val
        except (ValueError, TypeError):
            parsed_power = None

    db_max = await db.scalar(
        select(func.max(Camera.power)).where(Camera.status == "published")
    )
    highest_power = float(db_max) if db_max is not None else 15.0
    if parsed_power is not None and parsed_power > highest_power:
        highest_power = parsed_power
    scale_max = max(15.0, float(math.ceil(highest_power / 5.0) * 5.0))

    stmt = (
        select(Camera)
        .options(selectinload(Camera.likes))
        .where(Camera.status == "published")
        .order_by(Camera.id)
    )
    if parsed_power is not None:
        stmt = stmt.where(Camera.power <= parsed_power)

    result = await db.execute(stmt)
    cameras = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context={
            "cameras": cameras,
            "power_max": parsed_power,
            "scale_max": scale_max,
            "active_tab": "catalog",
        },
    )


@router.get("/draft", response_class=HTMLResponse)
@router.get("/create", response_class=HTMLResponse)
async def get_camera_draft(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Camera)
        .where(Camera.creator_id == 1, Camera.status == "draft")
        .order_by(Camera.id.desc())
    )
    result = await db.execute(stmt)
    draft = result.scalar_one_or_none()

    return templates.TemplateResponse(
        request=request,
        name="create.html",
        context={
            "camera": draft,
            "has_draft": draft is not None,
            "active_tab": "create",
        },
    )


@router.get("/feed", response_class=HTMLResponse)
@router.get("/feed/{camera_id}", response_class=HTMLResponse)
async def get_camera_feed(
    request: Request,
    camera_id: Optional[int] = None,
    next: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Camera)
        .options(selectinload(Camera.likes))
        .where(Camera.status == "published")
        .order_by(Camera.id)
    )
    result = await db.execute(stmt)
    published = result.scalars().all()
    if not published:
        raise HTTPException(status_code=404, detail="No published cameras found")

    camera = None
    if camera_id is None:
        camera = published[0]
    elif next:
        ids = [c.id for c in published]
        if camera_id in ids:
            curr_idx = ids.index(camera_id)
            next_idx = (curr_idx + 1) % len(ids)
            camera = published[next_idx]
        else:
            camera = published[0]
    else:
        cam_stmt = (
            select(Camera)
            .options(selectinload(Camera.likes))
            .where(Camera.id == camera_id)
        )
        cam_res = await db.execute(cam_stmt)
        found = cam_res.scalar_one_or_none()
        if not found or found.status == "deleted":
            raise HTTPException(status_code=404, detail="Camera not found or deleted")
        camera = found

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={
            "camera": camera,
            "current_camera_id": camera.id,
            "active_tab": "feed",
        },
    )


@router.post("", response_class=RedirectResponse)
@router.post("/", response_class=RedirectResponse)
async def create_camera_draft(
    model_name: str = Form(...),
    housing_type: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.scalar(
        select(Camera).where(Camera.creator_id == 1, Camera.status == "draft")
    )
    if not existing:
        new_draft = Camera(
            model_name=model_name.strip(),
            creator_id=1,
            status="draft",
            image_url="/static/img/default_camera.jpg",
            video_url="/static/video/default_video.mp4",
            housing_type=housing_type.strip() if housing_type else None,
        )
        db.add(new_draft)
        await db.commit()
    return RedirectResponse(url="/cameras/draft", status_code=303)


@router.post("/{camera_id}/publish", response_class=RedirectResponse)
async def publish_camera(
    camera_id: int,
    model_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    power: Optional[float] = Form(None),
    resolution: Optional[str] = Form(None),
    housing_type: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    camera = await db.scalar(
        select(Camera).where(Camera.id == camera_id, Camera.status == "draft")
    )
    if not camera:
        raise HTTPException(status_code=404, detail="Draft not found")

    if model_name is not None and model_name.strip():
        camera.model_name = model_name.strip()
    if description is not None:
        camera.description = description.strip() or None
    if power is not None:
        camera.power = max(0.0, float(power))
    if resolution is not None:
        camera.resolution = resolution.strip() or None
    if housing_type is not None:
        camera.housing_type = housing_type.strip() or None
    camera.status = "published"
    camera.published_at = datetime.now(timezone.utc)

    await db.commit()
    return RedirectResponse(url="/cameras", status_code=303)


@router.post("/{camera_id}/delete", response_class=RedirectResponse)
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
):
    raw_query = text("UPDATE cameras SET status = 'deleted' WHERE id = :camera_id")
    await db.execute(raw_query, {"camera_id": camera_id})
    await db.commit()
    return RedirectResponse(url="/cameras", status_code=303)
