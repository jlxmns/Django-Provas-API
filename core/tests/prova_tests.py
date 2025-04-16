from core import models
from core.tests.tests import BaseTestCase


class ProvaListagemTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.prova1 = models.Prova.objects.create(
            title="Prova de Matemática", description="Prova sobre conjuntos"
        )
        self.prova2 = models.Prova.objects.create(
            title="Prova de Biologia", description="Prova sobre evolução"
        )
        self.prova3 = models.Prova.objects.create(
            title="Prova de História", description="Prova sobre a ditadura militar"
        )

    def test_correct_items_and_quantity(self):
        response = self.client.get("/provas/listagem", headers=self.get_admin_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 3)

        titles = {p["title"] for p in response.json().get("items")}
        self.assertIn("Prova de Matemática", titles)
        self.assertIn("Prova de Biologia", titles)
        self.assertIn("Prova de História", titles)


class ProvaCreateTestCase(BaseTestCase):
    def test_create_prova_success(self):
        payload = {
            "title": "Prova de Física",
            "description": "Prova sobre termodinâmica",
        }

        response = self.client.post(
            "/provas/create", json=payload, headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)

        prova_id = response.json()["id"]
        prova = models.Prova.objects.get(id=prova_id)
        self.assertEqual(prova.title, payload["title"])
        self.assertEqual(prova.description, payload["description"])


class ProvaRetrieveTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.prova = models.Prova.objects.create(
            title="Prova de Física", description="Prova sobre termodinâmica"
        )

    def test_retrieve_prova_success(self):
        response = self.client.post(
            f"/provas/{self.prova.id}", headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.prova.id)
        self.assertEqual(response.json()["title"], self.prova.title)
        self.assertEqual(response.json()["description"], self.prova.description)


class ProvaPatchTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.prova = models.Prova.objects.create(
            title="Prova de Física", description="Prova sobre termodinâmica"
        )

    def test_retrieve_prova_success(self):
        response = self.client.patch(
            f"/provas/update/{self.prova.id}",
            json={"title": "Novo título"},
            headers=self.get_admin_headers(),
        )

        self.assertEqual(response.status_code, 200)
        updated_prova = models.Prova.objects.get(id=self.prova.id)
        self.assertEqual(updated_prova.title, "Novo título")
        self.assertEqual(updated_prova.description, "Prova sobre termodinâmica")


class ProvaDeleteTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.prova = models.Prova.objects.create(
            title="Prova de Física", description="Prova sobre termodinâmica"
        )

    def test_delete_prova_success(self):
        response = self.client.delete(
            f"/provas/delete/{self.prova.id}", headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        deleted_prova = models.Prova.objects.filter(id=self.prova.id)
        self.assertEqual(deleted_prova.exists(), False)


class ProvaRetrieveQuestoesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.prova_retrieve_questoes = models.Prova.objects.create(
            title="Prova de Física", description="Prova sobre termodinâmica"
        )

        self.questao1 = models.Questao.objects.create(
            text="Questão 01", peso=3, order=2
        )
        self.questao2 = models.Questao.objects.create(
            text="Questão 02", peso=1, order=1
        )
        self.questao3 = models.Questao.objects.create(
            text="Questão 03", peso=2, order=5
        )

        self.prova_retrieve_questoes.questoes.set(
            [self.questao1, self.questao2, self.questao3]
        )

    def test_retrieve_questoes_prova(self):
        response = self.client.get(
            f"/provas/{self.prova_retrieve_questoes.id}/questoes",
            headers=self.get_admin_headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 3)
        texts = {p["text"] for p in response.json().get("items")}
        self.assertIn("Questão 01", texts)
        self.assertIn("Questão 02", texts)
        self.assertIn("Questão 03", texts)


class ProvaAddQuestoesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.prova = models.Prova.objects.create(
            title="Prova de Física", description="Prova sobre termodinâmica"
        )

        self.questao1 = models.Questao.objects.create(
            text="Questão 01", peso=3, order=2
        )
        self.questao2 = models.Questao.objects.create(
            text="Questão 02", peso=1, order=1
        )
        self.questao3 = models.Questao.objects.create(
            text="Questão 03", peso=2, order=5
        )

        self.prova.questoes.set([self.questao1, self.questao2, self.questao3])

    def test_add_questoes_prova(self):
        questao_04 = models.Questao.objects.create(text="Questão 04", peso=6, order=4)

        payload = {"questao_id": [questao_04.id]}

        response = self.client.post(
            f"/provas/{self.prova.id}/add_questoes",
            json=payload,
            headers=self.get_admin_headers(),
        )

        self.assertEqual(response.status_code, 200)

        count = self.prova.questoes.count()
        self.assertEqual(count, 4)


class ProvaDeleteQuestoesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.prova = models.Prova.objects.create(
            title="Prova de Física", description="Prova sobre termodinâmica"
        )

        self.questao1 = models.Questao.objects.create(
            text="Questão 01", peso=3, order=2
        )
        self.questao2 = models.Questao.objects.create(
            text="Questão 02", peso=1, order=1
        )
        self.questao3 = models.Questao.objects.create(
            text="Questão 03", peso=2, order=5
        )

        self.prova.questoes.set([self.questao1, self.questao2, self.questao3])

    def test_remove_questoes_prova(self):
        payload = {"questao_id": [self.questao3.id]}

        response = self.client.delete(
            f"/provas/{self.prova.id}/remover_questoes",
            json=payload,
            headers=self.get_admin_headers(),
        )

        self.assertEqual(response.status_code, 200)

        count = self.prova.questoes.count()
        self.assertEqual(count, 2)
