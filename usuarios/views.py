from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.messages import constants
from django.urls import reverse


def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # VALIDAÇÃO SE A SENHAS SÃO IGUAIS
        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não são iguais.')
            return redirect(reverse('cadastro'))
        
        # VAI FILTRAR NO BANCO DE DADOS SE O EMAIL JÁ EXISTE
        user = User.objects.filter(email=email)
        if user.exists():
            messages.add_message(request, constants.ERROR, 'Email já cadastrado.')
            return redirect(reverse('cadastro'))
        

         # IRA CRIAR UM NOVO USUARIO NO BANCO DE DADOS
        user = User.objects.create_user(username=username, email=email, password=senha)
        messages.add_message(request, constants.SUCCESS, 'Usuario cadastrado com sucesso!.')
        return render(reverse('login'))


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        #AUTENTICAÇÃO SE O USUARIO EXISTE
        user = auth.authenticate(username=username, password=senha)

        #SE O USUARIO NAO EXISTIR
        if not user:
            messages.add_message(request, constants.ERROR, 'Username ou senha inválidos')
            return redirect(reverse('login'))
        
        #SE O USUARIO EXISTE ELE IRA LOGAR
        auth.login(request, user)
        return redirect('/eventos/novo_evento/')