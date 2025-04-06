from core.models import User
from django.http import HttpRequest
from ninja.security import HttpBearer
from ninja_jwt.tokens import UntypedToken
from typing import Optional, Any


class AuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
        try:
            user_id = UntypedToken(token).get("user_id")
            user = request.user = User.objects.get(id=user_id)
            return token
        except:
            return None


def is_admin(request):
    return request.user.role == User.Role.ADMIN
