from core import models
from core.tests.tests import BaseTestCase


class RespostaParticipanteListagemTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.prova = models.Prova.objects.create(
            title="Prova de Matemática", description="Prova sobre conjuntos"
        )

        self.questao = models.Questao.objects.create(text="Questão 01", peso=3, order=2)

        self.questao2 = models.Questao.objects.create(
            text="Questão 01", peso=3, order=2
        )

        self.prova.questoes.set([self.questao, self.questao2])

        self.resposta1 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 01", is_correct=True
        )
        self.resposta2 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 02", is_correct=False
        )
        self.resposta3 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 03", is_correct=False
        )

        self.resposta3 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 03", is_correct=True
        )
        self.resposta4 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 04", is_correct=False
        )
        self.resposta5 = models.Resposta.objects.create(
            questao=self.questao, text="Resposta 05", is_correct=False
        )

        self.tentativa_prova = models.TentativaProva.objects.create(
            user=self.regular_user,
            prova=self.prova,
        )

        self.tentativa_prova2 = models.TentativaProva.objects.create(
            user=self.regular_user,
            prova=self.prova,
        )

        self.resposta_participante = models.RespostaParticipante.objects.create(
            tentativa_prova=self.tentativa_prova,
            questao=self.questao,
            resposta_escolhida=self.resposta1,
        )

        self.resposta_participante2 = models.RespostaParticipante.objects.create(
            tentativa_prova=self.tentativa_prova,
            questao=self.questao2,
            resposta_escolhida=self.resposta5,
        )

    def test_correct_items_and_quantity(self):
        response = self.client.get(
            "/resposta_participante/listagem", headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 2)
        questao_id = {p["questao"] for p in response.json().get("items")}
        self.assertIn(self.resposta_participante.id, questao_id)
        self.assertIn(self.resposta_participante2.id, questao_id)


class RespostaParticipanteCreateTestCase(BaseTestCase):
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
            "/resposta_participante/create_resposta",
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


class RespostaParticipantePatchTestCase(BaseTestCase):
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
            f"/resposta_participante/update_resposta/{self.resposta_participante.id}",
            json=payload,
            headers=self.get_admin_headers(),
        )

        self.assertEqual(response.status_code, 200)
        updated_resposta = models.RespostaParticipante.objects.get(
            id=self.resposta_participante.id
        )
        self.assertEqual(
            updated_resposta.resposta_escolhida.id, payload["resposta_escolhida_id"]
        )
