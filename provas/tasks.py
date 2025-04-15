from celery import shared_task
from django.db.models import Case, DecimalField, F, Sum, When

from core.models import Ranking, RegistroRanking, TentativaProva


@shared_task
def corrigir_provas():
    tentativas = TentativaProva.objects.filter(nota=None)
    tentativas_ids = tentativas.values_list("id", flat=True).distinct()

    tentativas = tentativas.annotate(
        resultado_nota=Sum(
            Case(
                When(
                    tentativas_resposta__resposta_escolhida__is_correct=True,
                    then=F("tentativas_resposta__questao__peso"),
                ),
                default=0,
                output_field=DecimalField(),
            )
        )
    )

    for tentativa in tentativas:
        tentativa.nota = tentativa.resultado_nota
        tentativa.save()

    for tentativa_id in tentativas_ids:
        calcular_ranking.delay(tentativa_id)


@shared_task
def calcular_ranking(prova_id):
    tentativas = (
        TentativaProva.objects.filter(prova_id=prova_id, nota__isnull=False)
        .select_related("user")
        .order_by("-nota")
    )

    ranking, created = Ranking.objects.get_or_create(prova_id=prova_id)

    ranking.registroranking_set.all().delete()

    for posicao, tentativa in enumerate(tentativas, start=1):
        RegistroRanking.objects.create(
            ranking=ranking,
            user=tentativa.user,
            prova=tentativa.prova,
            posicao=posicao,
            nota=tentativa.nota,
        )
