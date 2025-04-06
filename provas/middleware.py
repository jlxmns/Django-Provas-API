from ninja.errors import HttpError


def admin_only(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin():
            raise HttpError(403, "Acesso negado.")
        return func(request, *args, **kwargs)
    return wrapper
