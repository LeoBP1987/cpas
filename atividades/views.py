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
        valor = forms['valor_padrao'].value()

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

def instituicao(request, id_instituicao):

    instituicao = Instituicao.objects.get(id=id_instituicao)

    dict_inst = {}

    valor = instituicao.valor_padrao
    valor = f'R$ {valor}'
    
    dict_inst['instituicao.id'] = {
        'id': instituicao.id,
        'nome_curto': instituicao.nome_curto if instituicao.nome_curto else '',
        'nome_inst': instituicao.nome_inst,
        'imagem': instituicao.imagem.url if instituicao.imagem else '',
        'valor_padrao': valor,
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

            if not data_final:
                data_final = data

            agendamento = agendar(instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs, nao_remunerado)

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
                atividades = Atividades.objects.filter(cod=atividade.cod)

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
    
def filtrar_financeiro(atividades):

    dict_financ = {}
    total = 0
    qt_atividade = 0
    qt_hora = 0
    list_dia_trab = []
    list_mes = []

    dict_inst = gerar_grafico_instituicao(atividades)
    lista_etiqueta = list(dict_inst.keys())
    lista_valores = list(dict_inst.values())

    if atividades :

        for atividade in atividades:

            total = total + float(atividade.valor)
            qt_atividade = qt_atividade + 1

            if atividade.entrada < atividade.saida:
                qt_hora = qt_hora + (atividade.saida - atividade.entrada)
            else:
                qt_hora = qt_hora + ((24 - atividade.entrada) + atividade.saida)

            if atividade.data not in list_dia_trab:
                list_dia_trab.append(atividade.data)

            if atividade.data.month not in list_mes:
                list_mes.append(atividade.data.month)
    
        dict_financ['financeiro'] = {
            'total': f'R$ {"{:,.2f}".format(round(float(total))).replace(",", "X").replace(".", ",").replace("X", ".")}',
            'media_atividade': f'R$ {"{:,.2f}".format(round(float(total/qt_atividade),2)).replace(",", "X").replace(".", ",").replace("X", ".")}',
            'media_hora': f'R$ {"{:,.2f}".format(round(float(total/qt_hora),2)).replace(",", "X").replace(".", ",").replace("X", ".")}',
            'media_dia_trab': f'R$ {"{:,.2f}".format(round(float(total/len(list_dia_trab)),2)).replace(",", "X").replace(".", ",").replace("X", ".")}',
            'media_mes': f'R$ {"{:,.2f}".format(round(float(total/len(list_mes)),2)).replace(",", "X").replace(".", ",").replace("X", ".")}'
        }
    else:
        dict_financ['financeiro'] = {
            'total': f'R$ 0,00',
            'media_atividade': f'R$ 0,00',
            'media_hora': f'R$ 0,00',
            'media_dia_trab': f'R$ 0,00',
            'media_mes': f'R$ 0,00'
        }

    return {'dict_financ': dict_financ, 'etiquetas': lista_etiqueta, 'valores': lista_valores}

def filtrar_mes(mes):

    atividades = Atividades.objects.filter(data__month=mes)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_ano(ano):

    atividades = Atividades.objects.filter(data__year=ano)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_ate_fim_mes():

    data_inicio = datetime.today().date()
    ano = data_inicio.year
    mes = data_inicio.month
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_final = datetime(ano, mes, ultimo_dia).date()

    atividades = Atividades.objects.filter(data__range=(data_inicio, data_final))

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_ate_fim_ano():

    data_inicio = datetime.today().date()
    ano = data_inicio.year
    data_final = datetime(ano, 12, 31).date()    

    atividades = Atividades.objects.filter(data__range=(data_inicio, data_final))

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_todo_periodo():

    atividades = Atividades.objects.filter(nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_personalizado(dataInicio, dataFinal):

    atividades = Atividades.objects.filter(data__range=(dataInicio, dataFinal))

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def gerar_grafico_instituicao (atividades) :

    dict_inst = {}

    for atividade in atividades:

        total = 0

        if atividade.instituicao.nome_inst not in dict_inst:

            nome_inst = atividade.instituicao.nome_inst

            atividades_inst = atividades.filter(instituicao__nome_inst=atividade.instituicao.nome_inst)

            for inst_atividade in atividades_inst:

                total = total + float(inst_atividade.valor)

            dict_inst[nome_inst] = total

    return dict_inst

def gerar_grafico_tipo (atividades) :

    dict_tipo = {}

    for atividade in atividades:

        total = 0

        if atividade.tipo_atividade.nome_tipo not in dict_tipo:

            nome_tipo = atividade.tipo_atividade.nome_tipo

            atividades_tipo = atividades.filter(tipo_atividade__nome_tipo=nome_tipo)

            for tipo_atividade in atividades_tipo:

                total = total + float(tipo_atividade.valor)

            dict_tipo[nome_tipo] = total

    return dict_tipo

def gerar_grafico_mes (atividades) :

    dict_mes = {}

    for atividade in atividades:

        total = 0

        if atividade.data.month not in dict_mes:

            nome_mes = gerar_mes(atividade.data)

            atividades_mes = atividades.filter(data__month=atividade.data.month)

            for mes_atividade in atividades_mes:

                total = total + float(mes_atividade.valor)

            dict_mes[nome_mes] = total

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
        
        try:
            if graficoSelect == '1':
                dict_financ = gerar_grafico_instituicao(atividades)
            elif graficoSelect == '2':
                dict_financ = gerar_grafico_tipo(atividades)
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


def rotina(request):

    return render(request, 'atividades/rotina.html')
    
