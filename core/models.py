from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', "Administrador"
        PARTICIPANTE = 'PARTICIPANTE', 'Participante'

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=255,
        choices=Role.choices,
        default=Role.PARTICIPANTE
    )

    def __str__(self):
        return self.name

    def is_admin(self):
        return self.role == self.Role.ADMIN

class AuditedModel(models.Model):
    date_created = models.DateTimeField("Criado em", auto_now_add=True)
    date_changed = models.DateTimeField("Modificado em", auto_now=True)
    active = models.BooleanField(verbose_name="Ativo", default=True)

    class Meta:
        abstract = True


class Prova(AuditedModel):
    title = models.CharField(verbose_name="Título da prova", max_length=255)
    description = models.TextField(verbose_name="Descrição", blank=True)

    def __str__(self):
        return self.title


class Questao(AuditedModel):
    provas = models.ManyToManyField(Prova, related_name="provas")
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text


class Resposta(AuditedModel):
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name="respostas")
    text = models.CharField(max_length=1000)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.questao


class TentativaProva(AuditedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prova = models.ForeignKey(Prova, on_delete=models.CASCADE)
    date_completed = models.DateTimeField(null=True, blank=True)


class RespostaParticipante(AuditedModel):
    tentativa_prova = models.ForeignKey(TentativaProva, on_delete=models.CASCADE, related_name="tentativas_resposta")
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    resposta_escolhida = models.ForeignKey(Resposta, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["tentativa_prova", "questao"]]

    def __str__(self):
        return f"Pergunta: {self.questao} / Resposta: {self.resposta_escolhida}"
