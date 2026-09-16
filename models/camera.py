from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from db.base import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    image_url = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=True)
    power = Column(Float, nullable=True)
    resolution = Column(String(50), nullable=True)
    housing_type = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    creator_id = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    published_at = Column(DateTime(timezone=True), nullable=True)

    creator = relationship("User", back_populates="cameras")
    likes = relationship("CameraLike", back_populates="camera")

    @property
    def summary(self) -> str:
        return self.description or ""
