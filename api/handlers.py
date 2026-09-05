from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from data.camera_collections import cameras

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
@router.get("/camera/{camera_id}")
def screen_feed(request: Request, camera_id: int | None = None, next: bool = False):
    published = [c for c in cameras if c["status"] == "опубликован"]

    if camera_id is None:
        target_cam = published[0]
    else:
        current_index = 0
        for idx, cam in enumerate(published):
            if cam["id"] == camera_id:
                current_index = idx
                break
        
        if next:
            next_idx = (current_index + 1) % len(published)
            target_cam = published[next_idx]
        else:
            target_cam = published[current_index]

    cam_data = {**target_cam, "likes_count": len(target_cam["likes"])}

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={"camera": cam_data, "active_tab": "feed"}
    )


@router.get("/create")
def screen_create(request: Request):
    draft_cam = next(c for c in cameras if c["status"] == "черновик")
    cam_data = {**draft_cam, "likes_count": len(draft_cam["likes"])}

    return templates.TemplateResponse(
        request=request,
        name="create.html",
        context={"camera": cam_data, "active_tab": "create"}
    )


@router.get("/catalog")
def screen_catalog(request: Request, search_power: float = 12.0):
    published = [c for c in cameras if c["status"] == "опубликован"]
    filtered = [c for c in published if c["power_consumption_watts"] <= search_power]
    view_cameras = [{**c, "likes_count": len(c["likes"])} for c in filtered]

    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context={
            "cameras": view_cameras,
            "search_power": search_power,
            "active_tab": "catalog"
        }
    )