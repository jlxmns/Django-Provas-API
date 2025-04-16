import os

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import RequestFactory, TestCase
from ninja.testing import TestClient
from ninja_jwt.tokens import AccessToken

from provas.api import api

User = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        # self.settings_override = override_settings(
        #     INSTALLED_APPS=[*settings.INSTALLED_APPS, "django_celery_beat"]
        # )
        # self.settings_override.enable()
        # super().setUp()

        os.environ["NINJA_SKIP_REGISTRY"] = "yes"

        self.client = TestClient(api)
        self.factory = RequestFactory()

        self.admin_user = User.objects.create_user(
            username="admin",
            password="admin",
            name="admin",
            email="admin@admin.com",
            role=User.Role.ADMIN,
        )
        self.admin_token = str(AccessToken.for_user(self.admin_user))

        self.regular_user = User.objects.create_user(
            username="regular",
            password="regular",
            email="regular@user.com",
            name="regular_user",
            role=User.Role.PARTICIPANTE,
        )
        self.regular_token = str(AccessToken.for_user(self.regular_user))

    def get_admin_headers(self):
        return {"Authorization": f"Bearer {self.admin_token}"}

    def get_regular_headers(self):
        return {"Authorization": f"Bearer {self.regular_token}"}

    def tearDown(self):
        cache.clear()

    #     super().tearDown()
    #     self.settings_override.disable()
