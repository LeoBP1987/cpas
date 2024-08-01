from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from calendario.models import Calendario
from atividades.models import Atividades, Instituicao, TipoAtividade
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
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
                )
            data_registro = data_registro + timedelta(days=1)

        messages.success(request, f'Calendário para o ano de {ano_atual} gerado com sucesso!')
        return redirect('index')
    else:
        messages.error(request,f'O calendário para o ano de {ano_atual} já foi gerado')
        return redirect('configuracoes')

def apagar(request):

    Atividades.objects.all().delete()
    Calendario.objects.all().delete()

    return redirect('index')

def gerar_agendamento(atividade, data, horas, horasS):
    agendado = False

    for hora in horas:
        calendario = Calendario.objects.filter(dia=data, range=hora).first()
        calendario.ocupado = True
        calendario.atividades.add(atividade)
        calendario.save()
        agendado = True

    if horasS:
        data = data + timedelta(days=1)
        for hora in horasS:
            calendario = Calendario.objects.filter(dia=data, range=hora).first()
            calendario.ocupado = True
            calendario.atividades.add(atividade)
            calendario.save()
            agendado = True


    return agendado

def gerar_atividade_sequencia(instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs, cod):

    instituicao = Instituicao.objects.get(id=instituicao)
    tipo = TipoAtividade.objects.get(id=tipo)

    atividade = Atividades.objects.create(
        instituicao=instituicao,
        tipo_atividade=tipo,
        data=data,
        entrada=entrada,
        saida=saida,
        valor=valor,
        sequencia=sequencia,
        data_final_seq=data_final,
        obs=obs,
        cod=cod
    )

    return atividade

def checar_sequencia(sequencia, data_atividade, data_final, horas):
    confirm = False
    list_confirm = []

    if sequencia == '1':
            while data_atividade < data_final:
                dia_semana = data_atividade.weekday()
                if dia_semana != 5 and dia_semana !=6:
                    for hora in horas:                        
                        if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                            confirm = True
                            list_confirm.append(data_atividade)
                            break
                data_atividade = data_atividade + timedelta(days=1)

    elif sequencia == '2':
            while data_atividade < data_final:
                dia_semana = data_atividade.weekday()
                if dia_semana != 5 and dia_semana !=6:
                    for hora in horas:
                        if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                            confirm = True
                            list_confirm.append(data_atividade)
                            break
                data_atividade = data_atividade + timedelta(weeks=1)    

    elif sequencia == '3':
            while data_atividade < data_final:
                dia_semana = data_atividade.weekday()
                if dia_semana != 5 and dia_semana !=6:
                    for hora in horas:
                        if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                            confirm = True
                            list_confirm.append(data_atividade)
                            break
                data_atividade = data_atividade + relativedelta(months=1)

    return {'list_confirm':list_confirm, 'confirm':confirm}

def agendar(atividade, instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs, cod):
    agendado = False

    h_ent = int(entrada)
    h_saida = int(saida)
    data_atividade = datetime.strptime(data, '%Y-%m-%d').date()
    horasS = None

    if h_ent < h_saida:
        horas = range(h_ent, h_saida + 1)
    else:
        horas = range(h_ent, 24)
        horasS = range(0, h_saida + 1)

    if sequencia:

        data_final = datetime.strptime(data_final, '%Y-%m-%d').date()

        verifica_except = checar_sequencia(sequencia, data_atividade, data_final, horas)
        data_except = verifica_except['list_confirm']        

        if sequencia == '1':
            while data_atividade < data_final:
                dia_semana = data_atividade.weekday()
                if dia_semana != 5 and dia_semana !=6 and data_atividade not in data_except:
                    atividade = gerar_atividade_sequencia(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod) if data_atividade != datetime.strptime(data, '%Y-%m-%d').date() else atividade
                    agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                data_atividade = data_atividade + timedelta(days=1)

        elif sequencia == '2':
            while data_atividade < data_final:
                dia_semana = data_atividade.weekday()
                if data_atividade not in data_except:
                    atividade = gerar_atividade_sequencia(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod) if data_atividade != datetime.strptime(data, '%Y-%m-%d').date() else atividade
                    agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                data_atividade = data_atividade + timedelta(weeks=1)

        elif sequencia == '3':
            while data_atividade < data_final:
                dia_semana = data_atividade.weekday()
                if data_atividade not in data_except:
                    atividade = gerar_atividade_sequencia(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod) if data_atividade != datetime.strptime(data, '%Y-%m-%d').date() else atividade
                    agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                data_atividade = data_atividade + relativedelta(months=1)    
    else:
        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)    

    return agendado

@require_GET
def disponibilidade(request):

    data = request.GET.get('data')

    if not data:
        return JsonResponse({'disponibilidade':[], 'erro':'Dados insuficientes'})

    horario = Calendario.objects.filter(dia=data)

    HORAS = [(hora.range, f'{hora.range:02d}:00') for hora in horario if not hora.ocupado]
    
    return JsonResponse({'disponibilidade': HORAS})

@require_GET
def disponibilidade_saida(request):

    data = request.GET.get('data')
    entrada = request.GET.get('entrada')

    if not entrada or not data:
        return JsonResponse({'disponibilidade':[], 'erro':'Dados insuficientes'})
    
    entrada = int(entrada)
    H_SAIDA = []
    HORAS = []
    data_field = data
    set_data = datetime.strptime(data_field, '%Y-%m-%d').date()
    data_saida = set_data + timedelta(days=1)

    for contador in range(0, 24):
        entrada = entrada + 1 if entrada < 23 else 0
        H_SAIDA.append(entrada)

    for hora in H_SAIDA:
        if (hora > entrada):
            if Calendario.objects.filter(dia=set_data, range=hora, ocupado=False).exists():
                HORAS.append((hora, f'{hora:02d}:00'))
            else:
                break
        elif Calendario.objects.filter(dia=data_saida, range=hora, ocupado=False).exists():
            HORAS.append((hora, f'{hora:02d}:00'))
        else:
            break

    return JsonResponse({'disponibilidade': HORAS})

@require_GET
def validar_sequencia(request):

    confirm = False
    msg_confirm = 'Os dias: '
    list_except = [] 

    data = request.GET.get('data')
    data_atividade = datetime.strptime(data, '%Y-%m-%d').date()
    data_final_seq = request.GET.get('data_final_seq')
    data_final = datetime.strptime(data_final_seq, '%Y-%m-%d').date()

    sequencia = request.GET.get('sequencia')

    entrada = request.GET.get('entrada')
    saida = request.GET.get('saida')
    h_ent = int(entrada)
    h_saida = int(saida)

    if h_ent < h_saida:
        horas = range(h_ent, h_saida + 1)
        checar = checar_sequencia(sequencia, data_atividade, data_final, horas)
        list_except = checar['list_confirm']
        confirm = checar['confirm']
    else:
        horas = range(h_ent, 24)
        checar = checar_sequencia(sequencia, data_atividade, data_final, horas)
        list_except = checar['list_confirm']
        confirm = checar['confirm']

        horas = range(0, h_saida + 1)
        data_atividade = data_atividade + timedelta(days=1)
        data_final = data_final + timedelta(days=1)
        checar = checar_sequencia(sequencia, data_atividade, data_final, horas)
        list_except = checar['list_confirm']
        confirm = checar['confirm']

    for dia in list_except:
        msg_confirm += f'{dia}, '
    msg_confirm = msg_confirm + ' não poderão ser agendados pois já possuem atividades programadas.'
    
    return JsonResponse({'msg_confirm': msg_confirm, 'confirm': confirm, 'except':list_except})