from django.utils import timezone

from core import models
from core.tests.tests import BaseTestCase


class ParticipanteListagemProvasTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.prova1 = models.Prova.objects.create(
            title="Prova de Matemática", description="Prova sobre conjuntos"
        )
        self.prova2 = models.Prova.objects.create(
            title="Prova de Biologia", description="Prova sobre evolução"
        )
        self.tentativa_prova1 = models.TentativaProva.objects.create(
            user=self.regular_user,
            prova=self.prova1,
        )
        self.tentativa_prova2 = models.TentativaProva.objects.create(
            user=self.regular_user,
            prova=self.prova2,
            date_completed=timezone.now(),
            nota=10,
        )

    def test_correct_items_and_quantity(self):
        response = self.client.get(
            "/participante/provas", headers=self.get_regular_headers()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 2)
        provas_id = {p["prova"] for p in response.json().get("items")}
        self.assertIn(1, provas_id)
        self.assertIn(2, provas_id)


class ParticipanteCreateTentativaRespostaTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.prova = models.Prova.objects.create(
            title="Prova de Matemática", description="Prova sobre conjuntos"
        )

        self.questao = models.Questao.objects.create(text="Questão 01", peso=3, order=2)

        self.prova.questoes.add(self.questao)

        self.resposta1 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 01", is_correct=True
        )
        self.resposta2 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 02", is_correct=False
        )
        self.resposta3 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 03", is_correct=False
        )

        self.tentativa_prova = models.TentativaProva.objects.create(
            user=self.regular_user,
            prova=self.prova,
        )

    def test_create_tentativa_resposta(self):
        payload = {
            "tentativa_prova_id": self.tentativa_prova.id,
            "questao_id": self.questao.id,
            "resposta_escolhida_id": self.resposta3.id,
        }

        response = self.client.post(
            "/participante/create_resposta",
            json=payload,
            headers=self.get_admin_headers(),
        )

        self.assertEqual(response.status_code, 200)

        tentativa_resposta_id = response.json()["id"]
        resposta_participante = models.RespostaParticipante.objects.get(
            id=tentativa_resposta_id
        )
        self.assertEqual(
            resposta_participante.tentativa_prova.id, payload["tentativa_prova_id"]
        )
        self.assertEqual(resposta_participante.questao.id, payload["questao_id"])
        self.assertEqual(
            resposta_participante.resposta_escolhida.id,
            payload["resposta_escolhida_id"],
        )


class ParticipantePatchTentativaRespostaTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.prova = models.Prova.objects.create(
            title="Prova de Matemática", description="Prova sobre conjuntos"
        )

        self.questao = models.Questao.objects.create(text="Questão 01", peso=3, order=2)

        self.prova.questoes.add(self.questao)

        self.resposta1 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 01", is_correct=True
        )
        self.resposta2 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 02", is_correct=False
        )
        self.resposta3 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 03", is_correct=False
        )

        self.tentativa_prova = models.TentativaProva.objects.create(
            user=self.regular_user,
            prova=self.prova,
        )

        self.resposta_participante = models.RespostaParticipante.objects.create(
            tentativa_prova=self.tentativa_prova,
            questao=self.questao,
            resposta_escolhida=self.resposta1,
        )

    def test_update_tentativa_resposta_success(self):
        payload = {"resposta_escolhida_id": self.resposta3.id}

        response = self.client.patch(
            f"/participante/update_resposta/{self.resposta_participante.id}",
            json=payload,
            headers=self.get_regular_headers(),
        )

        self.assertEqual(response.status_code, 200)
        updated_resposta = models.RespostaParticipante.objects.get(
            id=self.resposta_participante.id
        )
        self.assertEqual(
            updated_resposta.resposta_escolhida.id, payload["resposta_escolhida_id"]
        )
