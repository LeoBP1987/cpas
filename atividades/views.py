from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages, auth
from django.views.decorators.http import require_GET
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from atividades.forms import TipoAtividadeForms, InstituicaoForms, AtividadesForms
from atividades.models import TipoAtividade, Instituicao, Atividades
from calendario.models import Calendario
from calendario.views import agendar, checar_sequencia, gerar_dia_semana
import json
import random


def index(request):

    if not request.user.is_authenticated:
        return redirect('login')
    
    dict_atividade = {}

    dia_atual = datetime.today().date() - timedelta(days=1)

    atividades = Atividades.objects.filter(data__gt=dia_atual).order_by('data')

    for atividade in atividades:
        periodo = f'{atividade.entrada:02d}:00 às {atividade.saida:02d}:00'
        descricao = atividade.tipo_atividade.nome_tipo
        
        if atividade.sequencia :
            data_final = f'{atividade.data_final_seq.day:02d}/{atividade.data_final_seq.month:02d}/{atividade.data_final_seq.year:04d}'
            if atividade.sequencia == '1':
                descricao = f'{atividade.tipo_atividade.nome_tipo} diariamente até o dia {data_final}'
            elif atividade.sequencia == '2':
                descricao = f'{atividade.tipo_atividade.nome_tipo} semanalmente até o dia {data_final}'
            elif atividade.sequencia == '3':
                descricao = f'{atividade.tipo_atividade.nome_tipo} mensalmente até o dia {data_final}'

        dia_semana = gerar_dia_semana(atividade.data)
        
        if atividade.entrada < atividade.saida:
            qt_horas = atividade.saida - atividade.entrada
        else:
            qt_horas = (24 - atividade.entrada) + atividade.saida
        
        dict_atividade[f'{atividade.instituicao.nome_inst} - {atividade.data}'] = {
            'id': atividade.id,
            'periodo': periodo,
            'dia_semana': dia_semana,
            'imagem_url': atividade.instituicao.imagem.url if atividade.instituicao.imagem else None,
            'data': f'{atividade.data.day:02d}/{atividade.data.month:02d}/{atividade.data.year:04d}',
            'inst': atividade.instituicao.nome_inst,
            'descricao': descricao,
            'qt_horas': f'{qt_horas}hrs',
            'obs': atividade.obs
        }
    
    list_atividades = list(dict_atividade.values())

    return render(request, 'atividades/index.html', {'atividades': list_atividades})

def novo_tipo(request):

    forms = TipoAtividadeForms()

    if request.method == 'POST':

        forms = TipoAtividadeForms(request.POST)

        if forms.is_valid():
            novo_tipo = forms
            forms.save()
            messages.success(request,'Novo Tipo de Atividade Cadastrado com Sucesso!')
            return redirect('tipos')
        else:
            messages.error(request,'Erro ao realizar o cadastro. Favor, verifique as informações e tente novamente.')
            return redirect('tipos')

    return render(request, 'atividades/novo_tipo.html', {'forms':forms})

def editar_tipo(request, tipo_id):

    tipo = TipoAtividade.objects.get(id=tipo_id)
    
    forms = TipoAtividadeForms(instance=tipo)

    if request.method == 'POST':

        forms = TipoAtividadeForms(request.POST, instance=tipo)

        if forms.is_valid():
            forms.save()
            messages.success(request,'Alterações realizadas com sucesso!')
            return redirect('tipos')
        else:
            messages.error(request, 'Não foi possível realizar a edição. Favor revise os dados ou entre em contato com o administrador do sistema.')

    return render(request, 'atividades/editar_tipo.html', {'forms':forms, 'tipo':tipo})

def deletar_tipo(request, tipo_id):

    tipo = TipoAtividade.objects.get(id=tipo_id)

    tipo.delete()

    messages.success(request, 'Deleção realizada com sucesso!')
    return redirect('tipos')

def instituicoes(request):
    
    instituicoes = Instituicao.objects.all()

    return render(request, 'atividades/instituicoes.html', {'instituicoes':instituicoes})

def editar_instituicao(request, id_inst):

    inst = Instituicao.objects.get(id=id_inst)
    forms = InstituicaoForms(instance=inst)

    if request.method == 'POST':

        forms = InstituicaoForms(request.POST, instance=inst)

        if forms.is_valid():
            forms.save()
            messages.success(request, 'Edição realizada com sucesso')
            return redirect('instituicoes')
        else:
            messages.error(request, 'Não foi possível realizar a edição. Favor revise os dados ou entre em contato com o administrador do sistema.')

    return render(request, 'atividades/editar_instituicao.html', {'forms':forms, 'inst':inst})

def deletar_instituicao(request, id_inst):

    inst = Instituicao.objects.get(id=id_inst)

    inst.delete() 

    messages.success(request, 'Deleção realizada com sucesso!')
    return redirect('instituicoes')


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

def nova_atividade(request):

    if request.method == 'POST':

        forms = AtividadesForms(request.POST)

        if forms.is_valid():

            instituicao = forms['instituicao'].value()
            tipo = forms['tipo_atividade'].value()       
            data = forms['data'].value()
            entrada = forms['entrada'].value()
            saida = forms['saida'].value()
            valor = forms['valor'].value()
            sequencia = forms['sequencia'].value()
            data_final = forms['data_final_seq'].value()
            obs = forms['obs'].value()

            if not data_final:
                data_final = data

            agendamento = agendar(instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs)

            if agendamento:
                messages.success(request,'Agendamento realizado com Sucesso!')
                return redirect('index')
            else:
                messages.error(request,'A atividade foi criada mas ocorreu um problema na hora do agendamento. Favor, entrar em contato com o administrador do sistema.')
        else:
            mensagem = f'{forms.errors}'
            messages.error(request,mensagem)
    else:
        forms = AtividadesForms()


    return render(request, 'atividades/nova_atividade.html', {'forms':forms})

def editar_atividade(request, id_atividade):

    atividade = get_object_or_404(Atividades, id=id_atividade)
    forms = AtividadesForms(instance=atividade)

    if request.method == 'POST':

        forms = AtividadesForms(request.POST, instance=atividade)

        if forms.is_valid():

            param = forms['extra_param'].value()

            if param == '1':
                atividades = Atividades.objects.filter(id_vir=atividade.id_vir)

                inst = forms['instituicao'].value()
                instituicao = get_object_or_404(Instituicao, id=inst)
                tipo = forms['tipo_atividade'].value()
                tipo_atividade = get_object_or_404(TipoAtividade, id=tipo)

                for ativividade_seq in atividades:
                    ativividade_seq.instituicao = instituicao
                    ativividade_seq.tipo_atividade = tipo_atividade
                    ativividade_seq.valor = forms['valor'].value()
                    ativividade_seq.obs = forms['obs'].value()
                    ativividade_seq.save()

                forms.save()
                messages.success(request, 'Atividade editada com sucesso')
                return redirect('index')
            elif param == '2':
                atividades = Atividades.objects.filter(cod=atividade.cod)

                inst = forms['instituicao'].value()
                instituicao = get_object_or_404(Instituicao, id=inst)
                tipo = forms['tipo_atividade'].value()
                tipo_atividade = get_object_or_404(TipoAtividade, id=tipo)

                for ativividade_seq in atividades:
                    ativividade_seq.instituicao = instituicao
                    ativividade_seq.tipo_atividade = tipo_atividade
                    ativividade_seq.valor = forms['valor'].value()
                    ativividade_seq.obs = forms['obs'].value()
                    ativividade_seq.save()

                forms.save()
                messages.success(request, 'Sequência editada com sucesso')
                return redirect('index')
        else:
            messages.error(request, f'{forms.errors}')

    return render(request, 'atividades/editar_atividade.html', {'forms':forms, 'atividade':atividade})


def deletar_atividade(request, id_atividade):

    atividade_param = Atividades.objects.get(id=id_atividade)
    id_vir = atividade_param.id_vir
    atividade = Atividades.objects.filter(id_vir=id_vir)
    
    if atividade:

        for item in atividade:
            agenda = Calendario.objects.filter(atividades=item)
            
            for hora in agenda:
                hora.ocupado = False
                hora.save()
            item.delete()
        messages.success(request, 'Atividade deletada com Sucesso')
        return redirect('index')
    else:
        messages.error(request, 'Ocorreu um erro deleção não pode ser realizada!')
        return redirect('index')


def deletar_sequencia(request, id_atividade):

    atividade = Atividades.objects.get(id=id_atividade)
    cod = atividade.cod
    
    atividades = Atividades.objects.filter(cod=cod)

    if atividades:
        for atividade in atividades:
            agenda = Calendario.objects.filter(atividades=atividade)

            if agenda:
                for hora in agenda:
                    hora.ocupado = False
                    hora.save()
                atividade.delete()
        messages.success(request, 'Atividade deletada com Sucesso')
        return redirect('index')
                
    else:
        messages.error(request, 'Ocorreu um erro deleção não pode ser realizada!')
        return redirect('index')


def tipos(request):

    tipos = TipoAtividade.objects.all()

    return render(request, 'atividades/tipos.html', {'tipos':tipos})

def get_valor_padrao(request, instituicao_id):
    try:

        instituicao = Instituicao.objects.get(id=instituicao_id)
        valor_padrao = instituicao.valor_padrao
        return JsonResponse({'valor_padrao': valor_padrao})
    
    except Instituicao.DoesNotExist:

        return JsonResponse({'valor_padrao': ''}, status=404)
    
