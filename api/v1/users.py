from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import extract_session_id
from core.session import create_session, delete_session
from db.session import get_db
from models.user import User
from schemas.user import UserLoginRequest, UserLoginResponse, UserRegisterRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user_api(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.username == payload.username.strip())
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    new_user = User(
        username=payload.username.strip(),
        password=payload.password,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse(id=new_user.id, username=new_user.username)


@router.post("/authentication", response_model=UserLoginResponse, status_code=status.HTTP_200_OK, include_in_schema=False)
@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
async def login_user_api(
    payload: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.username == payload.username.strip())
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or user.password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    session_id = await create_session(user.id)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        path="/",
        max_age=86400,
    )

    return UserLoginResponse(
        session_id=session_id,
        token=session_id,
        user_id=user.id,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user_api(
    request: Request,
    response: Response,
):
    session_id = extract_session_id(request)
    if session_id:
        await delete_session(session_id)
    response.delete_cookie(key="session_id", path="/")
    return Response(status_code=status.HTTP_200_OK)
