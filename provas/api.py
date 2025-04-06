from typing import List

from ninja.errors import HttpError
from ninja.throttling import AnonRateThrottle
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.exceptions import TokenError
from ninja_jwt.tokens import RefreshToken

from core.models import User
from ninja import NinjaAPI
from ninja.pagination import paginate
from .middleware import admin_only

from provas.schemas import LoginSchema, RegisterSchema, RefreshSchema, UserOut

api = NinjaAPI()


class AdminJWTAuth(JWTAuth):
    def authenticate(self, request, token: str) -> User:
        user = super().authenticate(request, token)
        if not user.is_admin():
            raise HttpError(403, "Admin access required")

        return user

######################################################################
# Autenticação & Usuários
######################################################################


@api.post("/login", throttle=AnonRateThrottle(rate="10/h"))
def login(request, data: LoginSchema):
    try:
        user = User.objects.get(username=data.email)
        if not user.check_password(data.password):
            raise HttpError(404, "Usuário não registrado ou senha incorreta.")

        refresh = RefreshToken.for_user(user)
        return {
            "message": "Login realizado com sucesso",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    except User.DoesNotExist:
        raise HttpError(404, "Usuário não registrado ou senha incorreta.")


@api.post("/register")
def register(request, data: RegisterSchema):
    if User.objects.filter(username=data.email).exists():
        raise HttpError(400, "Usuário já existente.")

    user = User.objects.create_user(
        username=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )

    refresh = RefreshToken.for_user(user)

    return {
        "message": "Usuário criado com sucesso",
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }


@api.post("/refresh")
def refresh(request, data: RefreshSchema):
    try:
        refresh = RefreshToken(data.refresh)
        new_access_token = str(refresh.access_token)
        user_id = refresh.payload.get("user_id")
        if not User.objects.filter(id=user_id).exists():
            raise HttpError(401, "Usuário não encontrado ou token inválida.")
        return {"access": new_access_token}
    except TokenError:
        raise HttpError(401, "Token inválida ou expirada.")


@api.get("/me", auth=JWTAuth())
def get_user_by_token(request):
    user = request.auth
    return {
        "id": user.id,
        "email": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name
    }


@api.get("/get_users", response=List[UserOut], auth=AdminJWTAuth())
@paginate
def get_users(request):
    return User.objects.all()
