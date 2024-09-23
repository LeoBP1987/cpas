from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from calendario.models import Calendario
from atividades.models import Atividades, Instituicao, TipoAtividade, Preferencias
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
import random
import calendar

def index(request):

    """
    View para renderizar a página principal do sistema.

    Esta função exibe uma visão geral do calendário, incluindo uma agenda mensal de todas as atividades cadastradas, atuais e futuras, o calendário do dia atual e o calendário semanal.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP contendo informações sobre a requisição feita pelo usuário.

    Retorna:
    --------
    HttpResponse
        Renderiza a página HTML 'calendario/index.html' com os seguintes contextos:
        - agenda : dict
            Dicionário contendo a agenda mensal de todas a atividades atuais e futuras.
        - dia : dict
            Dicionário com os dados do calendário do dia atual.
        - semana : dict
            Dicionário com os dados do calendário da semana atual.
        - data_param : datetime.date
            Data atual no formato 'YYYY-MM-DD', para montagem do cabeçalho
        - mes : str
            Mês gerado pela função `gerar_mes()` com base na data atual, para montagem do cabeçalho
    
    Notas:
    ------------
    - Se o usuário não estiver autenticado, será redirecionado para a view 'login'.
    """

    if not request.user.is_authenticated:
        return redirect('login')
    
    data_param = datetime.today().date()
    mes = gerar_mes(data_param)

    dict_agenda = montar_calendario_agenda()
    dict_dia = montar_calendario_dia(data_param)
    dict_semana = montar_calendario_semana(data_param)


    return render(request, 'calendario/index.html', {'agenda':dict_agenda, 'dia': dict_dia, 'semana': dict_semana, 'data_param': data_param, 'mes': mes})

def configuracoes(request):

    """
    View para renderizar a página com o menu de configurações do sistema.

    Essa função checa se há calendário disponível para ser gerado no sistema.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP contendo informações sobre a requisição feita pelo usuário.

    Retorna:
    --------
    HttpResponse
        Renderiza a página HTML 'configuracoes/index.html' com um dicionario contendo um boolean que informa True para caso haja calendário disponível para ser gerado no sistema e False em caso contrário.
    
    Notas:
    ------------
    - Por esse página o usuario poderá acessar as opções de configurações como preferências, gerar novos calendários, cadastrar tipos de atividades e outros.
    - A página só exibirá o botão de geração de novos Calendários caso haja calendário disponível para geração no sistema. Além dos Calendários para o ano corrente o sistema disponibiliza o calendário para o ano seguinte a partir do mês 07 do ano corrente.
    """

    calendario_disponivel = False

    ano_atual = date.today().year
    mes_atual = date.today().month

    if not Calendario.objects.filter(ano=ano_atual).exists():
        calendario_disponivel = True

    if (mes_atual >= 7) and ( not Calendario.objects.filter(ano=(ano_atual + 1)).exists()):
        calendario_disponivel = True

    return render(request, 'calendario/configuracoes.html', {'calendario':calendario_disponivel})

def gerar_calendario(request):

    """
    View que gera os objetos que serão usados como calendário no sistema.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP contendo informações sobre a requisição feita pelo usuário.

    Retorna:
    --------
    Redirect para a path 'configuracoes'
    
    Notas:
    ------------
    - A função povoa o model calendario com objetos referentes a cada uma das vinte e quatro horas de cada dia do ano de referencia.
    - O calendário pode ser gerado para o ano atual.
    - O calendário para o ano seguinte só poderá ser gerado a partir do mês 07 do ano atual.
    - Nessa versão do sistema as atividades só poderam ser agendadas em horas completas, não sendo aceitos quebras por minutos.

    """

    ano_atual = date.today().year
    ano_seguinte = ano_atual + 1
    mes_atual = date.today().month


    if not Calendario.objects.filter(ano=ano_atual).exists():
        
        data_registro = date.today()

        if mes_atual < 7:
            while data_registro.year == ano_atual:
                for hora in range(0, 25):
                    Calendario.objects.create(
                        ano=ano_atual,
                        dia=data_registro,
                        range=hora, # hora do dia
                        ocupado=False, # Indicador se a hora esta ocupada
                    )
                data_registro = data_registro + timedelta(days=1)
            messages.success(request, f'O calendário disponível já foi gerado com sucesso!')
            return redirect('configuracoes')

        else:

            while (data_registro.year == ano_atual) or (data_registro.year == ano_seguinte):
                for hora in range(0, 25):
                    Calendario.objects.create(
                        ano=data_registro.year,
                        dia=data_registro,
                        range=hora, # hora do dia
                        ocupado=False, # Indicador se a hora esta ocupada
                    )
                data_registro = data_registro + timedelta(days=1)
                
        messages.success(request, f'O calendário disponível já foi gerado com sucesso!')
        return redirect('configuracoes')

    else:

        data_ref = Calendario.objects.order_by('-dia').first()
        data_max = data_ref + timedelta(days=1)

        while (data_max.year == ano_seguinte):
                for hora in range(0, 25):
                    Calendario.objects.create(
                        ano=data_max.year,
                        dia=data_max,
                        range=hora, # hora do dia
                        ocupado=False, # Indicador se a hora esta ocupada
                    )
                data_max = data_max + timedelta(days=1)
        messages.success(request, f'O calendário disponível já foi gerado com sucesso!')
        return redirect('configuracoes')


def apagar():

    """
    View usada para limpar model Atividades e Calendario em períodos de teste.

    Retorna:
    --------
    str
        Mensagem informando a deleção realizada
    
    Notas:
    ------------
    - Essa função só é possível ser acessada via linhas de comando e só deve ser utilizada por desenvolvedores.
    """

    Atividades.objects.all().delete()
    Calendario.objects.all().delete()

    return 'Estrutura devidademente deletada'

def agendar(instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs, nao_remunerado, fixo_mensal, seq_perso):

    """
    Faz a gestão dos cadastros de novas atividades e suas agendamentos, garantindo a cobertura de toda a sua sequência caso solicitada

    Parâmetros:
    -----------
    instituicao : str
        Id da Instituição onde ocorrerá a atividade.
    tipo :  str
        Id do Tipo da atividade cadastrada
    data : str
        Data em que atividade foi criada.
    entrada : str
        Hora em que a atividade será iniciada
    saida : str
        Hora em que a atividade será finalizada
    valor : str
        Valor recebido pela unidade
    sequencia : str
        Identificador de tipo de sequencia selecionada pelo usuário
    data_final : str
        Data de término da sequência
    obs : str
        Observaçaõ pertinentes à atividade
    nao_remunarado : boolean
        Indicador caso a atividade não seja remunerada
    fixo_mensal : boolean
        Indicador caso a atividade faça parte de pagamento fixo mensal realizado pela instituição
    seq_perso : list
        Lista contendo as ocorrências desejadas do dia da semana dentro de cada mês. Exemplo: [1, 3] para selecionar a 1ª e a 3ª ocorrência do dia da semana de `data_inicio` em cada mês. Isso caso o usuário opte por uma sequencia personalizada

    Retorno:
    --------
    boolean
        Retorna True se o agendamento foi realizado com sucesso, ou False em caso de falha.
    
    Notas:
    ------
    - A função lida com atividades que passam da meia-noite, dividindo o agendamento em dois dias.
    - As sequências personalizadas são processadas separadamente, e a função garante que os agendamentos sejam evitados em dias indisponíveis.
    - Usa Função 'gerar_cod' para o campo 'cod' dedicado a possibilitar tratamento unificado para atividades de mesma sequência
    
    """

    agendado = False

    h_ent = int(entrada) # Variável com 'entrada' convertida em int
    h_saida = int(saida) # Variável com 'saida' convertida em int
    data_atividade = datetime.strptime(data, '%Y-%m-%d').date()
    data_final = datetime.strptime(data_final, '%Y-%m-%d').date()

    virada = False # Variável para controle de atividades que passem a meia-noite

    cod = gerar_cod() # Gera código único para tratamento unificado para atividades de mesma sequência

    if h_ent < h_saida: # Checa se finaliza no mesmo dia
        
        # Caso sim, atribui range de horas transcorridas da atividade em uma váriavel
        horas = range(h_ent, h_saida + 1)
        horasS = None

        # Obtém lista de dias indisponiveis para cadastro em caso de sequência
        verifica_except = checar_sequencia(sequencia, seq_perso, data_atividade, data_final, horas)
        data_except = verifica_except['list_confirm']
    else:

        # Caso não, declara 'virada' True e divide o range de horas transcorridas da atividade em duas variáveis prevendo a virada de dia 
        virada = True
        horas = range(h_ent, 25)
        horasS = range(0, h_saida + 1)

        # Obtém lista de dias indisponiveis em duas etapas, com seus respectivos dias e ranges de horários
        verifica_except = checar_sequencia(sequencia, seq_perso, data_atividade, data_final, horas)
        except_1 = verifica_except['list_confirm']
        verifica_except = checar_sequencia(sequencia, seq_perso, data_atividade + timedelta(days=1), data_final, horasS)
        except_2 = verifica_except['list_confirm']
        data_except = except_1 + except_2

    if sequencia: 
        if sequencia == '1': # Para sequência de dias úteis
            while data_atividade <= data_final:
                
                dia_semana = data_atividade.weekday()
                
                if dia_semana != 5 and dia_semana !=6 and data_atividade not in data_except:
                    agendado = criar_e_agendar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, nao_remunerado, fixo_mensal, seq_perso, horas, horasS, virada)

                data_atividade = data_atividade + timedelta(days=1)
                
        elif sequencia == '2': # Para sequência semanal
            while data_atividade <= data_final:
                if data_atividade not in data_except:
                    agendado = criar_e_agendar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, nao_remunerado, fixo_mensal, seq_perso, horas, horasS, virada)
                        
                data_atividade = data_atividade + timedelta(weeks=1)

        elif sequencia == '3': # Para sequência quinzenal
            while data_atividade <= data_final:
                if data_atividade not in data_except:
                    agendado = criar_e_agendar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, nao_remunerado, fixo_mensal, seq_perso, horas, horasS, virada)

                data_atividade = data_atividade + timedelta(weeks=2)

        elif sequencia == '4': # Para sequência mensal
            while data_atividade <= data_final:
                if data_atividade not in data_except:
                    agendado = criar_e_agendar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, nao_remunerado, fixo_mensal, seq_perso, horas, horasS, virada)

                data_atividade = data_atividade + relativedelta(months=1)

    elif seq_perso: # Para sequência personalizada

        # Obtém lista_personalizada dos dias solicitados na sequencia personalizada 
        lista_personalizada = gerar_lista_personalizada(data_atividade, data_final, seq_perso)

        for data_perso in lista_personalizada:
            data_perso = datetime.strptime(data_perso, '%Y-%m-%d').date()

            if data_perso not in data_except:
                agendado = criar_e_agendar_atividade(instituicao, tipo, data_perso, entrada, saida, valor, sequencia, data_final, obs, cod, nao_remunerado, fixo_mensal, seq_perso, horas, horasS, virada)

    else: # Para caso não haja sequência
        agendado = criar_e_agendar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, nao_remunerado, fixo_mensal, seq_perso, horas, horasS, virada) 

    return agendado

def checar_sequencia(sequencia, seq_perso, data_atividade, data_final, horas):

    """
    View chamada no momento em que o usuario solicita um cadastro em sequencia. Ela checa a disponbilidade de todos os dias incluídos na sequencia em questão.

    Caso haja indisponibilidade para algum dia, a função incluí em uma lista que é retornada no final

    Parâmetros:
    -----------
    sequencia : str
        Identificador do tipo de sequência selecionada pelo usuário
    seq_perso : list
        Lista contendo as ocorrências desejadas do dia da semana dentro de cada mês. Exemplo: [1, 3] para selecionar a 1ª e a 3ª ocorrência do dia da semana de `data_atividade` em cada mês. Isso caso o usuário opte por uma sequencia personalizada
    data : datetime
        Data em que atividade foi criada.
    data_final : datetime
        Data de término da sequência
    horas : list of int
        Lista com range de horas em que a atividade ira ocorrer    

    Retorno:
    --------
    dict
        Retorna dicionario com lista de datas com indisponibilidade para cadastro e variavel do tipo boolean com True para o caso de sucesso da função e False para cado contrário.
    
    Notas:
    ------
    - Usa a função 'gerar_lista_personalizada' para obter lista de data em caso de sequencia personalizada.
    
    """

    confirm = False
    list_confirm = []

    if sequencia == '1': # Para sequência de dias úteis
        while data_atividade <= data_final:
            dia_semana = data_atividade.weekday()
            if dia_semana != 5 and dia_semana !=6:
                for hora in horas:                        
                    if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                        confirm = True
                        list_confirm.append(data_atividade)
                        break
            data_atividade = data_atividade + timedelta(days=1)

    elif sequencia == '2': # Para sequência semanal
        while data_atividade <= data_final:
            for hora in horas:
                if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                    confirm = True
                    list_confirm.append(data_atividade)
                    break              
            data_atividade = data_atividade + timedelta(weeks=1)    

    elif sequencia == '3': # Para sequência quinzenal
        while data_atividade <= data_final:
            for hora in horas:
                if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                    confirm = True
                    list_confirm.append(data_atividade)
                    break
            data_atividade = data_atividade + timedelta(weeks=2)

    elif sequencia == '4': # Para sequência mensal
        while data_atividade <= data_final:
            for hora in horas:
                if Calendario.objects.filter(dia=data_atividade, range=hora, ocupado=True).exists():
                    confirm = True
                    list_confirm.append(data_atividade)
                    break
            data_atividade = data_atividade + relativedelta(months=1)

    elif seq_perso: # Para sequência personalizada
        lista_personalizada = gerar_lista_personalizada(data_atividade, data_final, seq_perso)

        for data_perso in lista_personalizada:
            data_perso = datetime.strptime(data_perso, '%Y-%m-%d').date()
            for hora in horas:
                if Calendario.objects.filter(dia=data_perso, range=hora, ocupado=True).exists():
                    confirm = True
                    list_confirm.append(data_perso)
                    break

    return {'list_confirm':list_confirm, 'confirm':confirm}

def criar_e_agendar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, nao_remunerado, fixo_mensal, seq_perso, horas, horasS, virada):

    """
    Faz a gestão dos cadastros de novas atividades e agendamentos, com foco na existência de virada de dia para os casos de atividades que passem a meia-noite

    Parâmetros:
    -----------
    Todos identicos à com as seguintes mudanças e acréscimos:

    data_atividade : datetime
        Data de cadastro da atividade

    entrada : int
        Horário de entrada da atividade

    saida : int
        Horário de saída da atividade

    data_final : datetime
        Data de término da sequência

    horas : list int
        Lista com o range de horários entre entrada e saída da atividade. Caso passe da meia-noite o valor final será 24

    horasS : list int
        Lista com o range de horários de atividade que passaram da meia-noite, com o valor inicial sempre sendo 0 e o valor final sendo igual à saida da atividade

    virada : boolean
        Indicador se há virada de dia na atividade 

    Retorno:
    --------
    boolean
        Retorna True se o agendamento foi realizado com sucesso, ou False em caso de falha.
    
    Notas:
    ------
    - A função lida com atividades que passam da meia-noite, dividindo o agendamento em dois dias.
    - A função gerar_atividade já chamará a função gerar_agendamento
    - Mesmo no caso de quebra de atividades, que passem da meia-noite, é gerado o mesmo id_vir, garantindo assim um tratamento unificado para ambas.
    - Usa função gerar_id_vir() para o campo id_vir dedicado a garantir tratamento único para atividade que sejam quebradas em duas por conta de passar da meia-noite
    
    """

    if not virada:
        id_vir = gerar_id_vir() # Gera código único para tratamento unificado de atividade que passem da meia-noite

        agendado = gerar_atividade(instituicao, tipo, data_atividade, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso, horas)
    else:
        id_vir = gerar_id_vir() # Gera código único para tratamento unificado de atividade que passem da meia-noite

        data_virada = data_atividade + timedelta(days=1)

        agendado = gerar_atividade(instituicao, tipo, data_atividade, entrada, 24, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso, horas)

        if Calendario.objects.filter(dia=data_virada).exists():
            agendado = gerar_atividade(instituicao, tipo, data_virada, 0, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso, horasS)

    return agendado

def gerar_lista_personalizada(data_inicio, data_final, ordinal):

    """
    Gera a lista de datas referente a determinada sequencia personalizada solicitada pelo usuario.

    Parâmetros:
    -----------
    data_inicio : datetime
        Data em que atividade foi criada.
    data_final : datetime
        Data de término da sequencia.
    ordinal : list
        Lista contendo as ocorrências desejadas do dia da semana dentro de cada mês. Exemplo: [1, 3] para selecionar a 1ª e a 3ª ocorrência do dia da semana de `data_inicio` em cada mês.

    Retorno:
    --------
    list of str
        Retorna uma lista de strings representando as datas no formato 'YYYY-MM-DD' para as ocorrências solicitadas.
    
    Exemplo:
    --------
    Para uma data de início em uma quinta-feira, `ordinal=[1, 3]` retornaria a 1ª e 3ª quinta-feira de cada mês dentro do intervalo.
    """

    list_meses = [(data_inicio.month, data_inicio.year)] # Inicializa lista de meses do período da atividade
    lista_personalizada = []

    dia_semana = data_inicio.weekday() # Obtém o dia da semana de 'data_inicio'

    cal = calendar.Calendar() # Cria um calendário para o mês e ano indicados como parametro

    # Adiciona à lista de meses, todos os meses do intervalo entre 'data_inicio' e 'data_final'
    while data_inicio <= data_final:
        if data_inicio.month != list_meses[-1][0]:
            list_meses.append((data_inicio.month, data_inicio.year))
        data_inicio = data_inicio + relativedelta(months=1)

    # Percorre todos os meses de list_mes para gerar a lista_personalizada de retorno
    for mes in list_meses:

        # Gera a lista de todo os dias da semana iguais ao dia da semana de 'dia_inicio' 
        lista_dias = [dia for dia in cal.itermonthdays2(mes[1], mes[0]) if dia[0] != 0 and dia[1] == dia_semana]

        # Seleciona as ocorrencias de acordo com o 'ordinal'
        for item in ordinal:
            item_int = int(item)     
            if len(lista_dias) > item_int: # Evita a lógica para ordinal 5 em meses que só têm 4 ocorrências
                dia_ordinal = lista_dias[item_int][0]
                data = datetime(mes[1], mes[0], dia_ordinal)
                data_format = data.strftime('%Y-%m-%d')

                # Adiciona à lista se a data for futura ou atual
                if data.date() >= datetime.today().date():
                    lista_personalizada.append(data_format)

    return lista_personalizada

def gerar_atividade(instituicao, tipo, data, entrada, saida, valor, sequencia, data_final, obs, cod, id_vir, nao_remunerado, fixo_mensal, seq_perso_ativ, horas):

    """
    View que realiza cadastro de novas atividades e chama função para agendamento dessas atividades em suas respectivas horas

    Parâmetros:
    -----------
    instituicao : str
        Id do Instituição onde ocorrerá a atividade.
    tipo :  str
        Id do Tipo da atividade cadastrada
    data : datetime
        Data em que atividade foi criada.
    entrada : int
        Hora em que a atividade será iniciada
    saida : int
        Hora em que a atividade será finalizada
    valor : str
        Valor recebido pela unidade
    sequencia : str
        Identificador de tipo de sequencia selecionada pelo usuário
    data_final : datetime
        Data de término da sequência
    obs : str
        Observaçaõ pertinentes à atividade
    cod : int
        Código único gerado para possibilitar tratamento unificado para atividades geradas em sequência.
    id_vir : int
        Código único gerado para garantir tratamento unificado de atividades quebradas em duas por passarem da meia-noite
    nao_remunarado : boolean
        Indicador caso a atividade não seja remunerada
    fixo_mensal : boolean
        Indicador caso a atividade faça parte de pagamento fixo mensal realizado pela instituição
    seq_perso : list
        Lista contendo as ocorrências desejadas do dia da semana dentro de cada mês. Exemplo: [1, 3] para selecionar a 1ª e a 3ª ocorrência do dia da semana de `data_inicio` em cada mês. Isso caso o usuário opte por uma sequencia personalizada

    Retorno:
    --------
    boolean
        Retorna True se o agendamento foi realizado com sucesso, ou False em caso de falha.
    
    Notas:
    ------
    - A função em seu retorno chama a função gerar_agendamento para garantir o agendamento da atividade em seus respectivos horários
    
    """

    instituicao = Instituicao.objects.get(id=instituicao) # Usa id da Instituição para recuperar instância do modelo 'Instituição'

    tipo = TipoAtividade.objects.get(id=tipo) # Uda id do tipo de atividade para recuperar instância do modelo 'Tipo de Atividade'

    cod_fixo_ativ = instituicao.cod_fixo if fixo_mensal else '' # Recupera o cod_fixo da instituição para desta atividade fazer parte de pagamento fixo mensal realizado pela mesma

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

    # Garante agendamento da atividade em seu respectivos horários
    return gerar_agendamento(atividade, data, horas) 

def gerar_agendamento(atividade, data, horas):

    """
    View para gerar agendamento das atividades em suas respectivas horas no Calendário.

    Parâmetros:
    -----------
    atividade : Atividade
        Instância do modelo Atividade que será adicionada ao calendário.
    data : str
        Data da atividade no formato DD-MM-YYYY
    horas : list of int
        Lista com o range das horas em que ocorrerão a atividade.

    Retorna:
    --------
    boolean
        Retorna True para o caso do agendamento ter sido realizado com sucesso e False cao contrário
    
    """

    agendado = False

    for hora in horas:
        calendario = Calendario.objects.filter(dia=data, range=hora).first()
        calendario.ocupado = True
        calendario.atividades.add(atividade)
        calendario.save()
        agendado = True

    return agendado
    
@require_GET
def disponibilidade(request):

    """
    View que retorna lista com as horas disponiveis para serem exibidas no campo 'entrada' do cadastro de novas atividades.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP contendo dados como o método GET e os parâmetros da consulta.

    Retorno:
    --------
    JsonResponse
        - Retorna um JSON com um dicionário contento uma lista de tuplas.

    Notas:
    --------
        - A lista de tuplas que retorna é filtrada apenas com as horas diponiveis do dia onde o primeiro valor da tupla representa o horário como inteiro e o segundo é uma string com a formatação adequada para a exibição na label.

    Tratamento de Erros:
    --------------------
    - Se a data fornecida for inválida, retorna um erro 'Dados insuficientes'.

    """

    data = request.GET.get('data')

    if not data:
        return JsonResponse({'disponibilidade':[], 'erro':'Dados insuficientes'})

    horario = Calendario.objects.filter(dia=data)

    HORAS = [(hora.range, f'{hora.range:02d}:00') for hora in horario if not hora.ocupado and hora.range != 24]
    
    return JsonResponse({'disponibilidade': HORAS})

@require_GET
def disponibilidade_saida(request):

    """
    View que retorna lista com as horas disponiveis para a saída de uma atividade depois que o usuario já selecionou sua data e sua hora de entrada.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP contendo dados como o método GET e os parâmetros da consulta.

    Retorno:
    --------
    JsonResponse
        - Retorna um JSON com um dicionário contento uma lista de tuplas.

    Notas:
    --------
        - A função garante que as horas disponiveis sejam posteriores ao horário de entrada.
        - A lista finaliza na primeira hora indisponivel encontrada ou depois de 24 horas.
        - A lista de tuplas que retorna é filtrada apenas com as horas diponiveis do dia onde o primeiro valor da tupla representa o horário como inteiro e o segundo é uma string com a formatação adequada para a exibição na label.

    Tratamento de Erros:
    --------------------
    - Se a data fornecida for inválida, retorna um erro 'Dados insuficientes'.

    """

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

    """
    View para checar se há indisponibilidade para alguma data de determinada sequência solicitada pelo usuários.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP contendo dados como o método GET e os parâmetros da consulta.

    Retorno:
    --------
    JsonResponse
        - Retorna um JSON com um dicionário contento os seguintes contextos:
          - 'confirm': Variável do tipo 'boolean' que indica se foi encontrada alguma data indisponivel. Se sim, ela retorna True, caso contrário retorna False.
          - 'msg_confirm': Mensagem formatada para informar usuário das datas com indisponibilidade que foram encontradas.
          - 'list_except': Lista das datas com indiponibilidade
    
    Funcionamento:
    --------------
    - Inicializa as variáveis que servirão de retorno da view.
    - Recupera parâmetros enviados pelo usuário definindo à sequência desejada.
    - Verifica se a atividade passa da meia-noite.
    - Caso não, armazena período da atividade na variável 'horas', usa a função 'checar_sequencia' para obter datas com indisponibilidade, armazena retorno da função separadamente nas variáveis 'list_except' e 'confirm'.
    - Caso sim, realiza a checagem na função 'checar_sequencia' em duas etapas. Primeiro checando do horário de entrada às 24. Por fim, checando de 00 ao horário de saída.
    - Formata 'msg_confirm' com os dias obtidos em 'list_except'.

    """

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
    h_ent = int(entrada) #Converte 'entrada' em inteiro para uso em calculos
    h_saida = int(saida) #Converte 'saida' em inteiro para uso em calculos

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

@require_GET
def atualizar_calendario(request):
    """
    Atualiza o calendário diario via requisição AJAX, alterando o dia com base nos parâmetros enviados pelo usuário que pode solicitar ver o dia seguinte, anterior ou um dia específico através de botões no template.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP contendo dados como o método GET e os cabeçalhos.

    Retorno:
    --------
    JsonResponse
        - Retorna um JSON contendo o HTML atualizado do calendário diario.
    
    Funcionamento:
    --------------
    - A função verifica se a requisição é uma requisição AJAX, através do cabeçalho 'X-Requested-With'.
    - Checa o parâmetro 'control' que indica se o usuário deseja checar o dia seguinte, anterior ou um dia específico.
    - Se o parâmetro `control` for '1', adiciona um dia à data enviada.
    - Se o parâmetro `control` for '2', subtrai um dia na data enviada.
    - Se o parâmetro `control` for '3', utiliza a data enviada como parâmetro exato.
    - Utiliza a função `montar_calendario_dia` para obter os dados do dia.
    - Renderiza o template parcial 'calendario/partials/base_calendario_dia.html' com os dados.
    
    Tratamento de Erros:
    --------------------
    - Se a data fornecida no parâmetro `data` for inválida, retorna um erro 'Data inválida' (HTTP 400).
    - Se não houver dados para o dia selecionado, retorna um erro 'Nenhum dado encontrado' (HTTP 404).
    - Caso ocorra um erro durante a renderização do template, retorna um erro específico com o código de status HTTP 500.
    - Caso a requisição não seja AJAX, retorna um erro 'Requisição inválida' (HTTP 400).
    """

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
    """
    Atualiza o calendário semanal via requisição AJAX, alterando a semana com base no parâmetro enviado pelo usuário ao solicitar ver a semana seguinte ou a anterior através de botões no template.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP contendo dados como o método GET e os cabeçalhos.

    Retorno:
    --------
    JsonResponse
        - Retorna um JSON contendo o HTML atualizado do calendário semanal.
    
    Funcionamento:
    --------------
    - A função verifica se a requisição é uma requisição AJAX, através do cabeçalho 'X-Requested-With'.
    - Checa o parâmetro 'control' que indica de o usuário deseja checar a semana seguinte ou a anterior
    - Se o parâmetro `control` for '1', subtrai uma semana da data enviada.
    - Se o parâmetro `control` for '2', adiciona uma semana à data enviada.
    - Utiliza a função `montar_calendario_semana` para obter os dados da semana e a função `gerar_mes` para gerar o nome do mês correspondente.
    - Renderiza o template parcial 'calendario/partials/base_calendario_semana.html' com os dados.
    
    Tratamento de Erros:
    --------------------
    - Se a data fornecida no parâmetro `data` for inválida, retorna um erro 'Data inválida' (HTTP 400).
    - Se não houver dados para a semana selecionada, retorna um erro 'Nenhum dado encontrado' (HTTP 404).
    - Caso ocorra um erro durante a renderização do template, retorna um erro específico com o código de status HTTP 500.
    - Caso a requisição não seja AJAX, retorna um erro 'Requisição inválida' (HTTP 400).
    """

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

def montar_calendario_dia(data):

    """
    View chamada para obter os dados para a montagem do calendário da data enviada como parâmetro.

    Parâmetros:
    -----------
    data : datetime
        Data enviada como parâmetro para a montagem do calendário

    Retorno:
    --------
    dict
        Retorna dicionário com os dados para a montagem do calendário dia para referência ao campo 'data'.
    
    Funcionamento:
    --------------
    - A função cria a variavel 'data_calendario' para poder ser utilizada como filtro posteriormente.
    - Inicializa a montagem do dicionário com os campos 'dia_semana', 'num_dia' e 'mes' que serão usados como cabecalho e também inicializa uma lista vazia, 'lista_atividade', para receber as atividades da data referência.
    - Recupera os objetos do modelo 'Calendario' para à data referência.
    - Analisa cada um dos objetos recuperados consultando no modelo Atividades se há atividades previstas para aquelas respectivas hora e dia.
    - Caso haja, adiciona a atividade à lista_atividade com os campos 'id', 'hora', 'tipo', 'periodo' e 'tamanho'.

    Notas:
    --------------
    - O campo 'tamanho' define a classe que será usada pela DIV no template. Baseado no tamanho da atividade será definida uma classe que adeque sua respectiva DIV conforme o layout da página.

    """

    data_param = data
    data_calendario = data_param.strftime('%Y-%m-%d')
    
    dict_dia = {}

    dia_semana = gerar_dia_semana(data_param) if data_param else 'None'
    num_dia = f'{data_param.day:02d}' if data_param else 'None'
    mes = gerar_mes(data_param)
    dict_dia[data_calendario] = {
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

    """
    View chamada para obter os dados para a montagem do calendário semanal da semana da data enviada como parâmetro.

    Parâmetros:
    -----------
    data : datetime
        Data enviada como parâmetro para a montagem do calendário

    Retorno:
    --------
    dict
        Retorna um dicionário contendo dois dicionários:
        - 'dict_semana': Dicionário com os dados para a montagem das colunas, que representarão os dias, da tabela do calendário semanal.
        - 'dict_horas': Dicionário com os dados para a montagem das linhas, que representarão as horas, da tabela do calendário semanal.

    Funcionamento:
    --------------
    - Inicializa os dicionários 'dict_semana' e 'dict_horas'. O dicionário 'dict_semana' é iniciado com uma entrada vazia para a coluna que exibirá as horas.
    - Usa a Função 'obter_semana' para obter a semana da data fornecida.
    - Adiciona cada um dos dias da semana obtida em 'dict_semana', para a criação das colunas da tabela.
    - Preenche o dicionário 'dict_horas' com registros para cada uma das 24 horas do dia, inserindo uma classe que deixará 'invisível' a hora '0'.
    - Em cada registro de 'dict_horas' cria uma lista de dicionarios, 'linha', que representará as colunas da tabela.
    - O primeiro dicionário da lista 'linha' será referente à primeira coluna da tabela, que exibirá as horas.
    - Em seguida a função percorre cada um dos 24 registros de 'dict_horas' e para cada um deles percorre os registros de 'dict_semana' gerando um dicionário por coluna.
    - Checa se há atividade para aquela hora (dict_horas) e aquela data (dict_semana).
    - Caso sim, recupera as informação para serem exibidas na tabela.
    - Caso não, deixa o dicionário em branco.

    """

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

def montar_calendario_agenda():

    """
    View chamada para obter os dados para a montagem da agenda de atividades.

    Retorno:
    --------
    dict
        Retorna um dicionário com os dados das atividades atuais e futuras para montagem da agenda.

    Funcionamento:
    --------------
    - Ajusta variavel 'data_param' para um dia anterior ao dia atual.
    - Recupera todas as atividades atuais e futuras.
    - Inicializa dicionário 'dict_agenda'.
    - Percorre todas as atividades e cria um registro em 'dict_agenda' para cada data encontrada contendo 'sigla_dia', 'num_dia', 'mes' e inicializa uma lista vazia chamada 'lista_dia'.
    - Em 'lista_dia' adiciona todas as atividades ocorridas naquela respectiva data.

    """

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

def gerar_dia_semana(data):

    """
    View que retorna o uma str com o nome do dia da semana da data enviada como parâmetro.

    Parâmetros:
    -----------
    data : str
        Data do dia atual.

    Retorno:
    --------
    str
        Nome do dia da semana do campo 'data'.   
    
    """

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

    """
    View que retorna o uma str com o nome do mês da data enviada como parâmetro.

    Parâmetros:
    -----------
    data : datetime
        Data do dia atual.

    Retorno:
    --------
    str
        Nome do mês do campo 'data'.   
    
    """

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

    """
    View que gera lista com as datas da semana da data enviada como parâmetro, para montagem do calendário da semana.

    Parâmetros:
    -----------
    data : str
        Data do dia atual.

    Retorno:
    --------
    list of date
        Lista de datas da semana do campo 'data'.
    
    Notas:
    ------
    - A semana retornada na lista iniciára pelo dia escolhido pelo usuario em suas configurações de preferencia que são recuperadas nessa função.
    
    """

    data = datetime.strptime(str(data), '%Y-%m-%d').date() # Converte data para datetime

    # Recupera preferência do usuário
    preferencias = Preferencias.objects.get(id=1)
    referencia_inicio = int(preferencias.inicio_semana)
    
    # Encontra o domingo da semana da 'data'
    inicio_semana = data - timedelta(days=data.weekday() + referencia_inicio)
    
    # Gera as datas da semana
    datas_semana = [(inicio_semana + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    
    return datas_semana

def gerar_cod():

    """
    View que gera código único para possibilitar tratamento unificado para atividades geradas para a mesma sequência.

    Retorna:
    --------
    str
        Código único de 2 à 4 digitos
    """

    atividades = Atividades.objects.all() # Recupera todas as atividades do modelo Atividades

    gerado = False

    # Cria lista com todos os 'cod's já criados
    lista_codigos = []
    for atividade in atividades:

        if atividade.cod not in lista_codigos:
            lista_codigos.append(atividade.cod)

    # Garante a geração de um cod único
    while not gerado:
        cod_int = random.randint(0, 9999)
        if cod_int not in lista_codigos:
            cod = f'{cod_int:02d}'
            gerado = True

    return cod

def gerar_id_vir():

    """
    View que gera código único para garantir tratamento unificado para atividades que passem da meia-noite.

    Retorna:
    --------
    str
        Código único de 2 à 4 digitos
    """

    atividades = Atividades.objects.all() # Recupera todas as atividades do modelo Atividades
    
    gerado = False

    # Cria lista com todos os 'id_vir's já criados
    lista_codigos = []
    for atividade in atividades:

        if atividade.id_vir not in lista_codigos:
            lista_codigos.append(atividade.id_vir)

    # Garante a geração de um id_vir único
    while not gerado:
        id_int = random.randint(0, 9999)
        if id_int not in lista_codigos:
            id_vir = f'{id_int:02d}'
            gerado = True

    return id_vir