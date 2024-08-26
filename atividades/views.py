from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.contrib import messages, auth
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from atividades.forms import TipoAtividadeForms, InstituicaoForms, AtividadesForms
from atividades.models import TipoAtividade, Instituicao, Atividades
from calendario.models import Calendario
from calendario.views import agendar, checar_sequencia, gerar_dia_semana, gerar_mes
import json
import random
import calendar


def index(request):

    if not request.user.is_authenticated:
        return redirect('login')
    
    dict_atividade = {}

    dia_atual = datetime.today().date() - timedelta(days=1)

    atividades = Atividades.objects.filter(data__gt=dia_atual).order_by('data')

    for atividade in atividades:
        descricao = atividade.tipo_atividade.nome_tipo
        if atividade.saida < 24:
            periodo = f'{atividade.entrada:02d}:00 às {atividade.saida:02d}:00'
        else:
            periodo = f'{atividade.entrada:02d}:00 às 00:00'
        
        if atividade.sequencia :
            data_final = f'{atividade.data_final_seq.day:02d}/{atividade.data_final_seq.month:02d}/{atividade.data_final_seq.year:04d}'
            if atividade.sequencia == '1':
                descricao = f'{atividade.tipo_atividade.nome_tipo} diariamente até o dia {data_final}'
            elif atividade.sequencia == '2':
                descricao = f'{atividade.tipo_atividade.nome_tipo} semanalmente até o dia {data_final}'
            elif atividade.sequencia == '3':
                descricao = f'{atividade.tipo_atividade.nome_tipo} quinzenalmente até o dia {data_final}'
            elif atividade.sequencia == '4':
                descricao = f'{atividade.tipo_atividade.nome_tipo} mensalmente até o dia {data_final}'
        elif atividade.seq_personalizada :
            dia_semana = atividade.data.weekday()
            descr_seq_perso = descrever_seq_perso(atividade.seq_personalizada, dia_semana)
            data_final = f'{atividade.data_final_seq.day:02d}/{atividade.data_final_seq.month:02d}/{atividade.data_final_seq.year:04d}'
            descricao = f'{atividade.tipo_atividade.nome_tipo} repetido toda {descr_seq_perso} do mês até o dia {data_final}'


        dia_semana = gerar_dia_semana(atividade.data)

        if len(atividade.obs) > 69:
            obs = f'{atividade.obs[:69]}...'
        else:
            obs = atividade.obs
        
        dict_atividade[f'{atividade.id_vir} - {atividade.data}'] = { 
            'id': atividade.id,
            'periodo': periodo,
            'dia_semana': dia_semana,
            'imagem_url': atividade.instituicao.imagem.url if atividade.instituicao.imagem else None,
            'data': f'{atividade.data.day:02d}/{atividade.data.month:02d}/{atividade.data.year:04d}',
            'inst': atividade.instituicao.nome_curto if atividade.instituicao.nome_curto else atividade.instituicao.nome_inst,
            'descricao': descricao,
            'obs': obs
        }
    
    list_atividades = list(dict_atividade.values())

    return render(request, 'atividades/index.html', {'atividades': list_atividades})

def descrever_seq_perso(seq_perso, dia_semana):
    # Dicionário para mapear índices às descrições ordinais
    ordinais = {
        '0': '1ª',
        '1': '2ª',
        '2': '3ª',
        '3': '4ª',
        '4': '5ª'
    }

    dias_semana = {
        0: 'segunda-feira',
        1: 'terça-feira',
        2: 'quarta-feira',
        3: 'quinta-feira',
        4: 'sexta-feira',
        5: 'sábado',
        6: 'domingo'
    }

    dia = dias_semana.get(dia_semana, None)
    
    # Lista para armazenar as descrições ordinais
    descricao_lista = []
    
    for item in seq_perso:
        # Obtém o ordinal correspondente ou 'None' se o índice for inválido
        ordinal = ordinais.get(item, None)
        if ordinal:
            descricao_lista.append(ordinal)
    
    # Formatação final da string
    if len(descricao_lista) > 1:
        descricao_seq_perso = ', '.join(descricao_lista[:-1]) + f' e {descricao_lista[-1]} {dia}'
    else:
        descricao_seq_perso = f'{descricao_lista[0]} {dia}' if descricao_lista else ''
    
    return descricao_seq_perso

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
            instituicao = forms.save(commit=False)
            instituicao.cod_fixo = gerar_cod_fixo()
            instituicao.save()
            messages.success(request,'Nova Instituição Cadastrada com Sucesso!')
            return redirect('index')
        else:
            messages.error(request,'Erro ao realizar o cadastro. Favor, verifique as informações e tente novamente.')
    else:
        forms = InstituicaoForms()

    return render(request, 'atividades/nova_instituicao.html', {'forms':forms})

def gerar_cod_fixo():

    instituicoes = Instituicao.objects.all()
    lista_codigos = []
    gerado = False

    for instituicao in instituicoes:
        lista_codigos.append(instituicao.fixo_mensal_inst)

    while not gerado:
        id_int = random.randint(0, 9999)
        if id_int not in lista_codigos:
            cod_fixo = f'{id_int:02d}'
            gerado = True

    return cod_fixo

def instituicao(request, id_instituicao):

    instituicao = Instituicao.objects.get(id=id_instituicao)

    dict_inst = {}

    valor = instituicao.valor_fixo
    valor = f'R$ {valor}'
    
    dict_inst['instituicao.id'] = {
        'id': instituicao.id,
        'nome_curto': instituicao.nome_curto if instituicao.nome_curto else '',
        'nome_inst': instituicao.nome_inst,
        'imagem': instituicao.imagem.url if instituicao.imagem else '',
        'fixo_mensal': 'SIM' if instituicao.fixo_mensal_inst else 'NÃO',
        'valor_fixo': valor if instituicao.valor_fixo else '',
        'endereco': instituicao.endereco,
        'telefone': instituicao.telefone,
        'contato': instituicao.contato
    }
    

    return render(request, 'atividades/instituicao.html', {'instituicoes':dict_inst})

def atividade(request, id_atividade):

    hoje = datetime.today().date()

    dict_atividade = {}

    atividade = Atividades.objects.get(id=id_atividade)

    if atividade.sequencia:
        if atividade.sequencia == '1':
            sequencia = 'Diário'
        elif atividade.sequencia == '2':
            sequencia = 'Semanal'
        elif atividade.sequencia == '3':
            sequencia = 'Quinzenal'
        elif atividade.sequencia == '4':
            sequencia = 'Mensal'
    else:
        sequencia = ''

    if atividade.nao_remunerado:
        valor = 'Não Remunerado'
    else:
        valor = f'R$ {atividade.valor}'

    dict_atividade['atividade.id'] = {
        'id': atividade.id,
        'instituicao': atividade.instituicao,
        'tipo_atividade': atividade.tipo_atividade,
        'data': atividade.data,
        'entrada': f'{atividade.entrada:02d}:00',
        'saida': f'{atividade.saida:02d}:00' if atividade.saida != 24 else f'00:00',
        'valor': valor,
        'sequencia': sequencia,
        'data_final_seq': atividade.data_final_seq,
        'obs': atividade.obs
    }    

    return render(request, 'atividades/atividade.html', {'atividades':dict_atividade, 'hoje':hoje})

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
            valor = str(valor).replace('R$ ', '').replace(',', '').strip()
            sequencia = forms['sequencia'].value()
            data_final = forms['data_final_seq'].value()
            obs = forms['obs'].value()
            nao_remunerado = forms['nao_remunerado'].value()
            fixo_mensal = forms['fixo_mensal_ativ'].value()
            seq_perso = forms['seq_perso'].value()

            if not data_final:
                data_final = data

            agendamento = agendar(instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs, nao_remunerado, fixo_mensal, seq_perso)

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

    data_atual = datetime.today().date()
    atividade = get_object_or_404(Atividades, id=id_atividade)
    forms = AtividadesForms(instance=atividade)

    if request.method == 'POST':

        forms = AtividadesForms(request.POST, instance=atividade)

        if forms.is_valid():

            param = forms['extra_param'].value()
            valor = forms['valor'].value()
            valor = str(valor).replace('R$ ', '').replace(',', '').strip()
            nao_remunerado = forms['nao_remunerado'].value()

            if param == '1':
                atividades = Atividades.objects.filter(id_vir=atividade.id_vir)

                inst = forms['instituicao'].value()
                instituicao = get_object_or_404(Instituicao, id=inst)
                tipo = forms['tipo_atividade'].value()
                tipo_atividade = get_object_or_404(TipoAtividade, id=tipo)                

                for ativividade_seq in atividades:
                    ativividade_seq.instituicao = instituicao
                    ativividade_seq.tipo_atividade = tipo_atividade
                    ativividade_seq.valor = valor
                    ativividade_seq.nao_remunerado = nao_remunerado
                    ativividade_seq.obs = forms['obs'].value()
                    ativividade_seq.save()

                messages.success(request, 'Atividade editada com sucesso')
                return redirect('index')
            elif param == '2':
                atividades = Atividades.objects.filter(cod=atividade.cod, data__lt=data_atual)

                inst = forms['instituicao'].value()
                instituicao = get_object_or_404(Instituicao, id=inst)
                tipo = forms['tipo_atividade'].value()
                tipo_atividade = get_object_or_404(TipoAtividade, id=tipo)
                
                for ativividade_seq in atividades:
                    ativividade_seq.instituicao = instituicao
                    ativividade_seq.tipo_atividade = tipo_atividade
                    ativividade_seq.nao_remunerado = nao_remunerado
                    ativividade_seq.valor = valor
                    ativividade_seq.obs = forms['obs'].value()
                    ativividade_seq.save()

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

    data_atual = datetime.today().date()

    atividade = Atividades.objects.filter(id=id_atividade, data__lt=data_atual)
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

def get_valor_fixo(request, instituicao_id):
    try:

        instituicao = Instituicao.objects.get(id=instituicao_id)
        valor_fixo = instituicao.valor_fixo
        return JsonResponse({'valor_fixo': valor_fixo})
    
    except Instituicao.DoesNotExist:

        return JsonResponse({'valor_padrao': ''}, status=404)
    
def filtrar_financeiro(atividades):

    data_inicio = atividades.order_by('data').first()
    data_inicio = data_inicio.data
    data_final = atividades.order_by('data').last()
    data_final = data_final.data

    qt_meses = (data_final.month + 1) - data_inicio.month

    dict_financ = {}
    total = 0
    total_fixo = 0
    total_variavel = 0
    qt_atividade = 0
    qt_hora = 0
    list_dia_trab = []
    list_mes = []
    list_id_vir = []
    list_fixo = []

    dict_inst = gerar_grafico_instituicao(atividades, qt_meses)
    lista_etiqueta = list(dict_inst.keys())
    lista_valores = list(dict_inst.values())

    if atividades:

        for atividade in atividades:

            if atividade.fixo_mensal_ativ:
                if atividade.id_vir not in list_id_vir:
                    list_id_vir.append(atividade.id_vir)
                
                if atividade.cod_fixo_ativ not in list_fixo:
                    total_fixo += float(atividade.valor)
                    list_fixo.append(atividade.cod_fixo_ativ)
            else:
                if atividade.id_vir not in list_id_vir:
                    total_variavel += float(atividade.valor)
                    list_id_vir.append(atividade.id_vir)

            # Calculando a quantidade de horas
            if atividade.entrada < atividade.saida:
                qt_hora += (atividade.saida - atividade.entrada)
            else:
                qt_hora += ((24 - atividade.entrada) + atividade.saida)

            # Adiciona a data à lista de dias trabalhados se não estiver presente
            if atividade.data not in list_dia_trab:
                list_dia_trab.append(atividade.data)

            # Adiciona o mês à lista de meses se não estiver presente
            if atividade.data.month not in list_mes:
                list_mes.append(atividade.data.month)
        
        qt_atividade = len(list_id_vir)

        total_fixo = total_fixo * qt_meses
        total = total_fixo + total_variavel

        # Preparando os dados para o dicionário de finanças
        dict_financ['financeiro'] = {
            'total': f'R$ {"{:,.2f}".format(total).replace(",", "X").replace(".", ",").replace("X", ".")}',
            'media_atividade': f'R$ {"{:,.2f}".format(total / qt_atividade if qt_atividade else 0).replace(",", "X").replace(".", ",").replace("X", ".")}',
            'media_hora': f'R$ {"{:,.2f}".format(total / qt_hora if qt_hora else 0).replace(",", "X").replace(".", ",").replace("X", ".")}',
            'media_dia_trab': f'R$ {"{:,.2f}".format(total / len(list_dia_trab) if list_dia_trab else 0).replace(",", "X").replace(".", ",").replace("X", ".")}',
            'media_mes': f'R$ {"{:,.2f}".format(total / len(list_mes) if list_mes else 0).replace(",", "X").replace(".", ",").replace("X", ".")}'
        }
    else:
        dict_financ['financeiro'] = {
            'total': 'R$ 0,00',
            'media_atividade': 'R$ 0,00',
            'media_hora': 'R$ 0,00',
            'media_dia_trab': 'R$ 0,00',
            'media_mes': 'R$ 0,00'
        }

    return {'dict_financ': dict_financ, 'etiquetas': lista_etiqueta, 'valores': lista_valores}


def filtrar_mes(mes):

    atividades = Atividades.objects.filter(data__month=mes, nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_ano(ano):

    atividades = Atividades.objects.filter(data__year=ano, nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_ate_fim_mes():

    data_inicio = datetime.today().date()
    ano = data_inicio.year
    mes = data_inicio.month
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_final = datetime(ano, mes, ultimo_dia).date()

    atividades = Atividades.objects.filter(data__range=(data_inicio, data_final), nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_ate_fim_ano():

    data_inicio = datetime.today().date()
    ano = data_inicio.year
    data_final = datetime(ano, 12, 31).date()    

    atividades = Atividades.objects.filter(data__range=(data_inicio, data_final), nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_todo_periodo():

    atividades = Atividades.objects.filter(nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_personalizado(dataInicio, dataFinal):

    atividades = Atividades.objects.filter(data__range=(dataInicio, dataFinal), nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def gerar_grafico_instituicao(atividades, qt_meses):
    dict_inst = {}
    list_cod_fixo = []
    list_id_vir = []
    
    
    for atividade in atividades:
        nome_inst = atividade.instituicao.nome_inst

        if atividade.id_vir not in list_id_vir:
            list_id_vir.append(atividade.id_vir)

            # Inicializa o total se a instituição ainda não estiver no dicionário
            if nome_inst not in dict_inst:
                dict_inst[nome_inst] = 0

            if atividade.fixo_mensal_ativ:
                if atividade.cod_fixo_ativ not in list_cod_fixo:
                    valor = float(atividade.valor) * qt_meses
                    dict_inst[nome_inst] += valor
                    list_cod_fixo.append(atividade.cod_fixo_ativ)
            else:
                # Adiciona o valor da atividade ao total da instituição
                try:
                    dict_inst[nome_inst] += float(atividade.valor)
                except ValueError:
                    dict_inst[nome_inst] += 0  # Se ocorrer um erro de conversão, adicione 0
    
    return dict_inst

def gerar_grafico_tipo(atividades, qt_meses) :

    dict_tipo = {}
    list_cod_fixo = []
    list_id_vir = []

    for atividade in atividades:
        nome_tipo = atividade.tipo_atividade.nome_tipo

        if atividade.id_vir not in list_id_vir:
            list_id_vir.append(atividade.id_vir)

            # Inicializa o total se a instituição ainda não estiver no dicionário
            if nome_tipo not in dict_tipo:
                dict_tipo[nome_tipo] = 0

            if atividade.fixo_mensal_ativ:
                if atividade.cod_fixo_ativ not in list_cod_fixo:
                    valor = float(atividade.valor) * qt_meses
                    dict_tipo[nome_tipo] += valor
                    list_cod_fixo.append(atividade.cod_fixo_ativ)
            else:
                # Adiciona o valor da atividade ao total da instituição
                try:
                    dict_tipo[nome_tipo] += float(atividade.valor)
                except ValueError:
                    dict_tipo[nome_tipo] += 0  # Se ocorrer um erro de conversão, adicione 0

    return dict_tipo

def gerar_grafico_mes(atividades) :

    dict_mes = {}
    list_id_vir = []
    list_Control = []

    for atividade in atividades:
        mes = atividade.data.month
        control = f'{atividade.cod_fixo_ativ} - {mes}'

        if atividade.id_vir not in list_id_vir:
            list_id_vir.append(atividade.id_vir)

            # Inicializa o total se a instituição ainda não estiver no dicionário
            if mes not in dict_mes:
                dict_mes[mes] = 0

            if atividade.fixo_mensal_ativ:
                if control not in list_Control:
                    dict_mes[mes] += float(atividade.valor)
                    list_Control.append(control)
            else:
                # Adiciona o valor da atividade ao total da instituição
                try:
                    dict_mes[mes] += float(atividade.valor)
                except ValueError:
                    dict_mes[mes] += 0  # Se ocorrer um erro de conversão, adicione 0
        
    return dict_mes
    
def financeiro(request):

    mes = datetime.today().month        

    dict_financ = filtrar_mes(mes)

    etiquetas = dict_financ['etiquetas']
    valores = dict_financ['valores']
    dict_financ = dict_financ['dict_financ']

    return render(request, 'atividades/financeiro.html', {'financeiro': dict_financ, 'etiquetas': json.dumps(etiquetas), 'valores': json.dumps(valores)})


@require_GET
def atualizar_financeiro(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        periodoSelect = request.GET.get('periodoSelect')
        try:
            if periodoSelect == '1':
                mesSelect = request.GET.get('mesSelect')
                dict_financ = filtrar_mes(int(mesSelect))
            elif periodoSelect == '2':
                anoSelect = request.GET.get('anoSelect')
                dict_financ = filtrar_ano(int(anoSelect))
            elif periodoSelect == '3':
                dict_financ = filtrar_ate_fim_mes()
            elif periodoSelect == '4':
                dict_financ = filtrar_ate_fim_ano()
            elif periodoSelect == '5':
                dict_financ = filtrar_todo_periodo()
            elif periodoSelect == '6':
                dataInicio = request.GET.get('dataInicio')
                dataFinal = request.GET.get('dataFinal')

                try:
                    datetime.strptime(dataInicio, '%Y-%m-%d')
                    datetime.strptime(dataFinal, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse({'error': 'Formato de data inválido. Use YYYY-MM-DD.'}, status=400)
                
                dict_financ = filtrar_personalizado(dataInicio, dataFinal)
        except ValueError:
            return JsonResponse({'error': 'Data inválida'}, status=400)
        
        if dict_financ:
            etiquetas = dict_financ['etiquetas']
            valores = dict_financ['valores']
            dict_financ = dict_financ['dict_financ']
        else:       
            return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

        try:
            html_content = render_to_string('atividades/partials/base_financeiro.html', {'financeiro': dict_financ, 'etiquetas': etiquetas, 'valores': valores})
        except Exception as e:
            return JsonResponse({'error': f'Erro ao renderizar o template: {str(e)}'}, status=500)

        return JsonResponse({'html': html_content, 'etiquetas': etiquetas, 'valores': valores})
    else:
        return JsonResponse({'error': 'Requisição inválida'}, status=400)
    
@require_GET
def atualizar_grafico(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        periodoSelect = request.GET.get('periodoSelect')
        graficoSelect = request.GET.get('graficoSelect')
        try:
            if periodoSelect == '1':
                mesSelect = request.GET.get('mesSelect')
                atividades = Atividades.objects.filter(data__month=int(mesSelect), nao_remunerado=False)

            elif periodoSelect == '2':
                anoSelect = request.GET.get('anoSelect')
                atividades = Atividades.objects.filter(data__year=int(anoSelect), nao_remunerado=False)

            elif periodoSelect == '3':
                data_inicio = datetime.today().date()
                ano = data_inicio.year
                mes = data_inicio.month
                ultimo_dia = calendar.monthrange(ano, mes)[1]
                data_final = datetime(ano, mes, ultimo_dia).date()

                atividades = Atividades.objects.filter(data__range=(data_inicio, data_final))

            elif periodoSelect == '4':
                data_inicio = datetime.today().date()
                ano = data_inicio.year
                data_final = datetime(ano, 12, 31).date()    
                atividades = Atividades.objects.filter(data__range=(data_inicio, data_final), nao_remunerado=False)

            elif periodoSelect == '5':
                atividades = Atividades.objects.filter(nao_remunerado=False)

            elif periodoSelect == '6':
                dataInicio = request.GET.get('dataInicio')
                dataFinal = request.GET.get('dataFinal')

                try:
                    datetime.strptime(dataInicio, '%Y-%m-%d')
                    datetime.strptime(dataFinal, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse({'error': 'Formato de data inválido. Use YYYY-MM-DD.'}, status=400)
                
                atividades = Atividades.objects.filter(data__range=(dataInicio, dataFinal), nao_remunerado=False)
        except ValueError:
            return JsonResponse({'error': 'Data inválida'}, status=400)
        
        data_inicio = atividades.order_by('data').first()
        data_inicio = data_inicio.data
        data_final = atividades.order_by('data').last()
        data_final = data_final.data

        qt_meses = (data_final.month + 1) - data_inicio.month
        
        try:
            if graficoSelect == '1':
                dict_financ = gerar_grafico_instituicao(atividades, qt_meses)
            elif graficoSelect == '2':
                dict_financ = gerar_grafico_tipo(atividades, qt_meses)
            elif graficoSelect == '3':
                dict_financ = gerar_grafico_mes(atividades)
        except ValueError:
            return JsonResponse({'error': 'Grafico Select Inválido'}, status=400)
        
        if dict_financ:
            etiquetas = list(dict_financ.keys())
            valores = list(dict_financ.values())
        else:       
            return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

        return JsonResponse({'etiquetas': etiquetas, 'valores': valores})
    else:
        return JsonResponse({'error': 'Requisição inválida'}, status=400)
    
def filtrar_rotina(atividades, quant_dias):

    dict_rotina = {}

    quant_horas_totais = quant_dias*24
    
    qt_atividade = 0
    horas = 0
    qt_hora = 0
    qt_hora_remu = 0
    qt_hora_livre = quant_horas_totais

    list_id_vir = []

    dict_remu = gerar_grafico_remuneracao_rotina(atividades)
    lista_etiqueta = list(dict_remu.keys())
    lista_valores = list(dict_remu.values())

    if atividades :

        for atividade in atividades:

            if atividade.id_vir not in list_id_vir:    
                list_id_vir.append(atividade.id_vir)

            if atividade.entrada < atividade.saida:
                horas = (atividade.saida - atividade.entrada)
            else:
                horas = ((24 - atividade.entrada) + atividade.saida)

            if atividade.nao_remunerado == False:
                qt_hora = qt_hora + horas
                qt_hora_remu = qt_hora_remu + horas
            else:
                qt_hora = qt_hora + horas

            qt_hora_livre = quant_horas_totais - qt_hora

            qt_atividade = len(list_id_vir)

        dict_rotina['rotina'] = {
            'horas_atividade': qt_hora,
            'horas_livres': qt_hora_livre,
            'qt_atividade': qt_atividade,
            'media_hr_trab_sem': f'{round(qt_hora_remu / 4)} horas',
            'media_hr_ativ_sem': f'{round(qt_hora / 4)} horas',
            'media_hr_livre_sem': f'{round(qt_hora_livre / 4)} horas',
            'media_hr_trab_dia': f'{round(qt_hora_remu / quant_dias)} horas',
            'media_hr_ativ_dia': f'{round(qt_hora / quant_dias)} horas',
            'media_hr_livre_dia': f'{round(qt_hora_livre / quant_dias)} horas',
            'media_hr_ativ': f'{round(qt_hora / qt_atividade) if qt_atividade else 0} horas'
        }
    else:
        dict_rotina['rotina'] = {
            'horas_atividade': qt_hora,
            'horas_livres': qt_hora_livre,
            'qt_atividade': qt_atividade,
            'media_hr_trab_sem': f'0 horas',
            'media_hr_ativ_sem': f'0 horas',
            'media_hr_livre_sem': f'{round(qt_hora_livre / 4)} horas',
            'media_hr_trab_dia': f'0 horas',
            'media_hr_ativ_dia': f'0 horas',
            'media_hr_livre_dia': f'{round(qt_hora_livre / quant_dias)} horas',
            'media_hr_ativ': f'0 horas'
        }

    return {'dict_rotina': dict_rotina, 'etiquetas': lista_etiqueta, 'valores': lista_valores}

def filtrar_mes_rotina(mes):

    atividades = Atividades.objects.filter(data__month=mes)

    quant_dias = calendar.monthrange(datetime.today().year, mes)[1]

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def filtrar_ano_rotina(ano):

    atividades = Atividades.objects.filter(data__year=ano)

    data_inicio = datetime(ano, 1, 1).date()
    data_final = datetime(ano, 12, 31).date()

    diferenca = data_final - data_inicio
    quant_dias = diferenca.days

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def filtrar_ate_fim_mes_rotina():

    data_inicio = datetime.today().date()
    ano = data_inicio.year
    mes = data_inicio.month
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_final = datetime(ano, mes, ultimo_dia).date()

    quant_dias = ultimo_dia - data_inicio.today().day

    atividades = Atividades.objects.filter(data__range=(data_inicio, data_final))

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def filtrar_ate_fim_ano_rotina():

    data_inicio = datetime.today().date()
    ano = data_inicio.year
    data_final = datetime(ano, 12, 31).date()

    diferenca = data_final - data_inicio
    quant_dias = diferenca.days    

    atividades = Atividades.objects.filter(data__range=(data_inicio, data_final))

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def filtrar_todo_periodo_rotina():

    atividades = Atividades.objects.all()

    atividades_datas = Atividades.objects.order_by('data')
    data_inicio = atividades_datas.first().data
    data_final = atividades_datas.last().data

    diferenca = data_final - data_inicio
    quant_dias = diferenca.days

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def filtrar_personalizado_rotina(dataInicio, dataFinal):

    atividades = Atividades.objects.filter(data__range=(dataInicio, dataFinal))

    data_inicio = datetime.strptime(dataInicio, '%Y-%m-%d').date()
    data_final = datetime.strptime(dataFinal, '%Y-%m-%d').date()

    diferenca = data_final - data_inicio
    quant_dias = diferenca.days

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def gerar_grafico_remuneracao_rotina(atividades) :

    dict_remu = {}
    horas_remu = 0
    horas_nr = 0

    for atividade in atividades:
        if atividade.entrada < atividade.saida:
            horas = atividade.saida - atividade.entrada
        else:
            horas = ((24 - atividade.entrada) + atividade.saida)

        if atividade.nao_remunerado == False:
            horas_remu += horas
        else:
            horas_nr += horas
        
    dict_remu['Remuneradas'] = horas_remu
    dict_remu['Não Remuneradas'] = horas_nr

    return dict_remu

def gerar_grafico_tipo_rotina(atividades):

    dict_tipo = {}
    horas = 0

    for atividade in atividades:

        if atividade.entrada < atividade.saida:
            horas = atividade.saida - atividade.entrada
        else:
            horas = ((24 - atividade.entrada) + atividade.saida)

        nome_tipo = atividade.tipo_atividade.nome_tipo

        # Inicializa o total se a instituição ainda não estiver no dicionário
        if nome_tipo not in dict_tipo:
            dict_tipo[nome_tipo] = 0
        
        # Adiciona o valor da atividade ao total da instituição
        try:
            dict_tipo[nome_tipo] += horas
        except ValueError:
            dict_tipo[nome_tipo] += 0  # Se ocorrer um erro de conversão, adicione 0

    return dict_tipo

def gerar_grafico_categoria_rotina(atividades):

    dict_categoria = {}
    horas = 0

    for atividade in atividades:

        if atividade.entrada < atividade.saida:
            horas = atividade.saida - atividade.entrada
        else:
            horas = ((24 - atividade.entrada) + atividade.saida)

        nome_categoria = atividade.tipo_atividade.categoria

        # Inicializa o total se a instituição ainda não estiver no dicionário
        if nome_categoria not in dict_categoria:
            dict_categoria[nome_categoria] = 0
        
        # Adiciona o valor da atividade ao total da instituição
        try:
            dict_categoria[nome_categoria] += horas
        except ValueError:
            dict_categoria[nome_categoria] += 0  # Se ocorrer um erro de conversão, adicione 0

    return dict_categoria

def gerar_grafico_ocupacao_rotina(atividades, quant_horas_totais):

    dict_ocupacao = {}

    dict_ocupacao['Horas Ocupadas'] = 0
    dict_ocupacao['Horas Livres'] = quant_horas_totais

    for atividade in atividades:

        if atividade.entrada < atividade.saida:
            horas = atividade.saida - atividade.entrada
        else:
            horas = ((24 - atividade.entrada) + atividade.saida)

        dict_ocupacao['Horas Ocupadas'] += horas
        dict_ocupacao['Horas Livres'] -= horas

    return dict_ocupacao


def rotina(request):

    mes = datetime.today().month        

    dict_rotina = filtrar_mes_rotina(mes)

    etiquetas = dict_rotina['etiquetas']
    valores = dict_rotina['valores']
    dict_rotina = dict_rotina['dict_rotina']

    return render(request, 'atividades/rotina.html', {'rotina': dict_rotina, 'etiquetas': json.dumps(etiquetas), 'valores': json.dumps(valores)})

@require_GET
def atualizar_rotina(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        periodoSelect = request.GET.get('periodoSelect')
        try:
            if periodoSelect == '1':
                mesSelect = request.GET.get('mesSelect')
                dict_rotina = filtrar_mes_rotina(int(mesSelect))
            elif periodoSelect == '2':
                anoSelect = request.GET.get('anoSelect')
                dict_rotina = filtrar_ano_rotina(int(anoSelect))
            elif periodoSelect == '3':
                dict_rotina = filtrar_ate_fim_mes_rotina()
            elif periodoSelect == '4':
                dict_rotina = filtrar_ate_fim_ano_rotina()
            elif periodoSelect == '5':
                dict_rotina = filtrar_todo_periodo_rotina()
            elif periodoSelect == '6':
                dataInicio = request.GET.get('dataInicio')
                dataFinal = request.GET.get('dataFinal')

                try:
                    datetime.strptime(dataInicio, '%Y-%m-%d')
                    datetime.strptime(dataFinal, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse({'error': 'Formato de data inválido. Use YYYY-MM-DD.'}, status=400)
                
                dict_rotina = filtrar_personalizado_rotina(dataInicio, dataFinal)
        except ValueError:
            return JsonResponse({'error': 'Data inválida'}, status=400)
        
        if dict_rotina:
            etiquetas = dict_rotina['etiquetas']
            valores = dict_rotina['valores']
            dict_rotina = dict_rotina['dict_rotina']
        else:       
            return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

        try:
            html_content = render_to_string('atividades/partials/base_rotina.html', {'rotina': dict_rotina, 'etiquetas': etiquetas, 'valores': valores})
        except Exception as e:
            return JsonResponse({'error': f'Erro ao renderizar o template: {str(e)}'}, status=500)

        return JsonResponse({'html': html_content, 'etiquetas': etiquetas, 'valores': valores})
    else:
        return JsonResponse({'error': 'Requisição inválida'}, status=400)
    
@require_GET
def atualizar_grafico_rotina(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        periodoSelect = request.GET.get('periodoSelect')
        graficoSelect = request.GET.get('graficoSelect')
        try:
            if periodoSelect == '1':
                mesSelect = request.GET.get('mesSelect')
                atividades = Atividades.objects.filter(data__month=int(mesSelect))
                quant_dias = calendar.monthrange(datetime.today().year, int(mesSelect))[1]
                quant_horas = quant_dias * 24

            elif periodoSelect == '2':
                anoSelect = request.GET.get('anoSelect')
                atividades = Atividades.objects.filter(data__year=int(anoSelect))
                data_inicio = datetime(ano, 1, 1).date()
                data_final = datetime(ano, 12, 31).date()
                diferenca = data_final - data_inicio
                quant_dias = diferenca.days
                quant_horas = quant_dias * 24

            elif periodoSelect == '3':
                data_inicio = datetime.today().date()
                ano = data_inicio.year
                mes = data_inicio.month
                ultimo_dia = calendar.monthrange(ano, mes)[1]
                data_final = datetime(ano, mes, ultimo_dia).date()
                atividades = Atividades.objects.filter(data__range=(data_inicio, data_final))
                quant_dias = ultimo_dia - data_inicio.today().day
                quant_horas = quant_dias * 24

            elif periodoSelect == '4':
                data_inicio = datetime.today().date()
                ano = data_inicio.year
                data_final = datetime(ano, 12, 31).date()    
                atividades = Atividades.objects.filter(data__range=(data_inicio, data_final))
                diferenca = data_final - data_inicio
                quant_dias = diferenca.days
                quant_horas = quant_dias * 24 

            elif periodoSelect == '5':
                atividades = Atividades.objects.all()

                data_inicio = Atividades.objects.all().order_by('data').first()
                data_final = Atividades.objects.all().order_by('-data').last()

                diferenca = data_final - data_inicio
                quant_dias = diferenca.days
                quant_horas = quant_dias * 24


            elif periodoSelect == '6':
                dataInicio = request.GET.get('dataInicio')
                dataFinal = request.GET.get('dataFinal')

                try:
                    datetime.strptime(dataInicio, '%Y-%m-%d')
                    datetime.strptime(dataFinal, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse({'error': 'Formato de data inválido. Use YYYY-MM-DD.'}, status=400)
                
                atividades = Atividades.objects.filter(data__range=(dataInicio, dataFinal))

                data_inicio = datetime.strptime(dataInicio, '%Y-%m-%d').date()
                data_final = datetime.strptime(dataFinal, '%Y-%m-%d').date()

                diferenca = data_final - data_inicio
                quant_dias = diferenca.days
                quant_horas = quant_dias * 24

        except ValueError:
            return JsonResponse({'error': 'Data inválida'}, status=400)
        
        try:
            if graficoSelect == '1':
                dict_rotina = gerar_grafico_remuneracao_rotina(atividades)
            elif graficoSelect == '2':
                dict_rotina = gerar_grafico_tipo_rotina(atividades)
            elif graficoSelect == '3':
                dict_rotina = gerar_grafico_categoria_rotina(atividades)
            elif graficoSelect == '4':
                dict_rotina = gerar_grafico_ocupacao_rotina(atividades, quant_horas)
        except ValueError:
            return JsonResponse({'error': 'Grafico Select Inválido'}, status=400)
        
        if dict_rotina:
            etiquetas = list(dict_rotina.keys())
            valores = list(dict_rotina.values())
        else:       
            return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

        return JsonResponse({'etiquetas': etiquetas, 'valores': valores})
    else:
        return JsonResponse({'error': 'Requisição inválida'}, status=400)
    
