from ninja import ModelSchema, Schema

from core.models import Prova, Questao, Resposta, RespostaParticipante, User


class RegisterSchema(Schema):
    email: str
    first_name: str
    last_name: str
    password: str


class LoginSchema(Schema):
    email: str
    password: str


class RefreshSchema(Schema):
    refresh: str


class UserOut(ModelSchema):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "role"]


class UserIn(ModelSchema):
    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "role", "email"]


class UserPatch(ModelSchema):
    class Meta:
        model = User
        exclude = ["id", "last_login", "is_superuser", "date_joined"]
        fields_optional = "__all__"


class ProvasOut(ModelSchema):
    class Meta:
        model = Prova
        fields = "__all__"


class ProvasIn(ModelSchema):
    class Meta:
        model = Prova
        exclude = ["id", "date_created", "date_changed", "active"]


class ProvasPatch(ModelSchema):
    class Meta:
        model = Prova
        exclude = ["id", "date_created", "date_changed"]
        fields_optional = "__all__"


class QuestoesOut(ModelSchema):
    class Meta:
        model = Questao
        fields = "__all__"


class QuestoesIn(ModelSchema):
    class Meta:
        model = Questao
        exclude = ["id", "date_created", "date_changed", "active", "provas"]


class QuestoesPatch(ModelSchema):
    class Meta:
        model = Questao
        exclude = ["id", "date_created", "date_changed", "active", "provas"]
        fields_optional = "__all__"


class QuestoesProva(Schema):
    questao_id: list[int]


class RespostasOut(ModelSchema):
    class Meta:
        model = Resposta
        fields = "__all__"


class RespostasIn(ModelSchema):
    class Meta:
        model = Resposta
        fields = ["questao", "text", "is_correct"]


class RespostasPatch(ModelSchema):
    class Meta:
        model = Resposta
        fields = ["questao", "text", "is_correct"]
        fields_optional = "__all__"


class RespostaParticipanteIn(ModelSchema):
    class Meta:
        model = RespostaParticipante
        fields = ["tentativa_prova", "questao", "resposta_escolhida"]


class RespostaParticipanteOut(ModelSchema):
    class Meta:
        model = RespostaParticipante
        fields = "__all__"


class RespostaParticipantePatch(ModelSchema):
    class Meta:
        model = RespostaParticipante
        fields = ["tentativa_prova", "questao", "resposta_escolhida"]
        optional_fields = "__all__"
