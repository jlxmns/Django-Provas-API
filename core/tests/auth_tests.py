from core.tests.tests import BaseTestCase


class LoginTestCase(BaseTestCase):
    def test_login_success(self):
        payload = {"email": "regular", "password": "regular"}

        response = self.client.post(
            "/login",
            json=payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())
        self.assertEqual(response.data["message"], "Login realizado com sucesso")


class RegisterTestCase(BaseTestCase):
    def test_register_success(self):
        payload = {
            "username": "new_user",
            "password": "new_user",
            "first_name": "new",
            "last_name": "user",
        }

        response = self.client.post("/register", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())
        self.assertEqual(response.data["message"], "Usuário criado com sucesso")
