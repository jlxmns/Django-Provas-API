from decimal import Decimal

from core import models
from core.tests.tests import BaseTestCase


class QuestaoListagemTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.questao01 = models.Questao.objects.create(
            text="Questão 01",
            peso=1,
            order=1,
        )

        self.questao02 = models.Questao.objects.create(
            text="Questão 02",
            peso=1,
            order=2,
        )

        self.questao03 = models.Questao.objects.create(
            text="Questão 03",
            peso=1,
            order=3,
        )

    def test_correct_items_and_quantity(self):
        response = self.client.get(
            "/questoes/listagem", headers=self.get_admin_headers()
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 3)

        texts = {p["text"] for p in response.json().get("items")}
        self.assertIn("Questão 01", texts)
        self.assertIn("Questão 02", texts)
        self.assertIn("Questão 03", texts)


class QuestaoCreateTestCase(BaseTestCase):
    def test_create_questao_success(self):
        payload = {
            "text": "Questão 01",
            "peso": 1,
            "order": 1,
        }

        response = self.client.post(
            "/questoes/create", json=payload, headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)

        questao_id = response.json()["id"]
        questao = models.Questao.objects.get(id=questao_id)
        self.assertEqual(questao.text, payload["text"])
        self.assertEqual(questao.peso, payload["peso"])
        self.assertEqual(questao.order, payload["order"])


class QuestaoRetrieveTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.questao = models.Questao.objects.create(text="Questão 01", peso=1, order=1)

    def test_retrieve_questao_success(self):
        response = self.client.post(
            f"/questoes/{self.questao.id}", headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.questao.id)
        self.assertEqual(response.json()["text"], self.questao.text)
        self.assertEqual(Decimal(response.json()["peso"]), self.questao.peso)
        self.assertEqual(response.json()["order"], self.questao.order)


class QuestaoPatchTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.questao = models.Questao.objects.create(text="Questão 01", peso=1, order=1)

    def test_retrieve_questao_success(self):
        response = self.client.patch(
            f"/questoes/update/{self.questao.id}",
            json={"text": "Questão 99"},
            headers=self.get_admin_headers(),
        )

        self.assertEqual(response.status_code, 200)
        updated_questao = models.Questao.objects.get(id=self.questao.id)
        self.assertEqual(updated_questao.text, "Questão 99")
        self.assertEqual(updated_questao.peso, 1)
        self.assertEqual(updated_questao.order, 1)


class ProvaDeleteTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.questao = models.Questao.objects.create(text="Questão 01", peso=1, order=1)

    def test_delete_questao_success(self):
        response = self.client.delete(
            f"/questoes/delete/{self.questao.id}", headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        deleted_questao = models.Questao.objects.filter(id=self.questao.id)
        self.assertEqual(deleted_questao.exists(), False)
