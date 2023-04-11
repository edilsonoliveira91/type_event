from django.contrib import admin
from .models import Evento # para colocar a tabela do banco de dados no admin

#CRIA NA TELA ADMIN PARA MANIPULAR OS DADOS 
admin.site.register(Evento)


