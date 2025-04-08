from typing import List

from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from ninja.throttling import AnonRateThrottle
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.exceptions import TokenError
from ninja_jwt.tokens import RefreshToken

from core.models import User, Prova, Questao
from ninja import NinjaAPI
from ninja.pagination import paginate

from provas import schemas

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
def login(request, data: schemas.LoginSchema):
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
def register(request, data: schemas.RegisterSchema):
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
def refresh(request, data: schemas.RefreshSchema):
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


@api.get("/get_users", response=List[schemas.UserOut], auth=AdminJWTAuth())
@paginate
def get_users(request):
    return User.objects.all()


@api.post("/create_user", auth=AdminJWTAuth())
def create_user(request, payload: schemas.UserIn):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Usuário já existente.")

    user = User.objects.create_user(**payload.dict())

    refresh = RefreshToken.for_user(user)

    return {
        "message": "Usuário criado com sucesso",
        "id": user.id,
    }


@api.post("/users/{user_id}", auth=AdminJWTAuth(), response=schemas.UserOut)
def retrieve_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return user


@api.patch("/update_user/{user_id}")
def update_user(request, user_id: int, payload: schemas.UserPatch):
    user = get_object_or_404(User, id=user_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(user, attr, value)
    user.save()
    return {"message": f"Usuário ID f{user.id} modificado com sucesso."}


@api.delete("delete_user/{user_id}")
def delete_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return {"message": f"Usuário ID {user_id} deletado."}


######################################################################
# Provas
######################################################################


@api.get("/get_provas", response=List[schemas.ProvasOut])
@paginate
def get_prova(request):
    return Prova.objects.all()


@api.post("/create_prova")
def create_prova(request, payload: schemas.ProvasIn):
    prova = Prova.objects.create(**payload.dict())

    return {
        "message": "Prova criada com sucesso",
        "id": prova.id,
    }


@api.post("/provas/{prova_id}", response=schemas.ProvasOut)
def retrieve_prova(request, prova_id: int):
    prova = get_object_or_404(Prova, id=prova_id)
    return prova


@api.patch("/update_prova/{prova_id}")
def update_prova(request, prova_id: int, payload: schemas.ProvasPatch):
    prova = get_object_or_404(Prova, id=prova_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(prova, attr, value)
    prova.save()
    return {"message": f"Prova ID f{prova.id} modificada com sucesso."}


@api.delete("delete_prova/{prova_id}")
def delete_prova(request, prova_id: int):
    prova = get_object_or_404(Prova, id=prova_id)
    prova.delete()
    return {"message": f"Prova ID {prova_id} deletada."}


@api.get("provas/{prova_id}/questoes", response=List[schemas.QuestoesOut])
@paginate
def retrieve_questoes_from_prova(request, prova_id: int):
    prova = get_object_or_404(Prova, id=prova_id)
    return prova.questoes.all()


@transaction.atomic
@api.post("/provas/{prova_id}/add_questoes")
def add_questao_to_prova(request, payload: schemas.QuestoesProva):
    prova = get_object_or_404(Prova, id=payload.prova_id)
    for questao_id in payload.questao_id:
        questao = get_object_or_404(Questao, id=questao_id)
        prova.questoes.add(questao)
    return {'message': f"Questão(s) ID {', '.join(str(q_id) for q_id in payload.questao_id)} adicionadas(s) à prova ID {prova.id}"}


@transaction.atomic
@api.delete("/provas/{prova_id}/remover_questoes")
def remove_questao_from_prova(request, payload: schemas.QuestoesProva):
    prova = get_object_or_404(Prova, id=payload.prova_id)
    for questao_id in payload.questao_id:
        questao = get_object_or_404(Questao, id=questao_id)
        prova.questoes.remove(questao)
    return {'message': f"Questão(s) ID {', '.join(str(q_id) for q_id in payload.questao_id)} removida(s) da prova ID {prova.id}"}


######################################################################
# Questões
######################################################################


@api.get("/get_questoes", response=List[schemas.QuestoesOut])
@paginate
def get_questao(request):
    return Questao.objects.all()


@api.post("/create_questao")
def create_questao(request, payload: schemas.QuestoesIn):
    questao = Questao.objects.create(**payload.dict())

    return {
        "message": "Questão criada com sucesso",
        "id": questao.id,
    }


@api.post("/questoes/{questao_id}", response=schemas.QuestoesOut)
def retrieve_questao(request, questao_id: int):
    questao = get_object_or_404(Questao, id=questao_id)
    return questao


@api.patch("/update_questao/{questao_id}")
def update_questao(request, questao_id: int, payload: schemas.QuestoesPatch):
    questao = get_object_or_404(Questao, id=questao_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(questao, attr, value)
    questao.save()
    return {"message": f"Questão ID {questao.id} modificada com sucesso."}


@api.delete("delete_questao/{questao_id}")
def delete_questao(request, questao_id: int):
    questao = get_object_or_404(Questao, id=questao_id)
    questao.delete()
    return {"message": f"Questão ID {questao_id} deletada."}
