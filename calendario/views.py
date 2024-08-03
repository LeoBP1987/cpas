from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from calendario.models import Calendario
from atividades.models import Atividades, Instituicao, TipoAtividade
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
import random

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

def gerar_atividade(instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir):

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
        cod=cod,
        id_vir=id_vir
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

def agendar(instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs):
    agendado = False

    h_ent = int(entrada)
    h_saida = int(saida)
    data_atividade = datetime.strptime(data, '%Y-%m-%d').date()
    horasS = None
    virada = False
    cod = gerar_cod()

    if h_ent < h_saida:
        horas = range(h_ent, h_saida + 1)
    else:
        virada = True
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

                    if not virada:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                    else:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, 23, valor, sequencia, data_final, obs, cod, id_vir)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                        atividade = gerar_atividade(instituicao, tipo, data_atividade + timedelta(days=1), 0, saida, valor, sequencia, data_final, obs, cod, id_vir)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                data_atividade = data_atividade + timedelta(days=1)

        elif sequencia == '2':
            while data_atividade < data_final:
                dia_semana = data_atividade.weekday()
                if data_atividade not in data_except:

                    if not virada:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                    else:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, 23, valor, sequencia, data_final, obs, cod, id_vir)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                        atividade = gerar_atividade(instituicao, tipo, data_atividade + timedelta(days=1), 0, saida, valor, sequencia, data_final, obs, cod, id_vir)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                data_atividade = data_atividade + timedelta(weeks=1)

        elif sequencia == '3':
            while data_atividade < data_final:
                dia_semana = data_atividade.weekday()
                if data_atividade not in data_except:
                    if not virada:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                    else:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, 23, valor, sequencia, data_final, obs, cod, id_vir)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                        atividade = gerar_atividade(instituicao, tipo, data_atividade + timedelta(days=1), 0, saida, valor, sequencia, data_final, obs, cod, id_vir)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                data_atividade = data_atividade + relativedelta(months=1)    
    else:
        if not virada:
            id_vir = gerar_id_vir()
            atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir)
            agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
        else:
            id_vir = gerar_id_vir()
            atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, 23, valor, sequencia, data_final, obs, cod, id_vir)
            agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
            atividade = gerar_atividade(instituicao, tipo, data_atividade + timedelta(days=1), 0, saida, valor, sequencia, data_final, obs, cod, id_vir)
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

def exibir_calendario(request):
    dia_param = datetime.today().date() - timedelta(days=1)
    atividades = Atividades.objects.filter(data__gt=dia_param).order_by('data')
    dict_atividade = {}
    mes_param = 0
    
    if atividades:
        for atividade in atividades:
            dia_semana = gerar_dia_semana(atividade.data)
            sigla_dia = dia_semana[:3]
            num_dia = atividade.data.day

            if atividade.data.month != mes_param:
                mes = { 
                    1: 'Janeiro',
                    2: 'Fevereiro',
                    3: 'Março',
                    4: 'Abril',
                    5: 'Maio',
                    6: 'Junho',
                    7: 'Julho',
                    8: 'Agosto',
                    9: 'Setembro',
                    10: 'Outubro',
                    11: 'Novembro',
                    12: 'Dezembro'
                }.get(atividade.data.month, '')
            else:
                mes = None

            mes_param = atividade.data.month

            if atividade.data.strftime("%Y-%m-%d") not in dict_atividade:
                dict_atividade[atividade.data.strftime("%Y-%m-%d")] = {
                    'sigla_dia': sigla_dia,
                    'num_dia': num_dia,
                    'mes': mes,
                    'lista_dia': []
                }
            
            descricao = f'{atividade.tipo_atividade} - {atividade.instituicao.nome_inst}'
            sequencia = {
                '1': 'Diaria',
                '2': 'Semanal',
                '3': 'Mensal'
            }.get(atividade.sequencia, 'Único')
            
            periodo = f'{atividade.entrada:02d}:00 - {atividade.saida:02d}:00'
            
            dict_atividade[atividade.data.strftime("%Y-%m-%d")]['lista_dia'].append({
                'id': atividade.id,
                'descricao': descricao,
                'sequencia': sequencia,
                'periodo': periodo
            })
    
    return render(request, 'calendario/calendario.html', {'agenda': dict_atividade})


def gerar_dia_semana(data):

    if data.weekday() == 0:
        dia_semana = 'Segunda-Feira'
    elif data.weekday() == 1:
        dia_semana = 'Terça-Feira'
    elif data.weekday() == 2:
        dia_semana = 'Quarta-Feira'
    elif data.weekday() == 3:
        dia_semana = 'Quinta-Feira'
    elif data.weekday() == 4:
        dia_semana = 'Sexta-Feira'
    elif data.weekday() == 5:
        dia_semana = 'Sabádo'
    elif data.weekday() == 6:
        dia_semana = 'Domingo'

    return dia_semana

def gerar_cod():

    atividades = Atividades.objects.all()
    lista_codigos = []
    gerado = False

    for atividade in atividades:

        if atividade.cod not in lista_codigos:
            lista_codigos.append(atividade.cod)

    while not gerado:
        cod_int = random.randint(0, 9999)
        if cod_int not in lista_codigos:
            cod = f'{cod_int:02d}'
            gerado = True

    return cod

def gerar_id_vir():

    atividades = Atividades.objects.all()
    lista_codigos = []
    gerado = False

    for atividade in atividades:

        if atividade.id_vir not in lista_codigos:
            lista_codigos.append(atividade.id_vir)

    while not gerado:
        id_int = random.randint(0, 9999)
        if id_int not in lista_codigos:
            id_vir = f'{id_int:02d}'
            gerado = True

    return id_vir