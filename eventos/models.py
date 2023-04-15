from django.db import models
from django.contrib.auth.models import User #relacionar a tabela de usuarios com o evento para saber quem postou o evento.. chave estrangeira Foreign key 1 para muitos


#CRIA TABELA NO BANCO DE DADOS VIA ORM
class Evento(models.Model):
    criador = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    data_inicio = models.DateField()
    data_termino = models.DateField()
    carga_horaria = models.IntegerField()
    logo = models.ImageField(upload_to="logo")
    participantes = models.ManyToManyField(User, related_name="evento_participante", null=True, blank=True)

    # PALETAS DE CORES
    cor_principal = models.CharField(max_length=7)
    cor_secundaria = models.CharField(max_length=7)
    cor_fundo = models.CharField(max_length=7)

    def __str__(self) -> str:
        return self.nome