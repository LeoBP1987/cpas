from django.shortcuts import render, redirect
from calendario.models import Calendario
from datetime import date, timedelta
from django.contrib import messages

def configuracoes(request):

    return render(request, 'calendario/configuracoes.html')

def gerar_calendario(request):

    calendario = Calendario.objects.all()

    ano_atual = date.today().year

    if not calendario.exists():

        data_registro = date.today()

        while data_registro.year == ano_atual:
            for hora in range(0, 24):
                Calendario.objects.create(
                    dia=data_registro,
                    range=hora,
                    ocupado=False,
                    descricao=' ',
                )
            data_registro = data_registro + timedelta(days=1)

        messages.success(request, f'Calendário para o ano de {ano_atual} gerado com sucesso!')
        return redirect('index')
    else:
        messages.error(request,f'O calendário para o ano de {ano_atual} já foi gerado')
        return redirect('configuracoes')

def apagar(request):

    Calendario.objects.all().delete()

    return redirect('index')
