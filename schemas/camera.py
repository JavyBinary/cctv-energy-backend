from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CameraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_name: str
    description: Optional[str] = None
    status: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    power: Optional[float] = None
    resolution: Optional[str] = None
    housing_type: Optional[str] = None
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    creator_id: int
    likes_count: int = 0
    is_creator: int = 0


class CameraPublishRequest(BaseModel):
    model_name: Optional[str] = None
    description: Optional[str] = None
    power: float = Field(..., ge=0, description="Потребляемая мощность в Вт")
    resolution: str = Field(..., min_length=1, description="Разрешение камеры")
    housing_type: Optional[str] = Field(None, description="Тип корпуса: уличная/для помещения")


class LikeToggleRequest(BaseModel):
    like: int = Field(..., ge=0, le=1, description="0 - отменить лайк, 1 - поставить лайк")
