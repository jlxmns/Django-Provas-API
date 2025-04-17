from django.utils import timezone

from core import models
from core.tests.tests import BaseTestCase


class RankingListagemTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.prova = models.Prova.objects.create(
            title="Prova de Matemática", description="Prova sobre conjuntos"
        )

        self.tentativa_prova_regular_user = models.TentativaProva.objects.create(
            user=self.regular_user,
            prova=self.prova,
            date_completed=timezone.now(),
            nota=8,
        )

        self.tentativa_prova_admin_user = models.TentativaProva.objects.create(
            user=self.admin_user,
            prova=self.prova,
            date_completed=timezone.now(),
            nota=10,
        )

        self.ranking = models.Ranking.objects.create(prova=self.prova)

        self.ranking_entry1 = models.RegistroRanking.objects.create(
            ranking=self.ranking,
            user=self.tentativa_prova_admin_user.user,
            tentativa_prova=self.tentativa_prova_admin_user,
            posicao=1,
            nota=self.tentativa_prova_admin_user.nota,
        )

        self.ranking_entry1 = models.RegistroRanking.objects.create(
            ranking=self.ranking,
            user=self.tentativa_prova_regular_user.user,
            tentativa_prova=self.tentativa_prova_regular_user,
            posicao=2,
            nota=self.tentativa_prova_regular_user.nota,
        )

    def test_correct_items_and_quantity(self):
        response = self.client.get(
            f"/ranking/prova/{self.prova.id}", headers=self.get_admin_headers()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 2)
        provas_id = {p["tentativa_prova"] for p in response.json().get("items")}
        self.assertIn(self.tentativa_prova_regular_user.id, provas_id)
        self.assertIn(self.tentativa_prova_admin_user.id, provas_id)
