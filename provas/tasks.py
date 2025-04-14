from celery import shared_task
from django.db.models import Case, DecimalField, F, Sum, When

from core.models import TentativaProva


@shared_task
def corrigir_provas():
    tentativas = TentativaProva.objects.filter(nota=None).annotate(
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
