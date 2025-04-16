from core import models
from core.tests.tests import BaseTestCase


class RespostaListagemTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.questao = models.Questao.objects.create(text="Questão 01", peso=1, order=1)

        self.resposta1 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 01", is_correct=True
        )
        self.resposta2 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 02", is_correct=True
        )
        self.resposta3 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 03", is_correct=True
        )

    def test_correct_items_and_quantity(self):
        response = self.client.get(
            "/respostas/listagem", headers=self.get_admin_headers()
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 3)

        texts = {p["text"] for p in response.json().get("items")}
        self.assertIn("Resposta 01", texts)
        self.assertIn("Resposta 02", texts)
        self.assertIn("Resposta 03", texts)


class RespostaCreateTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.questao = models.Questao.objects.create(text="Questão 01", peso=1, order=1)

    def test_create_resposta_success(self):
        payload = {
            "questao_id": self.questao.id,
            "text": "Resposta 01",
            "is_correct": True,
        }

        response = self.client.post(
            "/respostas/create", json=payload, headers=self.get_admin_headers()
        )
        self.assertEqual(response.status_code, 200)

        resposta_id = response.json()["id"]
        resposta = models.Resposta.objects.get(id=resposta_id)
        self.assertEqual(resposta.questao.id, payload["questao_id"])
        self.assertEqual(resposta.text, payload["text"])
        self.assertEqual(resposta.is_correct, payload["is_correct"])


class RespostaRetrieveTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.questao = models.Questao.objects.create(text="Questão 01", peso=1, order=1)

        self.resposta = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 01", is_correct=True
        )

    def test_retrieve_resposta_success(self):
        response = self.client.post(
            f"/respostas/{self.resposta.id}", headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.resposta.id)
        self.assertEqual(response.json()["text"], self.resposta.text)
        self.assertEqual(response.json()["is_correct"], self.resposta.is_correct)


class RespostaPatchTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.questao = models.Questao.objects.create(text="Questão 01", peso=1, order=1)

        self.resposta = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 01", is_correct=True
        )

    def test_retrieve_resposta_success(self):
        response = self.client.patch(
            f"/respostas/update/{self.resposta.id}",
            json={"is_correct": False},
            headers=self.get_admin_headers(),
        )

        self.assertEqual(response.status_code, 200)
        updated_resposta = models.Resposta.objects.get(id=self.resposta.id)
        self.assertEqual(updated_resposta.is_correct, False)
        self.assertEqual(updated_resposta.text, "Resposta 01")


class RespostaDeleteTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.questao = models.Questao.objects.create(text="Questão 01", peso=1, order=1)

        self.resposta = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 01", is_correct=True
        )

    def test_delete_resposta_success(self):
        response = self.client.delete(
            f"/respostas/delete/{self.resposta.id}", headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        deleted_resposta = models.Resposta.objects.filter(id=self.resposta.id)
        self.assertEqual(deleted_resposta.exists(), False)
