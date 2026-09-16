from typing import Any, Dict, List, Optional

CAMERAS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "model_name": "DS-2CE16D8T-ITE",
        "description": "2Мп уличная компактная цилиндрическая HD-TVI камера с EXIR-подсветкой до 20м 1/3 Progressive Scan CMOS; объектив 3.6мм; угол обзора: 82.6°; механический ИК-фильтр; 0.005 Лк@F1.2; 1920×1080@25к/с; WDR 120дБ, 3D DNR, BLC; OSD-меню; Smart ИК; 1 HD-TVI выход; IP67; -40°С до +60°С; питание 12В DC±25% / PoC.af; 3.6Вт макс.",
        "power": 3.6,
        "resolution": "Full HD",
        "housing_type": "Цилиндрический",
        "is_outdoor": True,
        "status": "published",
        "image_url": "http://localhost:9000/cctv-media/camera_1.jpg",
        "video_url": "http://localhost:9000/cctv-media/video_1.mp4",
        "likes": [101, 102, 103, 104, 105],
    },
    {
        "id": 2,
        "model_name": "DS-2CD2123G0-IS",
        "description": "2Мп купольная IP-камера с ИК-подсветкой до 30м 1/2.8 Progressive Scan CMOS; объектив 2.8мм; угол обзора 114°; механический ИК-фильтр; 0.01 Лк@F1.2; сжатие H.265/H.264/MJPEG; тройной поток; 1920×1080@25к/с; WDR 120дБ, 3D DNR, BLC, ROI; обнаружение движения, вторжения в область и пересечения линии; слот для microSD до 128Гб; аудиовход/выход 1/1; тревожные вход/выход 1/1; 1 RJ45 10M/100M Ethernet; питание DC12В±25%/PoE(802.3af); 6Вт макс.",
        "power": 6.0,
        "resolution": "Full HD",
        "housing_type": "Купольный",
        "is_outdoor": False,
        "status": "published",
        "image_url": "http://localhost:9000/cctv-media/camera_2.jpg",
        "video_url": "http://localhost:9000/cctv-media/video_2.mp4",
        "likes": [101, 102],
    },
    {
        "id": 3,
        "model_name": "DS-2CD50C5G0-AP",
        "description": "12Мп стандартная корпусная IP-камера 1/1.7 Progressive Scan CMOS; крепление объектива C/CS; механический ИК-фильтр; 0.005 Лк@F1.2; сжатие H.265/H.264/MJPEG; пять потоков; 4000×3000@20к/с, 3840×2160@25к/с; DWDR, 3D DNR, BLC, антитуман, HLC, ROI; smart видеоаналитика; слот для microSD до 256Гб; аудиовход/выход 1/1; тревожные вход/выход 2/2; 1Vp-p композитный выход (75 Ом/BNC); 1 RJ45 10M/100M/1000M Ethernet; RS-485; питание DC12В/AC24В/PoE(802.3af); 7Вт макс.",
        "power": 7.0,
        "resolution": "2K QHD",
        "housing_type": "Стандартный",
        "is_outdoor": False,
        "status": "published",
        "image_url": "http://localhost:9000/cctv-media/camera_3.jpg",
        "video_url": "http://localhost:9000/cctv-media/video_3.mp4",
        "likes": [101, 102, 103],
    },
    {
        "id": 4,
        "model_name": "DS-2CD2025FWD-I",
        "description": "2Мп уличная цилиндрическая IP-камера с EXIR-подсветкой до 30м 1/2.8 Progressive Scan CMOS; объектив 4мм; угол обзора 86°; механический ИК-фильтр; 0.005 Лк@F1.2; сжатие H.265/H.264/MJPEG; тройной поток; 1920×1080@25к/с; WDR 120дБ, 3D DNR, BLC, ROI; smart видеоаналитика; слот для microSD до 128Гб; 1 RJ45 10M/100M Ethernet; IP67; -40°C до +60°C; питание DC12В±25%/PoE(802.3af); 6.5Вт макс.",
        "power": 6.5,
        "resolution": "Super HD",
        "housing_type": "Цилиндрический",
        "is_outdoor": True,
        "status": "published",
        "image_url": "http://localhost:9000/cctv-media/camera_4.jpg",
        "video_url": "http://localhost:9000/cctv-media/video_4.mp4",
        "likes": [101],
    },
    {
        "id": 5,
        "model_name": "DS-2CE56H0T-ITME",
        "description": "5Мп уличная купольная HD-TVI камера с EXIR-подсветкой до 20м и технологией PoC 1/2.7 Progressive Scan CMOS; объектив 2.8мм; угол обзора 85.5°; механический ИК-фильтр; 0.01 Лк@F1.2; 2560×1944@20к/с; Smart ИК; OSD-меню; 1 HD-TVI выход; IP67; -40°С до +60°С; питание 12В DC±25%/PoC.af; 4.2Вт макс.",
        "power": 4.2,
        "resolution": "Full HD",
        "housing_type": "Купольный",
        "is_outdoor": True,
        "status": "draft",
        "image_url": "http://localhost:9000/cctv-media/camera_1.jpg",
        "video_url": "http://localhost:9000/cctv-media/video_1.mp4",
        "likes": [],
    },
    {
        "id": 6,
        "model_name": "DS-2CE16C0T-IR",
        "description": "Удаленная устаревшая 1Мп цилиндрическая камера видеонаблюдения. В интерфейсе никогда не отображается.",
        "power": 4.0,
        "resolution": "HD Ready",
        "housing_type": "Цилиндрический",
        "is_outdoor": True,
        "status": "deleted",
        "image_url": "http://localhost:9000/cctv-media/camera_2.jpg",
        "video_url": "http://localhost:9000/cctv-media/video_2.mp4",
        "likes": [],
    },
]

for _cam in CAMERAS:
    _cam["summary"] = _cam["description"]


def get_published_cameras(power_max: Optional[float] = None) -> List[Dict[str, Any]]:
    result = [c for c in CAMERAS if c["status"] == "published"]
    if power_max is not None:
        result = [c for c in result if c["power"] <= power_max]
    return result


def get_camera_by_id(camera_id: int) -> Optional[Dict[str, Any]]:
    return next(
        (c for c in CAMERAS if c["id"] == camera_id and c["status"] == "published"),
        None,
    )


def get_next_published_camera(current_id: int) -> Optional[Dict[str, Any]]:
    published = [c for c in CAMERAS if c["status"] == "published"]
    if not published:
        return None
    for idx, c in enumerate(published):
        if c["id"] == current_id:
            next_idx = (idx + 1) % len(published)
            return published[next_idx]
    return published[0]


def get_draft_camera() -> Optional[Dict[str, Any]]:
    return next((c for c in CAMERAS if c["status"] == "draft"), None)
