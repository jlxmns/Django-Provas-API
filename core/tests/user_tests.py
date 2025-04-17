from core import models
from core.tests.tests import BaseTestCase


class UserListagemTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_correct_items_and_quantity(self):
        response = self.client.get("users/listagem", headers=self.get_admin_headers())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 2)
        user_ids = {p["id"] for p in response.json().get("items")}
        self.assertIn(self.admin_user.id, user_ids)
        self.assertIn(self.regular_user.id, user_ids)


class UserCreateTestCase(BaseTestCase):
    def test_create_user(self):
        payload = {
            "username": "Django",
            "password": "django123",
            "first_name": "Django",
            "last_name": "Python",
            "role": models.User.Role.PARTICIPANTE,
            "email": "django@python.com",
        }

        response = self.client.post(
            "users/create_user", json=payload, headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        user_id = response.json()["id"]
        user = models.User.objects.get(id=user_id)
        self.assertEqual(user.username, payload["username"])
        self.assertEqual(user.first_name, payload["first_name"])
        self.assertEqual(user.last_name, payload["last_name"])
        self.assertEqual(user.role, payload["role"])
        self.assertEqual(user.email, payload["email"])


class UserRetrieveTestCase(BaseTestCase):
    def test_retrieve_user(self):
        response = self.client.post(
            f"users/{self.regular_user.id}", headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        user_id = response.json()["id"]
        user = models.User.objects.get(id=user_id)
        self.assertEqual(self.regular_user.username, user.username)
        self.assertEqual(self.regular_user.first_name, user.first_name)
        self.assertEqual(self.regular_user.last_name, user.last_name)
        self.assertEqual(self.regular_user.role, user.role)
        self.assertEqual(self.regular_user.email, user.email)


class UserPatchTestCase(BaseTestCase):
    def test_patch_user(self):
        payload = {
            "name": "jlxmns",
        }

        response = self.client.patch(
            f"/users/update/{self.admin_user.id}",
            json=payload,
            headers=self.get_admin_headers(),
        )

        self.assertEqual(response.status_code, 200)
        user_id = response.json()["id"]
        user = models.User.objects.get(id=user_id)
        self.assertEqual("jlxmns", user.name)


class UserDeleteTestCase(BaseTestCase):
    def test_delete_user(self):
        response = self.client.delete(
            f"/users/delete/{self.regular_user.id}", headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        user_id = response.json()["id"]
        user = models.User.objects.filter(id=user_id)
        self.assertEqual(user.exists(), False)
