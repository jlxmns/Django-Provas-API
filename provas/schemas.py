from ninja import Schema, ModelSchema
from core.models import User


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
        fields = ['id', 'username', 'first_name', 'last_name', 'role']
