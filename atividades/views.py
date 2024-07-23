from django.shortcuts import render, redirect
from atividades.forms import TipoAtividadeForms, InstituicaoForms
from django.contrib import messages

def index(request):

    return render(request, 'atividades/index.html')

def novo_tipo(request):

    forms = TipoAtividadeForms()

    if request.method == 'POST':

        forms = TipoAtividadeForms(request.POST)

        if forms.is_valid():
            novo_tipo = forms
            forms.save()
            messages.success(request,'Novo Tipo de Atividade Cadastrado com Sucesso!')
            return redirect('index')
        else:
            messages.error(request,'Erro ao realizar o cadastro. Favor, verifique as informações e tente novamente.')
            return redirect('index')

    return render(request, 'atividades/novo_tipo.html', {'forms':forms})

def nova_instituicao(request):
    
    if request.method == 'POST':

        forms = InstituicaoForms(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            messages.success(request,'Nova Instituição Cadastrada com Sucesso!')
            return redirect('index')
        else:
            messages.error(request,'Erro ao realizar o cadastro. Favor, verifique as informações e tente novamente.')
    else:
        forms = InstituicaoForms()

    return render(request, 'atividades/nova_instituicao.html', {'forms':forms})