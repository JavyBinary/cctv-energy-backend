import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.auth import get_current_user_id
from db.session import get_db
from models.camera import Camera
from models.like import CameraLike
from schemas.camera import CameraPublishRequest, CameraResponse, LikeToggleRequest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/cameras", tags=["cameras"])


def to_camera_response(camera: Camera, current_user_id: int) -> CameraResponse:
    likes_count = len(camera.likes) if camera.likes is not None else 0
    is_creator = 1 if camera.creator_id == current_user_id else 0
    return CameraResponse(
        id=camera.id,
        model_name=camera.model_name,
        description=camera.description,
        status=camera.status,
        image_url=camera.image_url,
        video_url=camera.video_url,
        power=camera.power,
        resolution=camera.resolution,
        housing_type=camera.housing_type,
        created_at=camera.created_at,
        published_at=camera.published_at,
        creator_id=camera.creator_id,
        likes_count=likes_count,
        is_creator=is_creator,
    )


@router.get("", response_model=List[CameraResponse])
@router.get("/", response_model=List[CameraResponse])
async def get_cameras_api(
    power_max: Optional[float] = Query(None, description="Фильтрация по максимальной мощности"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    stmt = (
        select(Camera)
        .options(selectinload(Camera.likes))
        .where(Camera.status == "published")
        .order_by(Camera.id.asc())
    )
    if power_max is not None:
        stmt = stmt.where(Camera.power <= power_max)

    result = await db.execute(stmt)
    cameras = result.scalars().all()
    return [to_camera_response(c, current_user_id) for c in cameras]


@router.get("/feed", response_model=CameraResponse)
async def get_camera_feed_api(
    camera_id: Optional[int] = Query(None, description="ID текущей камеры"),
    next: bool = Query(False, description="Флаг перехода к следующей камере"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    camera = None
    if camera_id is None:
        stmt = (
            select(Camera)
            .options(selectinload(Camera.likes))
            .where(Camera.status == "published")
            .order_by(Camera.id.asc())
            .limit(1)
        )
        camera = (await db.execute(stmt)).scalar_one_or_none()
    elif next:
        stmt = (
            select(Camera)
            .options(selectinload(Camera.likes))
            .where(Camera.status == "published", Camera.id > camera_id)
            .order_by(Camera.id.asc())
            .limit(1)
        )
        camera = (await db.execute(stmt)).scalar_one_or_none()
        if not camera:
            fallback_stmt = (
                select(Camera)
                .options(selectinload(Camera.likes))
                .where(Camera.status == "published")
                .order_by(Camera.id.asc())
                .limit(1)
            )
            camera = (await db.execute(fallback_stmt)).scalar_one_or_none()
    else:
        stmt = (
            select(Camera)
            .options(selectinload(Camera.likes))
            .where(Camera.id == camera_id, Camera.status == "published")
            .limit(1)
        )
        camera = (await db.execute(stmt)).scalar_one_or_none()

    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    return to_camera_response(camera, current_user_id)


@router.get("/draft", response_model=CameraResponse)
async def get_camera_draft_api(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    stmt = (
        select(Camera)
        .options(selectinload(Camera.likes))
        .where(Camera.creator_id == current_user_id, Camera.status == "draft")
        .order_by(Camera.id.desc())
        .limit(1)
    )
    draft = (await db.execute(stmt)).scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")

    return to_camera_response(draft, current_user_id)


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera_api(
    model_name: str = Form(..., description="Название модели камеры"),
    housing_type: Optional[str] = Form(None, description="Тип корпуса"),
    image_file: Optional[UploadFile] = File(None, description="Файл изображения камеры"),
    video_file: Optional[UploadFile] = File(None, description="Файл короткого видео камеры"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    existing_stmt = select(Camera).where(
        Camera.creator_id == current_user_id, Camera.status == "draft"
    )
    existing_draft = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing_draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active draft",
        )

    saved_image_url = "/static/img/default_camera.jpg"
    if image_file and image_file.filename:
        ext = Path(image_file.filename).suffix.lower() or ".jpg"
        img_name = f"camera_{uuid.uuid4().hex[:10]}{ext}"
        img_path = UPLOAD_DIR / img_name
        content = await image_file.read()
        with open(img_path, "wb") as f:
            f.write(content)
        saved_image_url = f"/static/uploads/{img_name}"

    saved_video_url = "/static/video/default_video.mp4"
    if video_file and video_file.filename:
        ext = Path(video_file.filename).suffix.lower() or ".mp4"
        vid_name = f"video_{uuid.uuid4().hex[:10]}{ext}"
        vid_path = UPLOAD_DIR / vid_name
        content = await video_file.read()
        with open(vid_path, "wb") as f:
            f.write(content)
        saved_video_url = f"/static/uploads/{vid_name}"

    new_camera = Camera(
        model_name=model_name.strip(),
        creator_id=current_user_id,
        status="draft",
        image_url=saved_image_url,
        video_url=saved_video_url,
        housing_type=housing_type.strip() if housing_type else None,
    )
    db.add(new_camera)
    await db.commit()

    reloaded_stmt = (
        select(Camera)
        .options(selectinload(Camera.likes))
        .where(Camera.id == new_camera.id)
    )
    created = (await db.execute(reloaded_stmt)).scalar_one()
    return to_camera_response(created, current_user_id)


@router.put("/{camera_id}/publish", response_model=CameraResponse)
async def publish_camera_api(
    camera_id: int,
    payload: CameraPublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    stmt = (
        select(Camera)
        .options(selectinload(Camera.likes))
        .where(Camera.id == camera_id)
    )
    camera = (await db.execute(stmt)).scalar_one_or_none()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    if camera.creator_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creator can publish this camera",
        )

    if camera.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft cameras can be published",
        )

    if payload.model_name is not None and payload.model_name.strip():
        camera.model_name = payload.model_name.strip()
    if payload.description is not None:
        camera.description = payload.description.strip() or None
    camera.power = payload.power
    camera.resolution = payload.resolution.strip()
    if payload.housing_type is not None:
        camera.housing_type = payload.housing_type.strip() or None

    camera.status = "published"
    camera.published_at = datetime.now(timezone.utc)
    await db.commit()

    return to_camera_response(camera, current_user_id)


@router.delete("/{camera_id}", response_model=CameraResponse)
async def delete_camera_api(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    stmt = (
        select(Camera)
        .options(selectinload(Camera.likes))
        .where(Camera.id == camera_id)
    )
    camera = (await db.execute(stmt)).scalar_one_or_none()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    if camera.creator_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creator can delete this camera",
        )

    camera.status = "deleted"
    await db.commit()
    return to_camera_response(camera, current_user_id)


@router.post("/{camera_id}/like", response_model=CameraResponse)
async def toggle_camera_like_api(
    camera_id: int,
    payload: LikeToggleRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    cam_stmt = (
        select(Camera)
        .options(selectinload(Camera.likes))
        .where(Camera.id == camera_id, Camera.status == "published")
    )
    camera = (await db.execute(cam_stmt)).scalar_one_or_none()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    like_stmt = select(CameraLike).where(
        CameraLike.camera_id == camera_id, CameraLike.user_id == current_user_id
    )
    existing_like = (await db.execute(like_stmt)).scalar_one_or_none()

    if payload.like == 1 and not existing_like:
        new_like = CameraLike(camera_id=camera_id, user_id=current_user_id)
        db.add(new_like)
        await db.commit()
    elif payload.like == 0 and existing_like:
        await db.delete(existing_like)
        await db.commit()

    db.expire_all()
    reloaded_cam = (await db.execute(cam_stmt)).scalar_one()
    return to_camera_response(reloaded_cam, current_user_id)
