from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.user import User
from schemas.user import UserLoginRequest, UserLoginResponse, UserRegisterRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


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


@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
async def login_user_api(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.username == payload.username.strip())
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or user.password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return UserLoginResponse(
        token=f"stub_session_token_user_{user.id}",
        user_id=user.id,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user_api():
    return Response(status_code=status.HTTP_200_OK)
