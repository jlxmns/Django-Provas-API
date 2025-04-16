from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from ninja import Query
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja.throttling import AnonRateThrottle
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.exceptions import TokenError
from ninja_jwt.tokens import RefreshToken

from core.models import (
    Prova,
    Questao,
    Ranking,
    RegistroRanking,
    Resposta,
    RespostaParticipante,
    TentativaProva,
    User,
)
from provas import schemas

api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)


class AdminJWTAuth(JWTAuth):
    def authenticate(self, request, token: str) -> User:
        user = super().authenticate(request, token)
        if not user.is_admin():
            raise HttpError(403, "Admin access required")

        return user


######################################################################
# Autenticação
######################################################################


@api.post("/login", throttle=AnonRateThrottle(rate="10/h"), tags=["auth"])
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


@api.post("/register", tags=["auth"])
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


@api.post("/refresh", tags=["auth"])
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


@api.get("/me", auth=JWTAuth(), tags=["auth"])
def get_user_by_token(request):
    user = request.auth
    return {
        "id": user.id,
        "email": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


######################################################################
# Users
######################################################################


@api.get(
    "/get_users", response=list[schemas.UserOut], auth=AdminJWTAuth(), tags=["users"]
)
@decorate_view(cache_page(60 * 15))
@paginate
def get_users(
    request,
    name: str = None,
    order_by: str | None = Query(None, description="Ordenar por campo. Ex: '-nome'"),
):
    queryset = User.objects.all()

    if name:
        queryset = queryset.filter(
            Q(name__icontains=name)
            | Q(first_name__iexact=name)
            | Q(last_name__iexact=name)
        )

    if order_by:
        queryset = queryset.order_by(order_by)

    return queryset


@api.post("/create_user", auth=AdminJWTAuth(), tags=["users"])
def create_user(request, payload: schemas.UserIn):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Usuário já existente.")

    user = User.objects.create_user(**payload.dict())

    RefreshToken.for_user(user)

    return {
        "message": "Usuário criado com sucesso",
        "id": user.id,
    }


@api.post(
    "/users/{user_id}", auth=AdminJWTAuth(), response=schemas.UserOut, tags=["users"]
)
def retrieve_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return user


@api.patch("/update_user/{user_id}", tags=["users"])
def update_user(request, user_id: int, payload: schemas.UserPatch):
    user = get_object_or_404(User, id=user_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(user, attr, value)
    user.save()
    return {"message": f"Usuário ID f{user.id} modificado com sucesso."}


@api.delete("delete_user/{user_id}", tags=["users"])
def delete_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return {"message": f"Usuário ID {user_id} deletado."}


######################################################################
# Provas
######################################################################


@api.get(
    "/provas/listagem",
    response=list[schemas.ProvasOut],
    tags=["provas"],
    auth=AdminJWTAuth(),
)
@decorate_view(cache_page(60 * 15))
@paginate
def get_prova(
    request,
    q: str = None,
    order_by: str | None = Query(None, description="Ordenar por campo. Ex: '-nome'"),
):
    queryset = Prova.objects.all()

    if q:
        queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))

    if order_by:
        queryset = queryset.order_by(order_by)

    return queryset


@api.post("/provas/create", tags=["provas"])
def create_prova(request, payload: schemas.ProvasIn):
    prova = Prova.objects.create(**payload.dict())

    return {
        "message": "Prova criada com sucesso",
        "id": prova.id,
    }


@api.post("/provas/{prova_id}", response=schemas.ProvasOut, tags=["provas"])
def retrieve_prova(request, prova_id: int):
    prova = get_object_or_404(Prova, id=prova_id)
    return prova


@api.patch("/provas/update/{prova_id}", tags=["provas"])
def update_prova(request, prova_id: int, payload: schemas.ProvasPatch):
    prova = get_object_or_404(Prova, id=prova_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(prova, attr, value)
    prova.save()
    return {"message": f"Prova ID f{prova.id} modificada com sucesso."}


@api.delete("/provas/delete/{prova_id}", tags=["provas"])
def delete_prova(request, prova_id: int):
    prova = get_object_or_404(Prova, id=prova_id)
    prova.delete()
    return {"message": f"Prova ID {prova_id} deletada."}


@api.get(
    "/provas/{prova_id}/questoes", response=list[schemas.QuestoesOut], tags=["provas"]
)
@decorate_view(cache_page(60 * 15))
@paginate
def retrieve_questoes_from_prova(request, prova_id: int):
    prova = get_object_or_404(Prova, id=prova_id)
    return prova.questoes.all()


@api.post("/provas/{prova_id}/add_questoes", tags=["provas"])
def add_questao_to_prova(request, prova_id: int, payload: schemas.QuestoesProva):
    prova = get_object_or_404(Prova, id=prova_id)
    for questao_id in payload.questao_id:
        questao = get_object_or_404(Questao, id=questao_id)
        prova.questoes.add(questao)
    return {
        "message": f"Questão(s) ID {', '.join(str(q_id) for q_id in payload.questao_id)} adicionadas(s) à prova ID {prova.id}"
    }


@api.delete("/provas/{prova_id}/remover_questoes", tags=["provas"])
def remove_questao_from_prova(request, prova_id: int, payload: schemas.QuestoesProva):
    prova = get_object_or_404(Prova, id=prova_id)
    for questao_id in payload.questao_id:
        questao = get_object_or_404(Questao, id=questao_id)
        prova.questoes.remove(questao)
    return {
        "message": f"Questão(s) ID {', '.join(str(q_id) for q_id in payload.questao_id)} removida(s) da prova ID {prova.id}"
    }


######################################################################
# Questões
######################################################################


@api.get("/questoes/listagem", response=list[schemas.QuestoesOut], tags=["questoes"])
@decorate_view(cache_page(60 * 15))
@paginate
def get_questao(
    request,
    q: str = None,
    order_by: str | None = Query(None, description="Ordenar por campo. Ex: '-nome'"),
):
    queryset = Questao.objects.all()

    if q:
        queryset = queryset.filter(text__icontains=q)

    if order_by:
        queryset = queryset.order_by(order_by)

    return queryset


@api.post("/questoes/create", tags=["questoes"])
def create_questao(request, payload: schemas.QuestoesIn):
    questao = Questao.objects.create(**payload.dict())

    return {
        "message": "Questão criada com sucesso",
        "id": questao.id,
    }


@api.post("/questoes/{questao_id}", response=schemas.QuestoesOut, tags=["questoes"])
def retrieve_questao(request, questao_id: int):
    questao = get_object_or_404(Questao, id=questao_id)
    return questao


@api.patch("/questoes/update/{questao_id}", tags=["questoes"])
def update_questao(request, questao_id: int, payload: schemas.QuestoesPatch):
    questao = get_object_or_404(Questao, id=questao_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(questao, attr, value)
    questao.save()
    return {"message": f"Questão ID {questao.id} modificada com sucesso."}


@api.delete("/questoes/delete/{questao_id}", tags=["questoes"])
def delete_questao(request, questao_id: int):
    questao = get_object_or_404(Questao, id=questao_id)
    questao.delete()
    return {"message": f"Questão ID {questao_id} deletada."}


######################################################################
# Respostas
######################################################################


@api.get("/respostas/listagem", response=list[schemas.RespostasOut], tags=["respostas"])
@decorate_view(cache_page(60 * 15))
@paginate
def get_respostas(
    request,
    q: str = None,
    order_by: str | None = Query(None, description="Ordenar por campo. Ex: '-nome'"),
):
    queryset = Resposta.objects.all()

    if q:
        queryset = queryset.filter(text__icontains=q)

    if order_by:
        queryset = queryset.order_by(order_by)

    return queryset


@api.post("/respostas/create", tags=["respostas"])
def create_resposta(request, payload: schemas.RespostasIn):
    questao = Questao.objects.get(id=payload.questao)
    resposta = Resposta.objects.create(
        questao=questao,
        text=payload.text,
        is_correct=payload.is_correct,
    )

    return {
        "message": "Resposta criada com sucesso",
        "id": resposta.id,
    }


@api.post("/respostas/{resposta_id}", response=schemas.RespostasOut, tags=["respostas"])
def retrieve_resposta(request, resposta_id: int):
    resposta = get_object_or_404(Resposta, id=resposta_id)
    return resposta


@api.patch("/respostas/update/{resposta_id}", tags=["respostas"])
def update_resposta(request, resposta_id: int, payload: schemas.RespostasPatch):
    resposta = get_object_or_404(Resposta, id=resposta_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(resposta, attr, value)
    resposta.save()
    return {"message": f"Resposta ID {resposta.id} modificada com sucesso."}


@api.delete("/respostas/delete/{resposta_id}", tags=["respostas"])
def delete_resposta(request, resposta_id: int):
    resposta = get_object_or_404(Resposta, id=resposta_id)
    resposta.delete()
    return {"message": f"Questão ID {resposta_id} deletada."}


######################################################################
# API para Participantes
######################################################################


@api.get(
    path="/participante/provas",
    response=list[schemas.TentativaProvaOut],
    tags=["portal_participante"],
    auth=JWTAuth(),
)
@decorate_view(cache_page(60 * 15))
@paginate
def get_participante_prova(
    request,
    q: str = None,
    order_by: str | None = Query(None, description="Ordenar por campo. Ex: '-nome'"),
):
    user = request.user
    tentativas = TentativaProva.objects.filter(user=user)

    if q:
        tentativas = tentativas.filter(prova__title__icontains=q)

    if order_by:
        tentativas = tentativas.order_by(order_by)

    return tentativas


@api.post("/participante/create_resposta", tags=["portal_participante"], auth=JWTAuth())
def create_participante_resposta(request, payload: schemas.RespostaParticipanteIn):
    tentativa_prova = TentativaProva.objects.get(id=payload.tentativa_prova)
    questao = Questao.objects.get(id=payload.questao)
    resposta_escolhida = Resposta.objects.get(id=payload.resposta_escolhida)
    resposta_participante = RespostaParticipante.objects.create(
        tentativa_prova=tentativa_prova,
        questao=questao,
        resposta_escolhida=resposta_escolhida,
    )

    return {
        "message": "Resposta de participante criada com sucesso",
        "id": resposta_participante.id,
    }


@api.patch(
    "/participante/update_resposta/{resposta_participante_id}",
    tags=["portal_participante"],
    auth=JWTAuth(),
)
def update_participante_resposta(
    request, resposta_participante_id: int, payload: schemas.RespostaParticipantePatch
):
    resposta_participante = get_object_or_404(
        RespostaParticipante, id=resposta_participante_id
    )

    if resposta_participante.tentativa_prova.user != request.user:
        return {"message": "Sem permissão para modificar essa resposta."}

    for attr, value in payload.dict(exclude_unset=True).items():
        print(attr, value)
        field = attr.replace("_id", "")
        setattr(resposta_participante, f"{field}_id", value)
    resposta_participante.save()
    return {
        "message": f"Resposta da Questão {resposta_participante.questao} modificada com sucesso."
    }


######################################################################
# Respostas de Participantes
######################################################################


@api.get(
    "/get_respostas_participante",
    response=list[schemas.RespostaParticipanteOut],
    tags=["respostas_participantes"],
)
@decorate_view(cache_page(60 * 15))
@paginate
def get_respostas_participante(
    request,
    q: str = None,
    order_by: str | None = Query(None, description="Ordenar por campo. Ex: '-nome'"),
):
    queryset = RespostaParticipante.objects.all()

    if q:
        queryset = queryset.filter(
            Q(questao__text__icontains=q) | Q(resposta_escolhida__text__icontains=q)
        )

    if order_by:
        queryset = queryset.order_by(order_by)

    return queryset


@api.post("/create_resposta_participante", tags=["respostas_participantes"])
def create_resposta_participante(request, payload: schemas.RespostaParticipanteIn):
    resposta_participante = RespostaParticipante.objects.create(**payload.dict())

    return {
        "message": "Resposta de participante criada com sucesso",
        "id": resposta_participante.id,
    }


@api.patch(
    "/update_resposta_participante/{resposta_participante_id}",
    tags=["respostas_participantes"],
)
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


######################################################################
# Ranking
######################################################################


@api.post("/ranking/{prova_id}", response=schemas.RankingOut, tags=["ranking"])
def retrieve_ranking_from_prova(request, prova_id: int):
    ranking = get_object_or_404(Ranking, prova_id=prova_id)

    return RegistroRanking.objects.filter(ranking=ranking).order_by("posicao")
