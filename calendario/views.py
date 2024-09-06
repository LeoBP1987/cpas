from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from calendario.models import Calendario
from atividades.models import Atividades, Instituicao, TipoAtividade
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
import random
import calendar

def index(request):

    # Envia as informações para montar os calendários por index, por dia, semana ou uma agenda apenas com as atividades

    if not request.user.is_authenticated:
        return redirect('login')
    
    data_param = datetime.today().date()
    mes = gerar_mes(data_param)

    dict_agenda = montar_calendario_agenda()
    dict_dia = montar_calendario_dia(data_param)
    dict_semana = montar_calendario_semana(data_param)


    return render(request, 'calendario/index.html', {'agenda':dict_agenda, 'dia': dict_dia, 'semana': dict_semana, 'data_param': data_param, 'mes': mes})

def configuracoes(request):

    return render(request, 'calendario/configuracoes.html')

def gerar_calendario(request):

    ano_atual = date.today().year

    calendario = Calendario.objects.filter(ano=ano_atual)

    if not calendario.exists():

        data_registro = date.today()

        while data_registro.year == ano_atual:
            for hora in range(0, 25):
                Calendario.objects.create(
                    ano=ano_atual,
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

def apagar():

    Atividades.objects.all().delete()
    Calendario.objects.all().delete()

    return 'Estrutura devidademente deletada'

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

def gerar_atividade(instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso_ativ):

    instituicao = Instituicao.objects.get(id=instituicao)
    tipo = TipoAtividade.objects.get(id=tipo)

    cod_fixo_ativ = instituicao.cod_fixo if fixo_mensal else ''

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
        id_vir=id_vir,
        nao_remunerado=nao_remunerado,
        fixo_mensal_ativ=fixo_mensal,
        cod_fixo_ativ=cod_fixo_ativ,
        seq_personalizada=seq_perso_ativ,
    )

    return atividade

def checar_sequencia(sequencia, seq_perso, data_atividade, data_final, horas):
    confirm = False
    list_confirm = []

    if sequencia == '1':
        while data_atividade <= data_final:
            dia_semana = data_atividade.weekday()
            if dia_semana != 5 and dia_semana !=6:
                for hora in horas:                        
                    if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                        confirm = True
                        list_confirm.append(data_atividade)
                        break
            data_atividade = data_atividade + timedelta(days=1)

    elif sequencia == '2':
        while data_atividade <= data_final:
            for hora in horas:
                if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                    confirm = True
                    list_confirm.append(data_atividade)
                    break              
            data_atividade = data_atividade + timedelta(weeks=1)    

    elif sequencia == '3':
        while data_atividade <= data_final:
            for hora in horas:
                if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                    confirm = True
                    list_confirm.append(data_atividade)
                    break
            data_atividade = data_atividade + timedelta(weeks=2)

    elif sequencia == '4':
        while data_atividade <= data_final:
            for hora in horas:
                if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                    confirm = True
                    list_confirm.append(data_atividade)
                    break
            data_atividade = data_atividade + relativedelta(months=1)

    elif seq_perso:
        lista_personalizada = gerar_lista_personalizada(data_atividade, data_final, seq_perso)

        for data_perso in lista_personalizada:
            data_perso = datetime.strptime(data_perso, '%Y-%m-%d').date()
            for hora in horas:
                if Calendario.objects.filter(dia=data_perso, range=hora, ocupado=True).exists():
                    confirm = True
                    list_confirm.append(data_perso)
                    break

    return {'list_confirm':list_confirm, 'confirm':confirm}

def agendar(instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs, nao_remunerado, fixo_mensal, seq_perso):
    agendado = False

    h_ent = int(entrada)
    h_saida = int(saida)
    data_atividade = datetime.strptime(data, '%Y-%m-%d').date()
    data_final = datetime.strptime(data_final, '%Y-%m-%d').date()
    virada = False
    cod = gerar_cod()

    if h_ent < h_saida:
        horas = range(h_ent, h_saida + 1)
        horasS = None
        verifica_except = checar_sequencia(sequencia, seq_perso, data_atividade, data_final, horas)
        data_except = verifica_except['list_confirm']
    else:
        virada = True
        horas = range(h_ent, 25)
        horasS = range(0, h_saida + 1)
        verifica_except = checar_sequencia(sequencia, seq_perso, data_atividade, data_final, horas)
        except_1 = verifica_except['list_confirm']
        verifica_except = checar_sequencia(sequencia, seq_perso, data_atividade + timedelta(days=1), data_final, horasS)
        except_2 = verifica_except['list_confirm']
        data_except = except_1 + except_2

    if sequencia:        

        if sequencia == '1':
            while data_atividade <= data_final:
                dia_semana = data_atividade.weekday()
                if dia_semana != 5 and dia_semana !=6 and data_atividade not in data_except:

                    if not virada:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                    else:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, 24, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                        atividade = gerar_atividade(instituicao, tipo, data_atividade + timedelta(days=1), 0, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                data_atividade = data_atividade + timedelta(days=1)

        elif sequencia == '2':
            while data_atividade <= data_final:
                if data_atividade not in data_except:
                    if not virada:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                    else:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, 24, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                        atividade = gerar_atividade(instituicao, tipo, data_atividade + timedelta(days=1), 0, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                data_atividade = data_atividade + timedelta(weeks=1)

        elif sequencia == '3':
            while data_atividade <= data_final:
                if data_atividade not in data_except:
                    if not virada:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                    else:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, 24, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                        atividade = gerar_atividade(instituicao, tipo, data_atividade + timedelta(days=1), 0, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                data_atividade = data_atividade + timedelta(weeks=2)

        elif sequencia == '4':
            while data_atividade <= data_final:
                if data_atividade not in data_except:
                    if not virada:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                    else:
                        id_vir = gerar_id_vir()
                        atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, 24, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                        atividade = gerar_atividade(instituicao, tipo, data_atividade + timedelta(days=1), 0, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                        agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
                data_atividade = data_atividade + relativedelta(month=1)

    elif seq_perso:
        lista_personalizada = gerar_lista_personalizada(data_atividade, data_final, seq_perso)

        for data_perso in lista_personalizada:
            data_perso = datetime.strptime(data_perso, '%Y-%m-%d').date()
            if data_perso not in data_except:
                if not virada:
                    id_vir = gerar_id_vir()
                    atividade = gerar_atividade(instituicao, tipo, data_perso, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                    agendado = gerar_agendamento(atividade, data_perso, horas, horasS)
                else:
                    id_vir = gerar_id_vir()
                    atividade = gerar_atividade(instituicao, tipo, data_perso, entrada, 24, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                    agendado = gerar_agendamento(atividade, data_perso, horas, horasS)
                    atividade = gerar_atividade(instituicao, tipo, data_perso + timedelta(days=1), 0, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
                    agendado = gerar_agendamento(atividade, data_perso, horas, horasS)
    else:
        if not virada:
            id_vir = gerar_id_vir()
            atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
            agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
        else:
            id_vir = gerar_id_vir()
            atividade = gerar_atividade(instituicao, tipo, data_atividade, entrada, 24, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
            agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)
            atividade = gerar_atividade(instituicao, tipo, data_atividade + timedelta(days=1), 0, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso)
            agendado = gerar_agendamento(atividade, data_atividade, horas, horasS)

    return agendado

def gerar_lista_personalizada(data_inicio, data_final, ordinal):

    list_meses = [(data_inicio.month, data_inicio.year)]
    lista_personalizada = []
    dia_semana = data_inicio.weekday()

    # Cria um calendário para o mês e ano indicados
    cal = calendar.Calendar()

    while data_inicio <= data_final:
        if data_inicio.month != list_meses[-1][0]:
            list_meses.append((data_inicio.month, data_inicio.year))
        data_inicio = data_inicio + relativedelta(months=1)

    for mes in list_meses:
        lista_dias = [dia for dia in cal.itermonthdays2(mes[1], mes[0]) if dia[0] != 0 and dia[1] == dia_semana]

        for item in ordinal:
            item_int = int(item)     
            if len(lista_dias) > item_int:
                dia_ordinal = lista_dias[item_int][0]
                data = datetime(mes[1], mes[0], dia_ordinal)
                data_format = data.strftime('%Y-%m-%d')
                if data.date() >= datetime.today().date():
                    lista_personalizada.append(data_format)

    return lista_personalizada
    
@require_GET
def disponibilidade(request):

    data = request.GET.get('data')

    if not data:
        return JsonResponse({'disponibilidade':[], 'erro':'Dados insuficientes'})

    horario = Calendario.objects.filter(dia=data)

    HORAS = [(hora.range, f'{hora.range:02d}:00') for hora in horario if not hora.ocupado and hora.range != 24]
    
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
        entrada = entrada + 1 if entrada < 24 else 1
        H_SAIDA.append(entrada)

    for hora in H_SAIDA:
        if (hora > entrada):
            if Calendario.objects.filter(dia=set_data, range=hora, ocupado=False).exists():
                if hora == 24:
                    HORAS.append((hora, '00:00'))
                else:
                    HORAS.append((hora, f'{hora:02d}:00'))
            else:
                break
        elif Calendario.objects.filter(dia=data_saida, range=hora, ocupado=False).exists():
            if hora == 24:
                HORAS.append((hora, '00:00'))
            else:
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
    seq_perso = request.GET.getlist('seq_perso')

    entrada = request.GET.get('entrada')
    saida = request.GET.get('saida')
    h_ent = int(entrada)
    h_saida = int(saida)

    if h_ent < h_saida:
        horas = range(h_ent, h_saida + 1)
        checar = checar_sequencia(sequencia, seq_perso, data_atividade, data_final, horas)
        list_except = checar['list_confirm']
        confirm = checar['confirm']
    else:
        horas = range(h_ent, 25)
        checar = checar_sequencia(sequencia, seq_perso, data_atividade, data_final, horas)
        list_except = checar['list_confirm']
        confirm = checar['confirm']

        horas = range(0, h_saida + 1)
        data_atividade = data_atividade + timedelta(days=1)
        data_final = data_final + timedelta(days=1)
        checar = checar_sequencia(sequencia, seq_perso, data_atividade, data_final, horas)
        list_except = checar['list_confirm']
        confirm = checar['confirm']

    for dia in list_except:
        msg_confirm += f'{dia}, '
    msg_confirm = msg_confirm + ' não poderão ser agendados pois já possuem atividades programadas.'
    
    return JsonResponse({'msg_confirm': msg_confirm, 'confirm': confirm, 'except':list_except})

def montar_calendario_agenda():
    dia_param = datetime.today().date() - timedelta(days=1)
    atividades = Atividades.objects.filter(data__gt=dia_param).order_by('data')
    dict_agenda = {}
    mes_param = 0

    # Montando calendario agenda
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

            if atividade.data.strftime("%Y-%m-%d") not in dict_agenda:
                dict_agenda[atividade.data.strftime("%Y-%m-%d")] = {
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
            
            if atividade.saida < 24:
                periodo = f'{atividade.entrada:02d}:00 - {atividade.saida:02d}:00'
            else:
                periodo = f'{atividade.entrada:02d}:00 - 00:00'
            
            dict_agenda[atividade.data.strftime("%Y-%m-%d")]['lista_dia'].append({
                'id': atividade.id,
                'descricao': descricao,
                'sequencia': sequencia,
                'periodo': periodo
            })
    
    return dict_agenda

def montar_calendario_dia(data):

    data_param = data
    data_calendario = data_param.strftime('%Y-%m-%d')
    dict_dia = {}

    # Montando calendario dia

    dia_semana = gerar_dia_semana(data_param) if data_param else 'None'
    num_dia = f'{data_param.day:02d}' if data_param else 'None'
    mes = gerar_mes(data_param)
    dict_dia[data_param.strftime("%Y-%m-%d")] = {
                'dia_semana': dia_semana,
                'num_dia': num_dia,
                'mes': mes,
                'lista_atividade': []
        }
        
    calendario = Calendario.objects.filter(dia=data_calendario)

    for dia in calendario:
        hora = dia.range
        dia_dia = datetime.strptime(dia.dia, '%Y-%m-%d').date()

        atividade = Atividades.objects.filter(data=dia_dia, entrada=dia.range).first()

        id = atividade.id if atividade else ''

        tipo = f'{atividade.tipo_atividade} - {atividade.instituicao}' if atividade else ''

        if atividade:
            if atividade.saida < 24:
                periodo = f'{atividade.entrada:02d}:00 - {atividade.saida:02d}:00'
            else:
                periodo = f'{atividade.entrada:02d}:00 - 00:00'
        else:
            periodo = ''

        tamanho = f'dia-conteudo__tamanho-{atividade.saida - atividade.entrada}' if atividade else ''

        dict_dia[data_param.strftime("%Y-%m-%d")]['lista_atividade'].append({
            'id' : id,
            'hora': hora,
            'tipo': tipo,
            'periodo': periodo,
            'tamanho': tamanho
        })
        
    return dict_dia

def montar_calendario_semana(data):
    dict_semana = {}
    dict_horas = {}
    
    dict_semana['cabecalho'] = {
        'dia_semana': '',
        'num_dia': '',
    }

    datas_semana = obter_semana(data)

    for dia in datas_semana:
        dia_date = datetime.strptime(dia, '%Y-%m-%d').date()
        dia_semana = gerar_dia_semana(dia)[:1]
        num_dia = f'{dia_date.day:02d}'

        dict_semana[dia] = {
            'dia_semana': dia_semana,
            'num_dia': num_dia,
        }

    for num in range(0, 25):
        if num > 0 and num < 24:
            classe = 'main-tabela__semana__hora'
        else:
            classe = 'main-tabela__semana__hora color_white' 

        dict_horas[num] = {
            'linha': [{
                'hora':num, 
                'class': classe,
                'tipo':'',
                'periodo':'',
                'tamanho':'',
                'id':''
            }],
        }

    for num in range(0, 25):
        for dia in datas_semana:
            dia_date = datetime.strptime(dia, '%Y-%m-%d').date()

            atividade = Atividades.objects.filter(data=dia_date, entrada=num).first()
            tipo = f'{atividade.tipo_atividade} - {atividade.instituicao}' if atividade else ''

            if atividade:
                if atividade.saida < 24:
                    periodo = f'{atividade.entrada:02d}:00 - {atividade.saida:02d}:00'
                else:
                    periodo = f'{atividade.entrada:02d}:00 - 00:00'
            else:
                periodo = ''

            tamanho = f'semana-conteudo__tamanho-{atividade.saida - atividade.entrada}' if atividade else ''
            id = atividade.id if atividade else ''

            dict_horas[num]['linha'].append({
                'hora': '',
                'class':'main-tabela-semana__conteudo' if num != 0 else 'main-tabela-semana__conteudo_zero',
                'tipo': tipo,
                'periodo': periodo,
                'tamanho': tamanho,
                'id': id
            })


    return {'dict_semana': dict_semana, 'dict_horas': dict_horas}

@require_GET
def atualizar_calendario(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.GET.get('data')
        control = request.GET.get('control')
        try:
            if control == '1':
                data_param = datetime.strptime(data, '%Y-%m-%d').date() + timedelta(days=1)
            elif control == '2':
                data_param = datetime.strptime(data, '%Y-%m-%d').date() - timedelta(days=1)
            elif control == '3':
                data_param = datetime.strptime(data, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Data inválida'}, status=400)

        dict_dia = montar_calendario_dia(data_param)
        
        if not dict_dia:
            return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

        try:
            html_content = render_to_string('calendario/partials/base_calendario_dia.html', {'dia': dict_dia, 'data_param': data_param})
        except Exception as e:
            return JsonResponse({'error': f'Erro ao renderizar o template: {str(e)}'}, status=500)

        return JsonResponse({'html': html_content, 'data_param': str(data_param)})
    else:
        return JsonResponse({'error': 'Requisição inválida'}, status=400)

@require_GET
def atualizar_calendario_semana(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.GET.get('data')
        control = request.GET.get('control')
        try:
            if control == '1':
                data_param = datetime.strptime(data, '%Y-%m-%d').date() - timedelta(weeks=1)
            elif control == '2':
                data_param = datetime.strptime(data, '%Y-%m-%d').date() + timedelta(weeks=1)
        except ValueError:
            return JsonResponse({'error': 'Data inválida'}, status=400)

        dict_semana = montar_calendario_semana(data_param)
        mes = gerar_mes(data_param)
        
        if not dict_semana:
            return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

        try:
            html_content = render_to_string('calendario/partials/base_calendario_semana.html', {'semana': dict_semana, 'data_param': data_param, 'mes':mes})
        except Exception as e:
            return JsonResponse({'error': f'Erro ao renderizar o template: {str(e)}'}, status=500)

        return JsonResponse({'html': html_content})
    else:
        return JsonResponse({'error': 'Requisição inválida'}, status=400)


def gerar_dia_semana(data):

    data = datetime.strptime(str(data), '%Y-%m-%d').date()

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

def gerar_mes(data):
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
    }.get(data.month, 'None')

    return mes

def obter_semana(data):
    # Converte a string de data para um objeto datetime
    data = datetime.strptime(str(data), '%Y-%m-%d').date()
    
    # Encontra o domingo da semana da data de referência
    inicio_semana = data - timedelta(days=data.weekday() + 1)  # Ajuste para domingo
    
    # Gera as datas da semana
    datas_semana = [(inicio_semana + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    
    return datas_semana

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