from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base import Base


class CameraLike(Base):
    __tablename__ = "camera_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    camera_id = Column(
        Integer, ForeignKey("cameras.id", ondelete="RESTRICT"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "camera_id", name="uq_camera_user_like"),
    )

    user = relationship("User", back_populates="likes")
    camera = relationship("Camera", back_populates="likes")
