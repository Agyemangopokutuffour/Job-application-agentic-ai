import os

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from managers.user_manager import get_user_manager
from models.schemas import UserCreate, UserRead, UserUpdate
from models.user import User

load_dotenv()

SECRET = os.getenv("JWT_SECRET", "change-me-in-production")

bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)

router = APIRouter()
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router.include_router(fastapi_users.get_auth_router(auth_backend))
router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))
