from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from provas import settings

User = get_user_model()


class CeleryBeatTestCase(TestCase):
    def setUp(self):
        self.settings_override = override_settings(
            INSTALLED_APPS=[*settings.INSTALLED_APPS, "django_celery_beat"]
        )
        self.settings_override.enable()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.settings_override.disable()


class LoginTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.client = Client()

    def test_details(self):
        response = self.client.get("/api/get_users")

        self.assertEqual(response.status_code, 200)
