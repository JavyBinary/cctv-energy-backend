from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    cameras = relationship("Camera", back_populates="creator")
    likes = relationship("CameraLike", back_populates="user")
