import asyncio
from datetime import datetime, timezone

from sqlalchemy import select, text

from db.session import async_session_maker
from models.camera import Camera
from models.like import CameraLike
from models.user import User

SEED_USERS = [
    {"id": 1, "username": "admin", "password": "password123"},
    {"id": 101, "username": "user_101", "password": "password123"},
    {"id": 102, "username": "user_102", "password": "password123"},
    {"id": 103, "username": "user_103", "password": "password123"},
    {"id": 104, "username": "user_104", "password": "password123"},
    {"id": 105, "username": "user_105", "password": "password123"},
]

SEED_CAMERAS = [
    {
        "id": 1,
        "model_name": "DS-2CE16D8T-ITE",
        "description": "2Мп уличная компактная цилиндрическая HD-TVI камера с EXIR-подсветкой до 20м 1/3 Progressive Scan CMOS; объектив 3.6мм; угол обзора: 82.6°; механический ИК-фильтр; 0.005 Лк@F1.2; 1920×1080@25к/с; WDR 120дБ, 3D DNR, BLC; OSD-меню; Smart ИК; 1 HD-TVI выход; IP67; -40°С до +60°С; питание 12В DC±25% / PoC.af; 3.6Вт макс.",
        "power": 3.6,
        "resolution": "Full HD",
        "housing_type": "Цилиндрический",
        "status": "published",
        "image_url": "http://localhost:9000/media/camera_1.jpg",
        "video_url": "http://localhost:9000/media/video_1.mp4",
        "creator_id": 1,
        "published_at": datetime.now(timezone.utc),
    },
    {
        "id": 2,
        "model_name": "DS-2CD2123G0-IS",
        "description": "2Мп купольная IP-камера с ИК-подсветкой до 30м 1/2.8 Progressive Scan CMOS; объектив 2.8мм; угол обзора 114°; механический ИК-фильтр; 0.01 Лк@F1.2; сжатие H.265/H.264/MJPEG; тройной поток; 1920×1080@25к/с; WDR 120дБ, 3D DNR, BLC, ROI; обнаружение движения, вторжения в область и пересечения линии; слот для microSD до 128Гб; аудиовход/выход 1/1; тревожные вход/выход 1/1; 1 RJ45 10M/100M Ethernet; питание DC12В±25%/PoE(802.3af); 6Вт макс.",
        "power": 6.0,
        "resolution": "Full HD",
        "housing_type": "Купольный",
        "status": "published",
        "image_url": "http://localhost:9000/media/camera_2.jpg",
        "video_url": "http://localhost:9000/media/video_2.mp4",
        "creator_id": 1,
        "published_at": datetime.now(timezone.utc),
    },
    {
        "id": 3,
        "model_name": "DS-2CD50C5G0-AP",
        "description": "12Мп стандартная корпусная IP-камера 1/1.7 Progressive Scan CMOS; крепление объектива C/CS; механический ИК-фильтр; 0.005 Лк@F1.2; сжатие H.265/H.264/MJPEG; пять потоков; 4000×3000@20к/с, 3840×2160@25к/с; DWDR, 3D DNR, BLC, антитуман, HLC, ROI; smart видеоаналитика; слот для microSD до 256Гб; аудиовход/выход 1/1; тревожные вход/выход 2/2; 1Vp-p композитный выход (75 Ом/BNC); 1 RJ45 10M/100M/1000M Ethernet; RS-485; питание DC12В/AC24В/PoE(802.3af); 7Вт макс.",
        "power": 7.0,
        "resolution": "2K QHD",
        "housing_type": "Стандартный",
        "status": "published",
        "image_url": "http://localhost:9000/media/camera_3.jpg",
        "video_url": "http://localhost:9000/media/video_3.mp4",
        "creator_id": 1,
        "published_at": datetime.now(timezone.utc),
    },
    {
        "id": 4,
        "model_name": "DS-2CD2025FWD-I",
        "description": "2Мп уличная цилиндрическая IP-камера с EXIR-подсветкой до 30м 1/2.8 Progressive Scan CMOS; объектив 4мм; угол обзора 86°; механический ИК-фильтр; 0.005 Лк@F1.2; сжатие H.265/H.264/MJPEG; тройной поток; 1920×1080@25к/с; WDR 120дБ, 3D DNR, BLC, ROI; smart видеоаналитика; слот для microSD до 128Гб; 1 RJ45 10M/100M Ethernet; IP67; -40°C до +60°C; питание DC12В±25%/PoE(802.3af); 6.5Вт макс.",
        "power": 6.5,
        "resolution": "Super HD",
        "housing_type": "Цилиндрический",
        "status": "published",
        "image_url": "http://localhost:9000/media/camera_4.jpg",
        "video_url": "http://localhost:9000/media/video_4.mp4",
        "creator_id": 1,
        "published_at": datetime.now(timezone.utc),
    },
    {
        "id": 5,
        "model_name": "DS-2CE56H0T-ITME",
        "description": "5Мп уличная купольная HD-TVI камера с EXIR-подсветкой до 20м и технологией PoC 1/2.7 Progressive Scan CMOS; объектив 2.8мм; угол обзора 85.5°; механический ИК-фильтр; 0.01 Лк@F1.2; 2560×1944@20к/с; Smart ИК; OSD-меню; 1 HD-TVI выход; IP67; -40°С до +60°С; питание 12В DC±25%/PoC.af; 4.2Вт макс.",
        "power": 4.2,
        "resolution": "Full HD",
        "housing_type": "Купольный",
        "status": "draft",
        "image_url": "http://localhost:9000/media/camera_1.jpg",
        "video_url": "http://localhost:9000/media/video_1.mp4",
        "creator_id": 1,
        "published_at": None,
    },
    {
        "id": 6,
        "model_name": "DS-2CE16C0T-IR",
        "description": "Удаленная устаревшая 1Мп цилиндрическая камера видеонаблюдения. В интерфейсе никогда не отображается.",
        "power": 4.0,
        "resolution": "HD Ready",
        "housing_type": "Цилиндрический",
        "status": "deleted",
        "image_url": "http://localhost:9000/media/camera_2.jpg",
        "video_url": "http://localhost:9000/media/video_2.mp4",
        "creator_id": 1,
        "published_at": None,
    },
]

SEED_LIKES = [
    (101, 1),
    (102, 1),
    (103, 1),
    (104, 1),
    (105, 1),
    (101, 2),
    (102, 2),
    (101, 3),
    (102, 3),
    (103, 3),
    (101, 4),
]


async def seed_db():
    async with async_session_maker() as session:
        await session.execute(text("DELETE FROM camera_likes"))
        await session.execute(text("DELETE FROM cameras"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()

        for u in SEED_USERS:
            session.add(User(**u))
        await session.commit()

        for c in SEED_CAMERAS:
            session.add(Camera(**c))
        await session.commit()

        for user_id, camera_id in SEED_LIKES:
            existing = await session.scalar(
                select(CameraLike).where(
                    CameraLike.user_id == user_id, CameraLike.camera_id == camera_id
                )
            )
            if not existing:
                session.add(CameraLike(user_id=user_id, camera_id=camera_id))
        await session.commit()

        await session.execute(
            text(
                "SELECT setval('cameras_id_seq', COALESCE((SELECT max(id) FROM cameras), 1))"
            )
        )
        await session.execute(
            text(
                "SELECT setval('users_id_seq', COALESCE((SELECT max(id) FROM users), 1))"
            )
        )
        await session.execute(
            text(
                "SELECT setval('camera_likes_id_seq', COALESCE((SELECT max(id) FROM camera_likes), 1))"
            )
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_db())
    print("Database seeding completed successfully.")
