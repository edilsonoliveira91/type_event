from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required #faz com que seja obrigado a estar logado para visualizar a pagina
from .models import Evento, Certificado
from django.contrib import messages
from django.contrib.messages import constants
from django.http import Http404
import csv
from secrets import token_urlsafe
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


# VAI SER PERMITIDA APENAS PARA PESSOAS LOGADAS
@login_required
def novo_evento(request):
    if  request.method == "GET":
        return render(request, 'novo_evento.html')
    elif request.method == "POST":
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        data_inicio = request.POST.get('data_inicio')
        data_termino = request.POST.get('data_termino')
        carga_horaria = request.POST.get('carga_horaria')

        cor_principal = request.POST.get('cor_principal')
        cor_secundaria = request.POST.get('cor_secundaria')
        cor_fundo = request.POST.get('cor_fundo')

        logo = request.FILES.get('logo') #usando para capturar arquivos enviado.


        #USADO PARA LINKAR OS DADOS CAPTURADOS PELA VIEWS E INJETAR NOS CAMPOS CORRETO DENTRO DO BANCO DE DADOS.
        evento = Evento(
            criador=request.user,
            nome=nome,
            descricao=descricao,
            data_inicio=data_inicio,
            data_termino=data_termino,
            carga_horaria=carga_horaria,
            logo=logo,
            cor_principal=cor_principal,
            cor_secundaria=cor_secundaria,
            cor_fundo=cor_fundo,
        )

        #PARA SALVAR DE FATO NO BANCO DE DADOS TEMOS QUE FAZER O SEGUINTE.
        evento.save()

        messages.add_message(request, constants.SUCCESS, 'Evento cadastrado com sucesso.')
        return redirect(reverse('novo_evento'))


@login_required
def gerenciar_evento(request):
    if request.method == "GET":
        #VAMOS CAPTURAR DADOS DO MODELS PARA MOSTRAR PRO USUARIO.. QUERY
        eventos = Evento.objects.filter(criador=request.user) # ira filtrar no banco de dados todos os eventos de acordo com o usuario que esta logado, ou seja, so vai mostrar os eventos do usuario logado. Para mostrar no frontend, precisamos usar o render e informar duas coisas: {'nome': nome da varialvel que voce criou para puxar os dados.}
        nome = request.GET.get('nome')
        if nome:
            eventos = eventos.filter(nome__contains=nome)
        return render(request, 'gerenciar_evento.html', {'eventos': eventos})
    

@login_required
def inscrever_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    if request.method == "GET":
        return render(request, 'inscrever_evento.html', {'evento': evento})
    elif request.method == "POST":

        evento.participantes.add(request.user)
        evento.save()


        messages.add_message(request, constants.SUCCESS, 'Inscrição realizada com sucesso!')
        return redirect(f'/eventos/inscrever_evento/{evento.id}')
    

def participantes_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criador == request.user:
        raise Http404('Esse evento não é seu!')
    if request.method == "GET":
        participantes = evento.participantes.all() # isso vai fazer mostrar todos os participantes do evento mas se voce precisa mostrar apenas 3 ou menos ou mais, voce precisa utilizar o [::3] na frente do .all().
        return render(request, 'participantes_evento.html', {'participantes': participantes, 'evento': evento})
    

def gerar_csv(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criador == request.user:
        raise Http404('Esse evento não é seu!')
    participantes = evento.participantes.all() # buscando todos os participantes

    token = f'{token_urlsafe(6)}.csv'
    path = os.path.join(settings.MEDIA_ROOT, token)

    with open(path, 'w') as arq:
        writer = csv.writer(arq, delimiter=",")
        for participante in participantes:
            x = (participante.username, participante.email)
            writer.writerow(x)

    return redirect(f'/media/{token}')


def certificados_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criador == request.user:
        raise Http404('Esse evento não é seu')
    
    if request.method == "GET":
        qtd_certificados = evento.participantes.all().count() - Certificado.objects.filter(evento=evento).count()
        return render(request, 'certificados_evento.html', {'qtd_certificados': qtd_certificados, 'evento': evento})
    

def gerar_certificado(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criador == request.user:
        raise Http404('Esse evento não é seu')
    
    #Executa a concatenação dos arquivos da raiz com o template e fonte.
    path_template = os.path.join(settings.BASE_DIR, 'templates/static/evento/img/template_certificado.png')
    path_fonte = os.path.join(settings.BASE_DIR, 'templates/static/fontes/arimo.ttf')

    #Vai passar por cada participante que precisa gerar um certificado.
    for participante in evento.participantes.all():
        img = Image.open(path_template)
        draw = ImageDraw.Draw(img)

        #Variavel que define o tamanho de fonte para cada escrita.
        fonte_nome = ImageFont.truetype(path_fonte, 80)
        fonte_info = ImageFont.truetype(path_fonte, 30)

        #Faz com que seja escrito em cima da imagem com as possicoes dada em pixels.
        draw.text((230, 651), f"{participante.username}", font=fonte_nome, fill=(0,0,0))
        draw.text((761, 782), f"{evento.nome}", font=fonte_info, fill=(0,0,0))
        draw.text((816, 849), f"{evento.carga_horaria}", font=fonte_info, fill=(0,0,0))

       #Salva a imagem editada na memoria ram que ainda nao foi salva direto no banco de dados.
        output = BytesIO()
        img.save(output, format="png", quality=100)
        #Faz o "ponteiro" voltar para o começo da escrita para que seja lido toda a mensagen.
        output.seek(0)

        #Faz a conversao do arquivo editado no python para que o mesmo entenda o formato do arquivo que sera salvo.
        img_final = InMemoryUploadedFile(output, 'ImageField', f'{token_urlsafe(8)}.png', 'img/jpeg', sys.getsizeof(output), None)

        #passa o paramentro que ira dentro da funcao
        certificado_gerado = Certificado(certificado=img_final, participante=participante, evento=evento)
        #salva de fato no banco de dados o certificado.
        certificado_gerado.save()


    messages.add_message(request, constants.SUCCESS, 'Certificados gerado com sucesso!')
    return redirect(reverse('certificados_evento', kwargs={'id': evento.id}))

def procurar_certificado(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criador == request.user:
        raise Http404('Esse evento não é seu')
    
    email = request.POST.get('email')
    
    certificado = Certificado.objects.filter(evento=evento).filter(participante__email=email).first()

    if not certificado:
        messages.add_message(request, constants.ERROR, 'Esse certificado ainda não foi gerado.')
        return redirect(reverse('certificados_evento', kwargs={'id': evento.id}))
    else:
        return redirect(certificado.certificado.url)
