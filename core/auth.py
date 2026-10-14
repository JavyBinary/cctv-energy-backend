from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from core.session import get_session_user_id


def extract_session_id(request: Request) -> Optional[str]:
    raw_token = None

    # 1. Из куки FastAPI
    if "session_id" in request.cookies:
        raw_token = request.cookies.get("session_id")

    # 2. Из заголовка Cookie (ручная строка для Postman / Insomnia: "Cookie: session_id=...")
    if not raw_token:
        cookie_header = request.headers.get("cookie") or request.headers.get("Cookie")
        if cookie_header:
            for part in cookie_header.split(";"):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    if k.strip().lower() == "session_id":
                        raw_token = v
                        break
                elif len(part) >= 16:
                    raw_token = part
                    break

    # 3. Из заголовка Authorization (например: "Bearer <token>" или просто "<token>")
    if not raw_token:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth_header:
            auth_str = auth_header.strip()
            if auth_str.lower().startswith("bearer "):
                raw_token = auth_str[7:].strip()
            else:
                raw_token = auth_str

    # 4. Из кастомных заголовков
    if not raw_token:
        for h in ["session_id", "session-id", "x-session-id", "token", "x-token"]:
            val = request.headers.get(h)
            if val:
                raw_token = val
                break

    # 5. Из query параметров
    if not raw_token:
        raw_token = request.query_params.get("session_id") or request.query_params.get("token")

    if not raw_token:
        return None

    cleaned = str(raw_token).strip().strip('"').strip("'").strip("<").strip(">").strip()
    return cleaned if cleaned else None



async def get_current_user_optional(request: Request) -> Optional[int]:
    session_id = extract_session_id(request)
    if not session_id:
        return None
    user_id = await get_session_user_id(session_id)
    return user_id


async def get_current_user_required(
    current_user_id: Optional[int] = Depends(get_current_user_optional),
) -> int:
    if current_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: session cookie or token required",
        )
    return current_user_id


# Алиас для обратной совместимости
async def get_current_user_id(
    current_user_id: int = Depends(get_current_user_required),
) -> int:
    return current_user_id
