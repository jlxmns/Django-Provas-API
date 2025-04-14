from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja.throttling import AnonRateThrottle
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.exceptions import TokenError
from ninja_jwt.tokens import RefreshToken

from core.models import Prova, Questao, Resposta, RespostaParticipante, User
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
    except User.DoesNotExist as err:
        raise HttpError(404, "Usuário não registrado ou senha incorreta.") from err


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
        "refresh": str(refresh),
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
    except TokenError as err:
        raise HttpError(401, "Token inválida ou expirada.") from err


@api.get("/me", auth=JWTAuth())
def get_user_by_token(request):
    user = request.auth
    return {
        "id": user.id,
        "email": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


@api.get("/get_users", response=list[schemas.UserOut], auth=AdminJWTAuth())
@paginate
def get_users(request, name: str = None):
    if name:
        return User.objects.filter(
            Q(name__icontains=name)
            | Q(first_name__iexact=name)
            | Q(last_name__iexact=name)
        )
    return User.objects.all()


@api.post("/create_user", auth=AdminJWTAuth())
def create_user(request, payload: schemas.UserIn):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Usuário já existente.")

    user = User.objects.create_user(**payload.dict())

    RefreshToken.for_user(user)

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


@api.get("/get_provas", response=list[schemas.ProvasOut])
@paginate
def get_prova(request, q: str = None):
    if q:
        return Prova.objects.filter(Q(title__icontains=q) | Q(description__icontains=q))
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


@api.get("provas/{prova_id}/questoes", response=list[schemas.QuestoesOut])
@paginate
def retrieve_questoes_from_prova(request, prova_id: int):
    prova = get_object_or_404(Prova, id=prova_id)
    return prova.questoes.all()


@api.post("/provas/{prova_id}/add_questoes")
def add_questao_to_prova(request, prova_id: int, payload: schemas.QuestoesProva):
    prova = get_object_or_404(Prova, id=prova_id)
    for questao_id in payload.questao_id:
        questao = get_object_or_404(Questao, id=questao_id)
        prova.questoes.add(questao)
    return {
        "message": f"Questão(s) ID {', '.join(str(q_id) for q_id in payload.questao_id)} adicionadas(s) à prova ID {prova.id}"
    }


@api.delete("/provas/{prova_id}/remover_questoes")
def remove_questao_from_prova(request, prova_id: int, payload: schemas.QuestoesProva):
    prova = get_object_or_404(Prova, id=payload.prova_id)
    for questao_id in payload.questao_id:
        questao = get_object_or_404(Questao, id=questao_id)
        prova.questoes.remove(questao)
    return {
        "message": f"Questão(s) ID {', '.join(str(q_id) for q_id in payload.questao_id)} removida(s) da prova ID {prova.id}"
    }


######################################################################
# Questões
######################################################################


@api.get("/get_questoes", response=list[schemas.QuestoesOut])
@paginate
def get_questao(request, q: str = None):
    if q:
        return Questao.objects.filter(text__icontains=q)
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


######################################################################
# Respostas
######################################################################


@api.get("/get_respostas", response=list[schemas.RespostasOut])
@paginate
def get_respostas(request, q: str = None):
    if q:
        return Resposta.objects.filter(text__icontains=q)
    return Resposta.objects.all()


@api.post("/create_resposta")
def create_resposta(request, payload: schemas.RespostasIn):
    resposta = Resposta.objects.create(**payload.dict())

    return {
        "message": "Resposta criada com sucesso",
        "id": resposta.id,
    }


@api.post("/respostas/{resposta_id}", response=schemas.RespostasOut)
def retrieve_resposta(request, resposta_id: int):
    resposta = get_object_or_404(Questao, id=resposta_id)
    return resposta


@api.patch("/update_resposta/{resposta_id}")
def update_resposta(request, resposta_id: int, payload: schemas.RespostasPatch):
    resposta = get_object_or_404(Resposta, id=resposta_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(resposta, attr, value)
    resposta.save()
    return {"message": f"Resposta ID {resposta.id} modificada com sucesso."}


@api.delete("resposta/{resposta_id}")
def delete_resposta(request, resposta_id: int):
    resposta = get_object_or_404(Resposta, id=resposta_id)
    resposta.delete()
    return {"message": f"Questão ID {resposta_id} deletada."}


######################################################################
# Respostas de Participantes
######################################################################


@api.get("/get_respostas_participante", response=list[schemas.RespostaParticipanteOut])
@paginate
def get_respostas_participante(request, q: str = None):
    if q:
        return RespostaParticipante.objects.filter(
            Q(questao__text__icontains=q) | Q(resposta_escolhida__text__icontains=q)
        )
    return RespostaParticipante.objects.all()


@api.post("/create_resposta_participante")
def create_resposta_participante(request, payload: schemas.RespostaParticipanteIn):
    resposta_participante = RespostaParticipante.objects.create(**payload.dict())

    return {
        "message": "Resposta de participante criada com sucesso",
        "id": resposta_participante.id,
    }


@api.patch("/update_resposta_participante/{resposta_participante_id}")
def update_resposta_participante(
    request, resposta_participante_id: int, payload: schemas.RespostaParticipantePatch
):
    resposta_participante = get_object_or_404(
        RespostaParticipante, id=resposta_participante_id
    )
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(resposta_participante, attr, value)
    resposta_participante.save()
    return {
        "message": f"Resposta de Participante ID {resposta_participante.id} modificada com sucesso."
    }
