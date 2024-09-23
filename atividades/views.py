from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.contrib import messages
from datetime import date, timedelta, datetime
from atividades.forms import TipoAtividadeForms, InstituicaoForms, AtividadesForms, CategoriaForms, PreferenciasForms
from atividades.models import TipoAtividade, Instituicao, Atividades, Categoria, Preferencias
from calendario.models import Calendario
from calendario.views import agendar, gerar_dia_semana, gerar_mes
import json
import random
import calendar

def atividades(request):

    """
    Exibe a lista de atividades atuais e futuras.

    Esta view filtra as atividades atuais e futuras e as ordena por data. 
    A lista resultante é processada pela função `gerar_lista_atividade` e, em seguida, renderizada no 
    template `atividades/atividades.html`.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'atividades/atividades.html' com a lista de atividades filtradas e processadas.
    """

    dia_atual = datetime.today().date() - timedelta(days=1)

    atividades = Atividades.objects.filter(data__gt=dia_atual).order_by('data')

    list_atividades = gerar_lista_atividade(atividades)


    return render(request, 'atividades/atividades.html', {'atividades': list_atividades})

def gerar_lista_atividade(atividades):

    """
    Processa as atividades e retorna uma lista de dicionários formatados para exibição em cards no template.

    Esta view processa as atividades recebidas como parâmetro e retorna uma lista de dicionarios com os dados dessas atividades já formatados para a montagem dos cards exibidos template.

    Parâmetros:
    -----------
    atividades : QuerySet
        Query com instâncias do modelo 'Atividades' que foram previamente filtradas.

    Retorno:
    --------
    list
        Uma lista de dicionarios, cada um contendo os dados da atividade formatados para a montagem dos cards no template.
    """

    dict_atividade = {}

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

        # Limita o número de caracteres do campo observação para que não expanda a div e quebra o layout da página
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

    return list_atividades

def buscar(request):

    """
    Filtra as atividades atuais e futuras, por ordem de data, e que tenham nos campos 'instituicao' e/ou 'tipo_atividade' os termos procurados pelo usuario no campo de busca.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'atividades/atividades.html' com a lista de atividades filtradas e processadas.
    """

    data_hoje = datetime.today().date()

    atividades = Atividades.objects.filter(data__gt=data_hoje).order_by('data')

    if 'buscar' in request.GET:
        nome_a_buscar = request.GET['buscar']
        if nome_a_buscar:
            atividades = Atividades.objects.filter(Q(instituicao__nome_inst__icontains=nome_a_buscar) | Q(tipo_atividade__nome_tipo__icontains=nome_a_buscar) | Q(instituicao__nome_curto__icontains=nome_a_buscar))

    list_atividades = gerar_lista_atividade(atividades)

    return render(request, 'atividades/buscar.html', {'atividades':list_atividades})

def descrever_seq_perso(seq_perso, dia_semana):

    """
    Trata a descrição que será exibida no card das atividades que façam parte de uma sequência personalizada.

    Parâmetros:
    -----------
    seq_perso : list
        Lista contendo as ocorrências desejadas do dia da semana dentro de cada mês. Exemplo: [1, 3] para selecionar a 1ª e a 3ª ocorrência do dia da semana de `dia_semana` em cada mês. Isso caso o usuário opte por uma sequencia personalizada
    dia_semana : int
        Número relativo ao dia da semana retornada pela função 'weekday()' da data da atividade que o card representará.

    Retorno:
    --------
    str
        Texto contendo a descrição personalizada que será exibida no card.
    """

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
    
    descricao_lista = []
    
    for item in seq_perso:
        ordinal = ordinais.get(item, None)
        if ordinal:
            descricao_lista.append(ordinal)
    
    # Formatação final da string

    if len(descricao_lista) > 1:
        descricao_seq_perso = ', '.join(descricao_lista[:-1]) + f' e {descricao_lista[-1]} {dia}'
    else:
        descricao_seq_perso = f'{descricao_lista[0]} {dia}' if descricao_lista else ''
    
    return descricao_seq_perso

def tipos(request):

    """
    View para exibir todos os tipos de atividades cadastrados.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'atividades/tipos.html' com a QuerySet 'tipos' contendo as informações dos tipos de atividades presentes no modelo TipoAtividade.
    """

    tipos = TipoAtividade.objects.all()

    return render(request, 'atividades/tipos.html', {'tipos':tipos})

def novo_tipo(request):

    """
    Formulário de cadastro de novos tipos de atividade.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'atividades/novo_tipo.html' com o formulário TipoAtividadeForms.
        Se o método for POST: Salva o formulário enviado com as informações inseridas pelo usuário e o redirecionando para a path 'tipos' e exibindo uma mensagem informando o sucesso no cadastro do novo tipo de atividade. 

    Tratamento de erros:
    --------
    - Caso o formulário enviado pelo usuário seja inválido, o formulário não será salvo e o usuário sera encaminhado para a path 'tipos' e visualizará uma mensagem informando o erro no cadastro, pedindo revisão nos dados.
    """

    forms = TipoAtividadeForms()

    if request.method == 'POST':

        forms = TipoAtividadeForms(request.POST)

        if forms.is_valid():
            forms.save()
            messages.success(request,'Novo Tipo de Atividade Cadastrado com Sucesso!')
            return redirect('tipos')
        else:
            messages.error(request,'Erro ao realizar o cadastro. Favor, verifique as informações e tente novamente.')
            return redirect('tipos')

    return render(request, 'atividades/novo_tipo.html', {'forms':forms})

def editar_tipo(request, tipo_id):

    """
    Formulário para editar tipo de atividade relativa ao parâmetro 'tipo_id'.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    tipo_id: int
        ID da instância que deverá ser editada no modelo TipoAtividade.

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'atividades/editar_tipo.html' com o formulário TipoAtividadeForms instânciado pelo parâmetro 'tipo_id' e com a variável tipo contendo a instância do modelo TipoAtividade relativa ao parâmetro 'tipo_id'.
        Se o método for POST: Salva o formulário enviado com as informações inseridas pelo usuário, atualizando em caso de qualquer alteração, e o redirecionando para a path 'tipos', exibindo uma mensagem informando o sucesso na edição do tipo de atividade. 

    Tratamento de erros:
    --------
    - Caso o formulário enviado pelo usuário seja inválido, o formulário não será salvo e o usuário sera encaminhado para a path 'tipos' e visualizará uma mensagem informando o erro no cadastro, pedindo revisão nos dados.
    """

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

    """
    View que deleta a instância do modelo TipoAtividade relativa ao parâmetro 'tipo_id'.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    tipo_id: int
        ID da instância que deverá ser deletado no modelo TipoAtividade.

    Retorno:
    --------
    redirect
        Redireciona o usuário para a path 'tipos' exibindo uma mensagem de sucesso na deleção da instância.
    """

    tipo = TipoAtividade.objects.get(id=tipo_id)

    tipo.delete()

    messages.success(request, 'Deleção realizada com sucesso!')
    return redirect('tipos')

def instituicoes(request):

    """
    View para exibir todas as instituições cadastradas.
    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'atividades/instituicoes.html' com a QuerySet 'instituicoes' contendo as informações das 'instituicoes' presentes no modelo Instituicao.
    """
    
    instituicoes = Instituicao.objects.all()

    return render(request, 'atividades/instituicoes.html', {'instituicoes':instituicoes})

def nova_instituicao(request):

    """
    Formulário de cadastro de novas instituições.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'atividades/nova_instituicao.html' com o formulário InstituicaoForms.
        Se o método for POST: Salva o formulário enviado com as informações inseridas pelo usuário e o redireciona para a path 'instituicoes', exibindo uma mensagem informando sucesso no cadastro da nova instituição.

    Notas:
    --------
    - Antes de salvar o formulário, a view realiza um commit=False para em seguida inserir o campo 'cod_fixo' gerado pela Função 'gerar_cod_fixo' e usado como referência por atividades que integrem valores fixos pagos por essa instituição.

    Tratamento de erros:
    --------
    - Caso o formulário enviado pelo usuário seja inválido, o formulário não será salvo e o usuário encaminhado para a path 'instituicoes', visualizando uma mensagem que informa erro no cadastro, pedindo revisão nos dados.
    """
    
    if request.method == 'POST':

        forms = InstituicaoForms(request.POST, request.FILES)

        if forms.is_valid():
            instituicao = forms.save(commit=False)
            instituicao.cod_fixo = gerar_cod_fixo()

            if instituicao.fixo_mensal_inst:
                valor = str(instituicao.valor_fixo).replace('R$ ', '').replace('.', '').replace(',', '').strip() 
                valor = (valor[:-2] + '.' + valor[-2:]) if len(valor) > 2 else valor
                instituicao.valor_fixo = valor
            instituicao.save()
            messages.success(request,'Nova Instituição Cadastrada com Sucesso!')
            return redirect('instituicoes')
        else:
            messages.error(request,'Erro ao realizar o cadastro. Favor, verifique as informações e tente novamente.')
    else:
        forms = InstituicaoForms()

    return render(request, 'atividades/nova_instituicao.html', {'forms':forms})

def editar_instituicao(request, id_inst):

    """
    Formulário para editar a instituição relativa ao parâmetro 'id_inst'.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    id_inst: int
        ID da instância que deverá ser editada no modelo Instituicao.

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'atividades/editar_instituicao.html' com o formulário InstituicaoForms instânciado pelo parâmetro 'id_inst' e com a variável 'inst' contendo a instância do modelo Instituicao relativa ao parâmetro 'inst_id'.
        Se o método for POST: Salva o formulário enviado com as informações inseridas pelo usuário, atualizando em caso de alterações, e redirecionando para a path 'instituicoes', exibindo uma mensagem informando o sucesso na edição da instituicão. 

    Tratamento de erros:
    --------
    - Caso o formulário enviado pelo usuário seja inválido, o formulário não será salvo e o usuário encaminhado para a path 'instituicoes' visualizando uma mensagem que informa erro no cadastro, pedindo revisão nos dados.
    """

    inst = Instituicao.objects.get(id=id_inst)
    forms = InstituicaoForms(instance=inst)

    if request.method == 'POST':

        forms = InstituicaoForms(request.POST, instance=inst)

        if forms.is_valid():
            inst_edit = forms.save(commit=False)

            if inst_edit.fixo_mensal_inst:
                valor = inst_edit.valor_fixo
                valor = str(valor).replace('R$ ', '').replace('.', '').replace(',', '').strip() 
                inst_edit.valor_fixo = (valor[:-2] + '.' + valor[-2:]) if len(valor) > 2 else valor
            
            inst_edit.save()
            messages.success(request, 'Edição realizada com sucesso')
            return redirect('instituicoes')
        else:
            messages.error(request, 'Não foi possível realizar a edição. Favor revise os dados ou entre em contato com o administrador do sistema.')

    return render(request, 'atividades/editar_instituicao.html', {'forms':forms, 'inst':inst})

def deletar_instituicao(request, id_inst):

    """
    View que deleta a instância do modelo Instituicao relativa ao parâmetro 'id_inst'.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    id_inst: int
        ID da instância que deverá ser deletada no modelo Instituicao.

    Retorno:
    --------
    redirect
        Redireciona o usuário para a path 'instituicoes' exibindo uma mensagem de sucesso na deleção da instância.
    """

    inst = Instituicao.objects.get(id=id_inst)

    inst.delete() 

    messages.success(request, 'Deleção realizada com sucesso!')
    return redirect('instituicoes')

def gerar_cod_fixo():

    """
    View que gera um código único que será passado para o campo 'cod_fixo' da instituição. 
    
    Esse campo será usado de referência por atividades que componham pagamento fixo realizado pela instituição detentora desse código.

    Retorna:
    --------
    str
        Código único de 2 à 4 digitos
    """

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

    """
    View com a instância do modelo Instituicao relativa ao parâmetro id_instituicao.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    id_instituicao : int
        ID da instância que deverá ser editada no modelo Instituicao.

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'atividades/instituicao.html' com o dicionário 'dict_inst' que contém as informações da instituição instânciada.
    """

    instituicao = Instituicao.objects.get(id=id_instituicao)

    dict_inst = {}

    # Formata mascara para campo Valor
    valor = instituicao.valor_fixo
    valor = f'R$ {valor}'
    
    # Monta dicionário com formatação específica para exibição no template instituicao
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

    """
    View com a instância do modelo Atividades relativa ao parâmetro id_atividade.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    id_atividade : int
        ID da instância que deverá ser editada no modelo Atividades.

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'atividades/atividade.html' com o dicionário 'dict_atividade' que contém as informações da atividade instanciada e a variável 'hoje' que contém o dia atual.

    Notas:
    --------
    - A função renderiza o dia atual junto ao template, para que seja usado de parâmetro para decidir se deverá exibir os botões de edição ou não, pois os botões de edição só são exibidos para atividades atuais ou futuras, não permitindo edições em atividades que já ocorrerão.

    """


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

    # Monta dicionário com formatação específica para exibição no template atividade

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

    """
    Formulário de cadastro de novas atividades.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'atividades/nova_atividade.html' com o formulário AtividadesForms.
        Se o método for POST: Armazena as informações submetidas pelo formulário em suas devidas váriveis e as envia como parâmetro para a Função 'agendar' do app calendário.

    Notas:
    --------
    - Caso o campo 'data_final_seq' do formulário esteja vazio pelo fato do usuário não ter selecionado nenhuma sequência, a função preenche o mesmo com a data atual para evitar erros futuros na manipulação desse campo.
    - A função já coloca a devida mascará no campo valor.

    Tratamento de erros:
    --------
    - Caso o formulário enviado pelo usuário seja inválido, o formulário não será salvo e exibirá uma mensagem informando quais são as inconsistências do formulário para que o usuário possa ajustar.
    - Caso o retorno da Função 'agendar' seja False, ou seja, a criação da unidade e seu devidamente agendamento não tenha ocorrido, é exibida a mensagem "Erro ao criar atividade".
    """

    if request.method == 'POST':

        forms = AtividadesForms(request.POST)

        if forms.is_valid():

            instituicao = forms['instituicao'].value()
            tipo = forms['tipo_atividade'].value()       
            data = forms['data'].value()
            entrada = forms['entrada'].value()
            saida = forms['saida'].value()
            valor = forms['valor'].value()
            valor = str(valor).replace('R$ ', '').replace('.', '').replace(',', '').strip() 
            valor = (valor[:-2] + '.' + valor[-2:]) if len(valor) > 2 else valor
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
                messages.error(request,'Erro ao criar atividade')
        else:
            mensagem = f'O formulário de nova atividade apresenta as seguintes inconsistências: {forms.errors}'
            messages.error(request,mensagem)
    else:
        forms = AtividadesForms()


    return render(request, 'atividades/nova_atividade.html', {'forms':forms})

def editar_atividade(request, id_atividade):

    """
    Formulário para editar a atividade relativa ao parâmetro 'id_atividade'.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    id_atividade: int
        ID da instância que deverá ser editada no modelo Atividades.

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'atividades/editar_atividade.html' com o formulário AtividadesForms instanciado pelo parâmetro 'id_atividade' e com a variável 'atividade' contendo a instância do modelo Atividades relativa ao parâmetro 'id_atividade'.
        Se o método for POST: Checa o parâmetro 'extra_param' para verificar se o usuário deseja realizar a alterar na atividade solo ou em toda sua sequência. Em seguida salva o as alterações enviadas pelo formulário se acordo com a opção desejada. 

    Funcionamento:
    --------
    - Cria a variável 'data_atual' para garantir que nenhum edição seja feita em atividades que já ocorrerão.
    - Coloca instância do modelo Atividades, relativa ao parâmetro 'id_atividade', na variável 'atividade'.
    - Checa se o método do request é 'POST'.
    - Caso sim:
        - Obtém formulário enviado pelo método post na variável forms.
        - Checa se o formulário é válido.
        - Caso não, retorna uma mensagem com as inconsistência do formulário para que o usuário posso ajustar.
        - Caso sim, coloca os valores enviados pelo forms em suas devidas variaveis e em seguida checa o valor da variável 'param' que recebeu o valor do campo 'extra_param'.
        - Se o valor de 'param' for 1: Significa que o usuário deseja alterar apenas a atividade solo e então realiza a alteração baseado no 'id_vir' da atividade. Depois redireciona para a path 'index' com mensagem de sucesso.
        - Se o valor de 'param' for 2: Significa que o usuário deseja alterar toda a sequência na qual a atividade esteja incluída, então realiza a alteração baseado no 'cod' da atividade. Depois redireciona para a path 'index' com mensagem de sucesso.
    - Caso não:
        - Obtém o formulário de AtividadesForms instanciado pelo parâmetro id_atividade.
        - Renderiza o template 'atividades/editar_atividade.html' com o formulário AtividadesForms instanciado pelo parâmetro 'id_atividade' e com a variável 'atividade' contendo a instância do modelo Atividades relativa ao parâmetro 'id_atividade'. 

    Tratamento de erros:
    --------
    - Caso o formulário enviado pelo usuário seja inválido, o formulário não será salvo e será exibida uma mensagem com as inconsistência do formulário para que o usuário posso ajustar.
    - Caso o id_atividade tenha alguma inconsistência a 'atividade' receberá de um erro de status=404 ao tenta instanciar a atividade pela função 'get_object_or_404'.

    Notas:
    --------
    - O campo id_vir é destinado a unificar o tratamento de atividades que foram 'quebradas' em duas por passarem da meia-noite. Para maiores entendimenos, ler a documentação da view 'criar_e_agendar_atividade' do app calendário.
    """

    data_atual = datetime.today().date()    
    data_control = data_atual - timedelta(days=1)

    atividade = get_object_or_404(Atividades, id=id_atividade)

    if request.method == 'POST':

        forms = AtividadesForms(request.POST, instance=atividade)

        if forms.is_valid():

            param = forms['extra_param'].value()
            valor = forms['valor'].value()
            valor = str(valor).replace('R$ ', '').replace('.', '').replace(',', '').strip() 
            valor = (valor[:-2] + '.' + valor[-2:]) if len(valor) > 2 else valor
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
                atividades = Atividades.objects.filter(cod=atividade.cod, data__gt=data_control)

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
    else:
        forms = AtividadesForms(instance=atividade)

    return render(request, 'atividades/editar_atividade.html', {'forms':forms, 'atividade':atividade})

def deletar_atividade(request, id_atividade):

    """
    View que deleta a(s) instância(s) do modelo Atividades baseado no campo 'id_vir' da atividade relativa ao parâmetro 'id_atividade'.

    A view deleta apenas as atividades de mesmo 'id_vir' e mantém o restante da sequência, caso haja.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    id_atividade: int
        ID da instância que servirá de referência para deleção no modelo Atividades.

    Retorno:
    --------
    redirect
        Redireciona o usuário para a path 'index' exibindo uma mensagem de sucesso nas deleções realizadas.

    Tratamento de erros:
    --------
    - Caso ocorra algum erro na filtragem da atividade pelo 'id_vir' o usuário será redicionado para a path 'index' e visualizará a mensagem 'Ocorreu um erro deleção não pode ser realizada!'.

    Notas:
    --------
    - A Função percorre os objetos do modelo Calendario relativo as horas em que ocorreriam a atividade deletada e garante a retirada de seu respectivo agendamento.
    """

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

    """
    View que deleta as instâncias do modelo Atividades baseado no campo 'cod' da atividade relativa ao parâmetro 'id_atividade'.

    A view deleta todas as atividade da mesma sequência.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    id_atividade: int
        ID da instância que servirá de referência para deleção no modelo Atividades.

    Retorno:
    --------
    redirect
        Redireciona o usuário para a path 'index' exibindo uma mensagem de sucesso nas deleções realizadas.

    Tratamento de erros:
    --------
    - Caso ocorra algum erro na filtragem da atividade pelo 'cod' o usuário será redicionado para a path 'index' e visualizará a mensagem 'Ocorreu um erro deleção não pode ser realizada!'.

    Notas:
    --------
    - A Função percorre os objetos do modelo Calendario relativo as horas em que ocorreriam a atividade deletada e garante a retirada de seu respectivo agendamento.
    """

    data_atual = datetime.today().date()
    data_control = data_atual - timedelta(days=1)

    get_object_or_404(Atividades, id=id_atividade)
    
    cod = atividade.cod    

    atividades = Atividades.objects.filter(cod=cod, data__gt=data_control)

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

def categorias(request):

    """
    View para exibir todas as categorias cadastradas.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'atividades/categorias.html' com a QuerySet 'categorias' contendo as informações das categorias presentes no modelo Categoria.
    """

    categorias = Categoria.objects.all()

    return render(request, 'atividades/categorias.html', {'categorias':categorias})

def nova_categoria(request):

    """
    Formulário de cadastro de novas categorias.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'atividades/nova_categoria.html' com o formulário CategoriaForms.
        Se o método for POST: Salva o formulário enviado com as informações inseridas pelo usuário e o redirecionando para a path 'categorias', exibindo uma mensagem informando o sucesso no cadastro da nova categoria. 

    Tratamento de erros:
    --------
    - Caso o formulário enviado pelo usuário seja inválido, o formulário não será salvo e o usuário sera encaminhado para a path 'categorias', visualizando mensagem informando erro no cadastro, pedindo revisão nos dados.
    """

    forms = CategoriaForms()

    if request.method == 'POST':

        forms = CategoriaForms(request.POST)

        if forms.is_valid():
            forms.save()
            messages.success(request,'Nova Categoria Cadastrada com Sucesso!')
            return redirect('categorias')
        else:
            messages.error(request,'Erro ao realizar o cadastro. Favor, verifique as informações e tente novamente.')
            return redirect('categorias')

    return render(request, 'atividades/nova_categoria.html', {'forms':forms})

def editar_categoria(request, categoria_id):

    """
    Formulário para editar a categoria relativa ao parâmetro 'categoria_id'.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    categoria_id: int
        ID da instância que deverá ser editada no modelo Categoria.

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'atividades/editar_categoria.html' com o formulário CategoriaForms instânciado pelo parâmetro 'categoria_id' e com a variável 'categoria' contendo a instância do modelo Categoria relativa ao parâmetro 'categoria_id'.
        Se o método for POST: Salva o formulário enviado com as informações inseridas pelo usuário, atualizando em caso de qualquer alteração, e o redirecionando para a path 'categorias', exibindo uma mensagem informando o sucesso na edição da categoria. 

    Tratamento de erros:
    --------
    - Caso o formulário enviado pelo usuário seja inválido, o formulário não será salvo e será exibida a mensagem 'Não foi possível realizar a edição. Favor revise os dados ou entre em contato com o administrador do sistema.'.
    """

    # Formulario de categoria referente à categoria_id enviada para a edição

    categoria = Categoria.objects.get(id=categoria_id)
    
    forms = CategoriaForms(instance=categoria)

    if request.method == 'POST':

        forms = CategoriaForms(request.POST, instance=categoria)

        if forms.is_valid():
            forms.save()
            messages.success(request,'Alterações realizadas com sucesso!')
            return redirect('categorias')
        else:
            messages.error(request, 'Não foi possível realizar a edição. Favor revise os dados ou entre em contato com o administrador do sistema.')

    return render(request, 'atividades/editar_categoria.html', {'forms':forms, 'categoria':categoria})

def deletar_categoria(request, categoria_id):

    """
    View que deleta a instância do modelo Categoria relativa ao parâmetro 'categoria_id'.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    categoria_id: int
        ID da instância que deverá ser deletada no modelo Categoria.

    Retorno:
    --------
    redirect
        Redireciona o usuário para a path 'categorias' exibindo uma mensagem de sucesso na deleção da instância.
    """

    categoria = Categoria.objects.get(id=categoria_id)

    categoria.delete()

    messages.success(request, 'Deleção realizada com sucesso!')
    return redirect('categorias')

def get_valor_fixo(request, instituicao_id):

    """
    View que obtém o valor do campo 'valor_fixo' da instituição relativa ao parâmetro 'instituicao_id'.

    Essa função é chamada no momento em que o usuário indica que determinada atividade deve integrar um valor fixo pago por determinada instituição, clicando no checkbox 'Fixo Mensal' do formulário de cadastro de novas atividades.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).
    instituicao_id: int
        ID da instância do modelo Instituicao que será usado como referência.

    Retorno:
    --------
    JsonResponse
        Retorna o campo 'valor_fixo' da instituição relativa ao parâmetro 'instituicao_id'.

    Tratamento de erros:
    --------
    - Caso a instituição referência pelo parâmento 'instituicao_id' não exista, a função retorna um JsonResponse com o 'valor_padrao' vazio e o erro de status=404.

    """

    try:

        instituicao = Instituicao.objects.get(id=instituicao_id)
        valor_fixo = instituicao.valor_fixo
        return JsonResponse({'valor_fixo': valor_fixo})
    
    except Instituicao.DoesNotExist:

        return JsonResponse({'valor_padrao': ''}, status=404)

def get_data_max(request):

    """
    View que obtém a data máxima disponível no calenário do sistema

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    JsonResponse
        Retorna o campo 'data_max' que é a data máxima disponível no calendário do sistema.

    Tratamento de erros:
    --------
    - Caso ainda não haja datas disponíveis no modelo calendário, a função retorna o dia de hoje.

    """

    data_ref = Calendario.objects.order_by('-dia').first()

    if data_ref:  
        data_max = data_ref.dia

        return JsonResponse({'data_max': data_max})
    
    else:
        data_max = date.today()

        return JsonResponse({'data_max': data_max})
    
def filtrar_financeiro(atividades):

    """
    View que gera dicionário com os dados da QuerySet atividades, enviada como parâmetro, filtrados e formatados para apresentação no dashboard Financeiro.

    Parâmetros:
    -----------
    atividades: QuerySet
        Query com instâncias do modelo 'Atividades' que foram previamente filtradas.

    Retorno:
    --------
    dict
        Dicionário contendo os seguintes contextos:
        - 'dict_financ': Dicionário com dados da QuerySet atividades devidamente formatados e filtrados para apresentação no DashBoard Financeiro.
        - 'etiquetas': Lista contendo os valores que serão usados como labels no gráfico padrão, obtido pela Função 'gerar_grafico_instituicao'.
        - 'valores': Lista contendo os valores que serão usados para montar o gráfico padrão, obtido pela Função 'gerar_grafico_instituicao'. 

    Funcionamento:
    --------
    - Obtém quantidade de meses transcorridos no período referênte as atividades presentes no parâmetro 'atividades'.
    - Declara as variáves que serão necessárias no decorrer do código.
    - Usa Função 'gerar_grafico_instituicao' para obter valores necessários para a geração de gráfico padrão. E separa o resultado em suas devidas variáveis.
    - Percorre a QuerySet 'atividades' unificando e formatando os valores das atividades dentro do dicionário 'dict_financ'.
    - Checa se a atividade percorrida tem True para o campo 'fixo_mensal_ativ'.
    - Caso sim, garante o valor da atividade será somado apenas uma vez por mes no período referente as atividades.
    - Caso não, efetua as somas normalmente.

    Tratamento de erros:
    --------
    - Caso a QuerySet atividades enviada esteja vazia a função preenche os campos de 'dict_financ' e as variaveis 'etiquetas' e 'valores' com em branco para declara-las e evitar erros futuros na manipulação das mesmas.
    - Se o o campo valor estiver vazio, ele insere 0 para evitar erro de conversão.

    Notas:
    --------
    - A Função garante que atividade 'quebradas' por passarem da meia-noite sejam tratadas de maneira unificada.
    """

    dict_financ = {}

    if atividades:

        # Obtem quantidade de meses
        data_inicio = atividades.order_by('data').first()
        data_inicio = data_inicio.data
        data_final = atividades.order_by('data').last()
        data_final = data_final.data
        qt_meses = (data_final.month + 1) - data_inicio.month

        total = 0
        total_fixo = 0
        total_variavel = 0
        qt_atividade = 0
        qt_hora = 0
        list_dia_trab = []
        list_mes = []
        list_id_vir = []
        list_fixo = []

        # Obtem dados para gerar gráfico
        dict_inst = gerar_grafico_instituicao(atividades, qt_meses)
        lista_etiqueta = list(dict_inst.keys())
        lista_valores = list(dict_inst.values())

        for atividade in atividades:

            # Garante um incidência por mês em valores fixos
            if atividade.fixo_mensal_ativ:
                if atividade.id_vir not in list_id_vir:
                    list_id_vir.append(atividade.id_vir)       

                if atividade.cod_fixo_ativ not in list_fixo:
                    total_fixo += float(atividade.valor)
                    list_fixo.append(atividade.cod_fixo_ativ)
            else:
                if atividade.id_vir not in list_id_vir:
                    list_id_vir.append(atividade.id_vir)

                    if atividade.valor:  # Caso valor seja vazio, adiciona zero para evitar erro de conversão
                        total_variavel += float(atividade.valor)
                    else:
                        total_variavel += 0

            # Checa virada de dia para tratar quantidade de horas
            if atividade.entrada < atividade.saida:
                qt_hora += (atividade.saida - atividade.entrada)
            else:
                qt_hora += ((24 - atividade.entrada) + atividade.saida)

            if atividade.data not in list_dia_trab:
                list_dia_trab.append(atividade.data)

            if atividade.data.month not in list_mes:
                list_mes.append(atividade.data.month)
        
        qt_atividade = len(list_id_vir)

        # Calcula o total de fixos mensais multiplicando pela quantidade de meses
        total_fixo = total_fixo * qt_meses

        # Gerar o total faturado no período entre fixos e variaveis
        total = total_fixo + total_variavel

        # Gera o dicionario com os valores já formatados
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

        # Garante a existencia das variaveis caso o retorno da função de geração de gráfico seja nulo
        lista_etiqueta = ''
        lista_valores = ''

    return {'dict_financ': dict_financ, 'etiquetas': lista_etiqueta, 'valores': lista_valores}

def filtrar_mes(mes):

    """
    View que filtra os objetos do modelo Atividades pelo parâmetro 'mes'.
    
    Em seguida, envia o resultado para a função 'filtrar_financeiro' à fim de obter os dados formatados para o dashboard Financeiro.

    Parâmetros:
    -----------
    mes : int
        Mês pelo qual se filtrará os objetos do modelo Atividades.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta com as instâncias do modelo Atividades filtradas pelo parâmetro 'mes', contendo os seguintes contextos:
        - 'dict_financ': Dicionário com os dados para uso no dashboard Financeiro.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_financeiro' para obter os dados formatados.
    """

    atividades = Atividades.objects.filter(data__month=mes, nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_ano(ano):

    """
    View que filtra os objetos do modelo Atividades pelo parâmetro 'ano'.
    
    Em seguida, envia o resultado para a função 'filtrar_financeiro' à fim de obter os dados formatados para o dashboard Financeiro.

    Parâmetros:
    -----------
    ano : int
        Ano pelo qual se filtrará os objetos do modelo Atividades.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta com as instâncias do modelo Atividades filtradas pelo parâmetro 'ano', contendo os seguintes contextos:
        - 'dict_financ': Dicionário com os dados para uso no dashboard Financeiro.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_financeiro' para obter os dados formatados.
    """

    atividades = Atividades.objects.filter(data__year=ano, nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_ate_fim_mes():

    """
    View que filtra os objetos do modelo Atividades tendo como referência a data atual até o último dia do mês atual.
    
    Em seguida, envia o resultado para a função 'filtrar_financeiro' à fim de obter os dados formatados para o dashboard Financeiro.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta com as instâncias do modelo Atividades filtradas pelo período da data_atual até o último dia do mês atual, contendo os seguintes contextos:
        - 'dict_financ': Dicionário com os dados para uso no dashboard Financeiro.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_financeiro' para obter os dados formatados.
    """

    data_inicio = datetime.today().date()
    ano = data_inicio.year
    mes = data_inicio.month
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_final = datetime(ano, mes, ultimo_dia).date()

    atividades = Atividades.objects.filter(data__range=(data_inicio, data_final), nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_ate_fim_ano():

    """
    View que filtra os objetos do modelo Atividades tendo como referência a data atual até o último dia do ano atual.
    
    Em seguida, envia o resultado para a função 'filtrar_financeiro' à fim de obter os dados formatados para o dashboard Financeiro.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta com as instâncias do modelo Atividades filtradas pelo período da data_atual até o último dia do ano atual, contendo os seguintes contextos:
        - 'dict_financ': Dicionário com os dados para uso no dashboard Financeiro.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_financeiro' para obter os dados formatados.
    """

    data_inicio = datetime.today().date()
    ano = data_inicio.year
    data_final = datetime(ano, 12, 31).date()    

    atividades = Atividades.objects.filter(data__range=(data_inicio, data_final), nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_todo_periodo():

    """
    View que obtem todos os objetos do modelo Atividades, exceto os não remunerados, e os envia para a função 'filtrar_financeiro' à fim de obter os dados formatados para o dashboard Financeiro.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta todas as instâncias do modelo Atividades, exceto as não remuneradas, contendo os seguintes contextos:
        - 'dict_financ': Dicionário com os dados para uso no dashboard Financeiro.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_financeiro' para obter os dados formatados.
    """

    atividades = Atividades.objects.filter(nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def filtrar_personalizado(dataInicio, dataFinal):

    """
    View que filtra os objetos do modelo Atividades no período entre os parâmetros 'dataInicio' e 'dataFinal'.
    
    Em seguida, envia o resultado para a função 'filtrar_financeiro' à fim de obter os dados formatados para o dashboard Financeiro.

    Parâmetros:
    -----------
    dataInicio : datetime
        Data de inicio do período que o usuário deseja filtrar as informações.
    dataFinal : datetime
        Data de término do período que o usuário deseja filtrar as informações.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta com as instâncias do modelo Atividades filtradas pelo período entre os parâmetros 'dataInicio' e 'dataFinal', contendo os seguintes contextos:
        - 'dict_financ': Dicionário com os dados para uso no dashboard Financeiro.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_financeiro' para obter os dados formatados.
    """

    atividades = Atividades.objects.filter(data__range=(dataInicio, dataFinal), nao_remunerado=False)

    dict_financ = filtrar_financeiro(atividades)

    return dict_financ

def gerar_grafico_instituicao(atividades, qt_meses):

    """
    View que gera um dicionário a partir da queryset atividades enviada como parâmetro. 
    
    A Função agrupa os valores recebidos por instituição no período transcorrido entre as atividades do parâmetro 'atividades'.
    Cada instituição vira uma chave no dicionário sendo que seu valor será o total recebido por ela nesse período.

    Parâmetros:
    -----------
    atividades : QuerySet
        Query com instâncias do modelo 'Atividades' que foram previamente filtradas.
    qt_meses : int
        Número que representa a quantidade de meses transcorridos no período entre as atividades da query 'atividades'.

    Retorno:
    --------
    dict
        Retorna um dicionário com total dos valores recebidos por instituição dentre as atividades presentes na query 'atividades'.  

    Tratamento de erros:
    --------
    - Caso haja erro de conversão dos valores para o tipo float, a função adiciona 0 ao campo prevendo erros futuros.

    Notas:
    --------
    - As chaves dessa função formarão as labels para geração do gráfico financeiro por instituição.
    - Os valores dessa função serão os valores para a geração do gráfico financeiro por instituição.
    - A Função trata atividades 'quebradas' por passarem da meia-noite de maneira unificada.
    - A Função garante que valores fixos sejam somados apenas uma vez a cada mes.
    """

    dict_inst = {}
    list_cod_fixo = []
    list_id_vir = []
    
    for atividade in atividades:
        nome_inst = atividade.instituicao.nome_inst

        if atividade.id_vir not in list_id_vir:
            list_id_vir.append(atividade.id_vir)

            if nome_inst not in dict_inst:
                dict_inst[nome_inst] = 0

            if atividade.fixo_mensal_ativ:
                if atividade.cod_fixo_ativ not in list_cod_fixo:
                    valor = float(atividade.valor) * qt_meses
                    dict_inst[nome_inst] += valor
                    list_cod_fixo.append(atividade.cod_fixo_ativ)
            else:
                try:
                    dict_inst[nome_inst] += float(atividade.valor)
                except ValueError:
                    dict_inst[nome_inst] += 0  # Adiciona 0 caso ocorra um erro de conversão
    
    return dict_inst

def gerar_grafico_tipo(atividades, qt_meses) :

    """
    View que gera um dicionário a partir da queryset atividades enviada como parâmetro. 
    
    A Função agrupa os valores recebidos por 'tipo de atividade' no período transcorrido entre as atividades do parâmetro 'atividades'.
    Cada tipo de atividade vira uma chave no dicionário sendo que seu valor será o total recebido por ela nesse período.

    Parâmetros:
    -----------
    atividades : QuerySet
        Query com instâncias do modelo 'Atividades' que foram previamente filtradas.
    qt_meses : int
        Número que representa a quantidade de meses transcorridos no período entre as atividades da query 'atividades'.

    Retorno:
    --------
    dict
        Retorna um dicionário com total dos valores recebidos por tipo de atividade dentre as atividades presentes na query 'atividades'.  

    Tratamento de erros:
    --------
    - Caso haja erro de conversão dos valores para o tipo float, a função adiciona 0 ao campo prevendo erros futuros.

    Notas:
    --------
    - As chaves dessa função formarão as labels para geração do gráfico financeiro por tipo de atividade.
    - Os valores dessa função serão os valores para a geração do gráfico financeiro por tipo de atividade.
    - A Função trata atividades 'quebradas' por passarem da meia-noite de maneira unificada.
    - A Função garante que valores fixos sejam somados apenas uma vez a cada mes.
    """

    dict_tipo = {}
    list_cod_fixo = []
    list_id_vir = []

    for atividade in atividades:
        nome_tipo = atividade.tipo_atividade.nome_tipo

        if atividade.id_vir not in list_id_vir:
            list_id_vir.append(atividade.id_vir)

            if nome_tipo not in dict_tipo:
                dict_tipo[nome_tipo] = 0

            if atividade.fixo_mensal_ativ:
                if atividade.cod_fixo_ativ not in list_cod_fixo:
                    valor = float(atividade.valor) * qt_meses
                    dict_tipo[nome_tipo] += valor
                    list_cod_fixo.append(atividade.cod_fixo_ativ)
            else:
                try:
                    dict_tipo[nome_tipo] += float(atividade.valor)
                except ValueError:
                    dict_tipo[nome_tipo] += 0  # Adicionar 0 caso ocorra erro na conversão

    return dict_tipo

def gerar_grafico_mes(atividades) :

    """
    View que gera um dicionário a partir da queryset atividades enviada como parâmetro. 
    
    A Função agrupa os valores recebidos por mês no período transcorrido entre as atividades do parâmetro 'atividades'.
    Cada mês vira uma chave no dicionário sendo que seu valor será o total recebido por ela nesse período.

    Parâmetros:
    -----------
    atividades : QuerySet
        Query com instâncias do modelo 'Atividades' que foram previamente filtradas.

    Retorno:
    --------
    dict
        Retorna um dicionário com total dos valores recebidos por mês dentre as atividades presentes na query 'atividades'.  

    Tratamento de erros:
    --------
    - Caso haja erro de conversão dos valores para o tipo float, a função adiciona 0 ao campo prevendo erros futuros.

    Notas:
    --------
    - As chaves dessa função formarão as labels para geração do gráfico financeiro por mês.
    - Os valores dessa função serão os valores para a geração do gráfico financeiro por mês.
    - A Função trata atividades 'quebradas' por passarem da meia-noite de maneira unificada.
    - A Função garante que valores fixos sejam somados apenas uma vez a cada mes.
    """

    dict_mes = {}
    list_id_vir = []
    list_Control = []

    for atividade in atividades:
        mes = atividade.data.month
        control = f'{atividade.cod_fixo_ativ} - {mes}'
        nome_mes = gerar_mes(atividade.data)

        if atividade.id_vir not in list_id_vir:
            list_id_vir.append(atividade.id_vir)

            if nome_mes not in dict_mes:
                dict_mes[nome_mes] = 0

            if atividade.fixo_mensal_ativ:
                if control not in list_Control:
                    dict_mes[nome_mes] += float(atividade.valor)
                    list_Control.append(control)
            else:
                try:
                    dict_mes[nome_mes] += float(atividade.valor)
                except ValueError:
                    dict_mes[nome_mes] += 0  # Adicionar 0 caso ocorra erro na conversão
        
    return dict_mes
    
def financeiro(request):

    """
    View que renderiza o template 'atividades/financeiro.html' com suas informações pertinentes para a exibição do dashboad Financeiro.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'atividades/financeiro.html' com dicionário contento os seguintes contextos:
        - 'dict_financ': Dicionário com os dados financeiros referente ao mês atual, filtrados e formatados para a exibição no dashboard Financeiro.
        - 'etiquetas': Lista convertida para JSON com os rótulos (labels) para geração do gráfico financeiro por instituição.
        - 'valores': Lista convertida para JSON com os valores para geração do gráfico financeiro por instituição.
        - 'tipo': String convertida para JSON com o tipo de gráfico definido nas preferências do usuário.

    Notas:
    --------
    - Recupera as preferências do usuário a partir do modelo Preferencias.
    - Usa a função 'filtrar_mes' enviando o mês atual de parâmetro para obter demais dados.
    """

    mes = datetime.today().month

    preferencias = get_preferencias()
    tipo = preferencias['tipo_grafico']        

    dict_financ = filtrar_mes(mes)

    etiquetas = dict_financ['etiquetas']
    valores = dict_financ['valores']
    dict_financ = dict_financ['dict_financ']

    return render(request, 'atividades/financeiro.html', {'financeiro': dict_financ, 'etiquetas': json.dumps(etiquetas), 'valores': json.dumps(valores), 'tipo': json.dumps(tipo)})

@require_GET
def atualizar_financeiro(request):

    """
    View que atualiza os dados do dashboard Financeiro a partir de uma requição AJAX contento os parâmetros solicitados pelo usuário.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    JsonResponse
        Retorna um JSON contendo o HTML atualizado do template 'atividades/partials/base_financeiro.html' com um dicionário contento os seguintes contextos:
        - 'dict_financ': Dicionário com os dados financeiros formatados e filtrados conforme parâmetros enviados pelo usuário.
        - 'etiquetas': Lista com os rótulos (labels) para geração do gráfico financeiro por instituição.
        - 'valores': Lista com os valores para geração do gráfico financeiro por instituição.
        - 'tipo': String com o tipo de gráfico definido nas preferências do usuário.

    Funcionamento:
    --------
    - A função verifica se a requisição é uma requisição AJAX, através do cabeçalho 'X-Requested-With'.
    - Obtém o tipo de período selecionado pelo usuário.
    - Checar qual tipo de período e obtém os demais parâmetros para chamar a função relativa ao período selecionado. A Função retornará o 'dict_financ' que é o dicionário com os contextos necessários para a atualização da página.
    - Divide o 'dict_financ' em suas devidas variáveis e recupera as preferências de usuário para obter o tipo do gráfico.
    - Renderiza o template 'atividades/partials/base_financeiro.html' com os dados.

    Tratamento de erros:
    --------
    - Caso não seja um requisição AJAX, retorna erro 'Requisição Inválida' (HTTP 400).
    - Se o a informação fornecida no parâmetro `periodoSelect` for inválida, retorna um erro 'Data inválida' (HTTP 400).
    - Caso o período selecionado for o 'personalizado' (periodoSelect == 6), a função formatará a data para o formatado %Y-%m-%d, caso haja erro na formatação retornará o erro 'Formato de data inválido. Use YYYY-MM-DD.' (HTTP 400).
    - Se houver erro na Função usada para gerar o dicionário 'dict_financ' a função retornará 'Não foi possível gerar dict_financeiro a partir do período selecionado'. (HTTP 404)
    
    """

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
            
            preferencias = Preferencias.objects.get(id=1)
            tipo = preferencias.tipo_grafico
        else:       
            return JsonResponse({'error': 'Não foi possível gerar dict_financeiro a partir do período selecionado'}, status=404)

        try:
            
            html_content = render_to_string('atividades/partials/base_financeiro.html', {'financeiro': dict_financ, 'etiquetas': etiquetas, 'valores': valores, 'tipo': tipo})
        except Exception as e:
            return JsonResponse({'error': f'Erro ao renderizar o template: {str(e)}'}, status=500)

        return JsonResponse({'html': html_content, 'etiquetas': etiquetas, 'valores': valores, 'tipo': tipo})
    else:
        return JsonResponse({'error': 'Requisição inválida'}, status=400)
    
@require_GET
def atualizar_grafico(request):

    """
    View que atualiza os dados para a geração do gráfico do dashboard Financeiro a partir de uma requição AJAX contento os parâmetros solicitados pelo usuário.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    JsonResponse
        Retorna um JSON contendo com um dicionário contento os seguintes contextos:
        - 'etiquetas': Lista com os rótulos (labels) para geração do gráfico.
        - 'valores': Lista com os valores para geração do gráfico.
        - 'tipo': String com o tipo de gráfico definido nas preferências do usuário.

    Funcionamento:
    --------
    - A função verifica se a requisição é uma requisição AJAX, através do cabeçalho 'X-Requested-With'.
    - Obtém o tipo de período e o gráfico desejado selecionado pelo usuário.
    - Checar qual tipo de período e obtém os demais parâmetros para filtrar as instâncias do modelo Atividades de acordo com o período selecionado.
    - Obtém a quantidade de meses transcorridas entre as atividades da query 'atividades'.
    - Com a query 'atividades' e a quantidade de meses, a Função checa qual o gráfico solicitado pelo usuário através da variável 'graficoSelect' e chama a função de geração de gráfico de acordo com o que foi selecionado. A Função será retornada para o dicionário 'dict_financ'.
    - Divide o 'dict_financ' em suas devidas variáveis e recupera as preferências de usuário para obter o tipo do gráfico.

    Tratamento de erros:
    --------
    - Caso a requisição não seja uma requisição AJAX, retorna o erro 'Requisição Inválida' (HTTP 400).
    - Se a informação fornecida no parâmetro `periodoSelect` for inválida, retorna um erro 'Data inválida' (HTTP 400).
    - Caso o período selecionado for o 'personalizado' (periodoSelect == 6), a função formatará a data para o formatado %Y-%m-%d, caso haja erro na formatação retornará o erro 'Formato de data inválido. Use YYYY-MM-DD.' (HTTP 400).
    - Se a query 'atividades' retornar vazia, o dicionário 'dict_financ' é preenchido com valor nulo para prevenção de erro em manipulações futuras.
    - Se a informação fornecida no parâmetro 'graficoSelect' for inválida, retorna um erro 'Erro ao gerar o gráfico' (HTTP 400).
    - Se houver erro na Função usada para gerar o dicionário 'dict_financ' a função retornará 'Não foi possível gerar dict_financeiro a partir do período selecionado' (HTTP 404)
    
    """

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
        
        if atividades:
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
                return JsonResponse({'error': 'Erro ao gerar o gráfico'}, status=400)
        else:
            
            dict_financ = {
                '':''
            }
        
        if dict_financ:
            
            etiquetas = list(dict_financ.keys())
            valores = list(dict_financ.values())
            
            preferencias = Preferencias.objects.get(id=1)
            tipo = preferencias.tipo_grafico
        else:       
            return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

        return JsonResponse({'etiquetas': etiquetas, 'valores': valores, 'tipo': tipo})
    else:
        return JsonResponse({'error': 'Requisição inválida'}, status=400)
    
def filtrar_rotina(atividades, quant_dias):

    """
    View que gera dicionário com os dados da QuerySet atividades, enviada como parâmetro, filtrados e formatados para apresentação no dashboard Rotina.

    Parâmetros:
    -----------
    atividades: QuerySet
        Query com instâncias do modelo 'Atividades' que foram previamente filtradas.
    quant_dias: int
        Quantidade de dias que transcorrerão no período entre as atividades presentes na queryset 'atividades'.

    Retorno:
    --------
    dict
        Dicionário contendo os seguintes contextos:
        - 'dict_rotina': Dicionário com dados da QuerySet atividades devidamente formatados e filtrados para apresentação no DashBoard Rotina.
        - 'etiquetas': Lista contendo os valores que serão os rótulos (labels) no gráfico padrão, obtido pela Função 'gerar_grafico_remuneracao_rotina'.
        - 'valores': Lista contendo os valores que serão usados para montar o gráfico padrão, obtido pela Função 'gerar_grafico_remuneracao_rotina'. 

    Funcionamento:
    --------
    - Obtém quantidade de horas totais e quantidade de semanas a partir da variável 'quant_dias'.
    - Recupera preferências do usuário para obter quantidade de horas de sono no período transcorrido entra as atividades presentes na queryset 'atividades'.
    - Declara as variáves que serão necessárias no decorrer do código.
    - Usa Função 'gerar_grafico_remuneracao_rotina para obter valores necessários para a geração de gráfico padrão. E separa o resultado em suas devidas variáveis.
    - Percorre a QuerySet 'atividades' unificando e formatando os valores das atividades dentro do dicionário 'dict_rotina'.

    Tratamento de erros:
    --------
    - Caso a QuerySet atividades enviada esteja vazia a função preenche os campos de 'dict_rotina' e as variaveis 'etiquetas' e 'valores' com valores nulos e em branco para declara-las e evitar erros futuros na manipulação das mesmas.

    Notas:
    --------
    - A Função garante que atividade 'quebradas' por passarem da meia-noite sejam contabilizadas como apenas ' atividade.
    - A Função retorna número de horas de atividades remuneradas e não remuneradas.
    """

    dict_rotina = {}

    quant_horas_totais = quant_dias*24
    quant_semanas = quant_dias // 7 if (quant_dias // 7) > 0 else 1
    
    preferencias = get_preferencias()
    horas_sono = preferencias['horas_sono']
    quant_horas_sono = horas_sono * quant_dias

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

            qt_hora_livre = quant_horas_totais - (qt_hora + quant_horas_sono)
            qt_atividade = len(list_id_vir)

        dict_rotina['rotina'] = {
            'horas_atividade': qt_hora,
            'horas_livres': qt_hora_livre,
            'qt_atividade': qt_atividade,
            'media_hr_trab_sem': f'{round(qt_hora_remu / quant_semanas)} horas',
            'media_hr_ativ_sem': f'{round(qt_hora / quant_semanas)} horas',
            'media_hr_livre_sem': f'{round(qt_hora_livre / quant_semanas)} horas',
            'media_hr_trab_dia': f'{round(qt_hora_remu / quant_dias)} horas',
            'media_hr_ativ_dia': f'{round(qt_hora / quant_dias)} horas',
            'media_hr_livre_dia': f'{round(qt_hora_livre / quant_dias)} horas',
            'media_hr_ativ': f'{round(qt_hora / qt_atividade) if qt_atividade else 0} horas'
        }
    else:
        dict_rotina['rotina'] = {
            'horas_atividade': qt_hora,
            'horas_livres': qt_hora_livre - quant_horas_sono,
            'qt_atividade': qt_atividade,
            'media_hr_trab_sem': f'0 horas',
            'media_hr_ativ_sem': f'0 horas',
            'media_hr_livre_sem': f'{round((qt_hora_livre - quant_horas_sono) / quant_semanas)} horas',
            'media_hr_trab_dia': f'0 horas',
            'media_hr_ativ_dia': f'0 horas',
            'media_hr_livre_dia': f'{round((qt_hora_livre - quant_horas_sono) / quant_dias)} horas',
            'media_hr_ativ': f'0 horas'
        }

    return {'dict_rotina': dict_rotina, 'etiquetas': lista_etiqueta, 'valores': lista_valores}

def filtrar_mes_rotina(mes):

    """
    View que filtra os objetos do modelo Atividades pelo parâmetro 'mes'.
    
    Em seguida, envia o resultado para a função 'filtrar_rotina' à fim de obter os dados formatados para o dashboard Rotina.

    Parâmetros:
    -----------
    mes : int
        Mês pelo qual se filtrará os objetos do modelo Atividades.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta com as instâncias do modelo Atividades filtradas pelo parâmetro 'mes', contendo os seguintes contextos:
        - 'dict_rotina': Dicionário com os dados para uso no dashboard Financeiro.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_rotina' para obter os dados formatados.
    """

    atividades = Atividades.objects.filter(data__month=mes)

    quant_dias = calendar.monthrange(datetime.today().year, mes)[1]

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def filtrar_ano_rotina(ano):

    """
    View que filtra os objetos do modelo Atividades pelo parâmetro 'ano'.
    
    Em seguida, envia o resultado para a função 'filtrar_rotina' à fim de obter os dados formatados para o dashboard Rotina.

    Parâmetros:
    -----------
    ano : int
        Ano pelo qual se filtrará os objetos do modelo Atividades.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta com as instâncias do modelo Atividades filtradas pelo parâmetro 'ano', contendo os seguintes contextos:
        - 'dict_rotina': Dicionário com os dados para uso no dashboard Rotina.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_rotina' para obter os dados formatados.
    """

    atividades = Atividades.objects.filter(data__year=ano)

    data_inicio = datetime(ano, 1, 1).date()
    data_final = datetime(ano, 12, 31).date()

    diferenca = data_final - data_inicio
    quant_dias = diferenca.days

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def filtrar_ate_fim_mes_rotina():

    """
    View que filtra os objetos do modelo Atividades tendo como referência a data atual até o último dia do mês atual.
    
    Em seguida, envia o resultado para a função 'filtrar_rotina' à fim de obter os dados formatados para o dashboard Rotina.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta com as instâncias do modelo Atividades filtradas pelo período da data_atual até o último dia do mês atual, contendo os seguintes contextos:
        - 'dict_rotina': Dicionário com os dados para uso no dashboard Rotina.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_rotina' para obter os dados formatados.
    """

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

    """
    View que filtra os objetos do modelo Atividades tendo como referência a data atual até o último dia do ano atual.
    
    Em seguida, envia o resultado para a função 'filtrar_rotina' à fim de obter os dados formatados para o dashboard Rotina.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta com as instâncias do modelo Atividades filtradas pelo período da data_atual até o último dia do ano atual, contendo os seguintes contextos:
        - 'dict_rotina': Dicionário com os dados para uso no dashboard Rotina.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_rotina' para obter os dados formatados.
    """

    data_inicio = datetime.today().date()
    ano = data_inicio.year
    data_final = datetime(ano, 12, 31).date()

    diferenca = data_final - data_inicio
    quant_dias = diferenca.days    

    atividades = Atividades.objects.filter(data__range=(data_inicio, data_final))

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def filtrar_todo_periodo_rotina():

    """
    View que obtem todos os objetos do modelo Atividades e os envia para a função 'filtrar_rotina' à fim de obter os dados formatados para o dashboard Rotina.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta todas as instâncias do modelo Atividades, contendo os seguintes contextos:
        - 'dict_rotina': Dicionário com os dados para uso no dashboard Rotina.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_rotina' para obter os dados formatados.
    """

    atividades = Atividades.objects.all()

    atividades_datas = Atividades.objects.order_by('data')
    data_inicio = atividades_datas.first().data
    data_final = atividades_datas.last().data

    diferenca = data_final - data_inicio
    quant_dias = diferenca.days

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def filtrar_personalizado_rotina(dataInicio, dataFinal):

    """
    View que filtra os objetos do modelo Atividades no período entre os parâmetros 'dataInicio' e 'dataFinal'.
    
    Em seguida, envia o resultado para a função 'filtrar_rotina' à fim de obter os dados formatados para o dashboard Rotina.

    Parâmetros:
    -----------
    dataInicio : datetime
        Data de inicio do período que o usuário deseja filtrar as informações.
    dataFinal : datetime
        Data de término do período que o usuário deseja filtrar as informações.

    Retorno:
    --------
    dict
        Retorna um dicionário criado a partir dos dados da QuerySet 'atividades', que conta com as instâncias do modelo Atividades filtradas pelo período entre os parâmetros 'dataInicio' e 'dataFinal', contendo os seguintes contextos:
        - 'dict_rotina': Dicionário com os dados para uso no dashboard Rotina.
        - 'etiquetas': Lista com valores para serem usados como label na geração do gráfico padrão.
        - 'valores': Lista com valores para serem usados na geração do gráfico padrão. 

    Notas:
    --------
    - A Função exclui todas as atividades não remuneradas.
    - Usa a Função 'filtrar_rotina' para obter os dados formatados.
    """

    atividades = Atividades.objects.filter(data__range=(dataInicio, dataFinal))

    data_inicio = datetime.strptime(dataInicio, '%Y-%m-%d').date()
    data_final = datetime.strptime(dataFinal, '%Y-%m-%d').date()

    diferenca = data_final - data_inicio
    quant_dias = diferenca.days

    dict_rotina = filtrar_rotina(atividades, quant_dias)

    return dict_rotina

def gerar_grafico_remuneracao_rotina(atividades) :

    """
    View que gera um dicionário a partir da queryset atividades enviada como parâmetro. 
    
    A Função agrupa as horas de atividade por remuneradas ou não remuneradas, percorrendo todos as instâncias do parâmetro 'atividades'.

    Parâmetros:
    -----------
    atividades : QuerySet
        Query com instâncias do modelo 'Atividades' que foram previamente filtradas.
    
    Retorno:
    --------
    dict
        Retorna um dicionário com total de horas de atividades as agrupando nas chaves 'remuneradas' e 'não remuneradas'.  

    Notas:
    --------
    - As chaves dessa função formarão as labels para geração do gráfico rotina por remuneração.
    - Os valores dessa função serão os valores para a geração do gráfico rotina por remuneração.
    """

    dict_remu = {}
    horas_remu = 0
    horas_nr = 0

    if atividades:
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

    """
    View que gera um dicionário a partir da queryset atividades enviada como parâmetro. 
    
    A Função agrupa as horas de atividade por tipo de atividade, percorrendo todos as instâncias do parâmetro 'atividades'.

    Parâmetros:
    -----------
    atividades : QuerySet
        Query com instâncias do modelo 'Atividades' que foram previamente filtradas.
    
    Retorno:
    --------
    dict
        Retorna um dicionário com total de horas de atividades agrupadas por tipo de atividades.  

    Notas:
    --------
    - As chaves dessa função formarão as labels para geração do gráfico rotina por tipo de atividade.
    - Os valores dessa função serão os valores para a geração do gráfico rotina por tipo de atividade.
    """

    dict_tipo = {}
    horas = 0

    if atividades:
        for atividade in atividades:

            if atividade.entrada < atividade.saida:
                horas = atividade.saida - atividade.entrada
            else:
                horas = ((24 - atividade.entrada) + atividade.saida)

            nome_tipo = atividade.tipo_atividade.nome_tipo

            if nome_tipo not in dict_tipo:
                dict_tipo[nome_tipo] = 0
            
            dict_tipo[nome_tipo] += horas

    return dict_tipo

def gerar_grafico_categoria_rotina(atividades):

    """
    View que gera um dicionário a partir da queryset atividades enviada como parâmetro. 
    
    A Função agrupa as horas de atividade por categoria, percorrendo todos as instâncias do parâmetro 'atividades'.

    Parâmetros:
    -----------
    atividades : QuerySet
        Query com instâncias do modelo 'Atividades' que foram previamente filtradas.
    
    Retorno:
    --------
    dict
        Retorna um dicionário com total de horas de atividades agrupadas por categoria.  

    Notas:
    --------
    - As chaves dessa função formarão as labels para geração do gráfico rotina por categoria.
    - Os valores dessa função serão os valores para a geração do gráfico rotina por categoria.
    """

    dict_categoria = {}
    horas = 0

    if atividades:

        for atividade in atividades:

            if atividade.entrada < atividade.saida:
                horas = atividade.saida - atividade.entrada
            else:
                horas = ((24 - atividade.entrada) + atividade.saida)

            nome_categoria = atividade.tipo_atividade.categoria.nome_categoria

            if nome_categoria not in dict_categoria:
                dict_categoria[nome_categoria] = 0
            
            dict_categoria[nome_categoria] += horas

    return dict_categoria

def gerar_grafico_ocupacao_rotina(atividades, quant_horas_totais, qt_horas_sono):

    """
    View que gera um dicionário a partir da queryset atividades enviada como parâmetro. 
    
    A Função agrupa as horas de atividade por horas ocupadas e horas livres, percorrendo todos as instâncias do parâmetro 'atividades'.

    Parâmetros:
    -----------
    atividades : QuerySet
        Query com instâncias do modelo 'Atividades' que foram previamente filtradas.
    quant_horas_totais : int
        Quantidade de horas de atividades do período transcorrido entre as atividades presentes na queryset 'atividades'
    qt_horas_sono : int
        Quantidade de horas de sono recuperadas do modelo Preferencias relativo às preferências do usuário.
    
    Retorno:
    --------
    dict
        Retorna um dicionário com total de horas de atividades agrupadas por horas ocupadas e horas livres.  

    Notas:
    --------
    - As chaves dessa função formarão as labels para geração do gráfico rotina por ocupação.
    - Os valores dessa função serão os valores para a geração do gráfico rotina por ocupação.
    """

    dict_ocupacao = {}

    dict_ocupacao['Horas Ocupadas'] = 0
    dict_ocupacao['Horas Livres'] = quant_horas_totais - qt_horas_sono

    if atividades:

        for atividade in atividades:

            if atividade.entrada < atividade.saida:
                horas = atividade.saida - atividade.entrada
            else:
                horas = ((24 - atividade.entrada) + atividade.saida)

            dict_ocupacao['Horas Ocupadas'] += horas
            dict_ocupacao['Horas Livres'] -= horas

    return dict_ocupacao

def rotina(request):

    """
    View que renderiza o template 'atividades/rotina.html' com suas informações pertinentes para a exibição do dashboad Rotina.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'atividades/rotina.html' com dicionário contento os seguintes contextos:
        - 'dict_rotina': Dicionário com os dados de rotina referente ao mês atual, filtrados e formatados para a exibição no dashboard Rotina.
        - 'etiquetas': Lista convertida para JSON com os rótulos (labels) para geração do gráfico rotina por remuneração.
        - 'valores': Lista convertida para JSON com os valores para geração do gráfico rotina por remuneração.
        - 'tipo': String convertida para JSON com o tipo de gráfico definido nas preferências do usuário.

    Notas:
    --------
    - Recupera as preferências do usuário a partir do modelo Preferencias.
    - Usa a função 'filtrar_mes_rotina' enviando o mês atual de parâmetro para obter demais dados.
    """

    mes = datetime.today().month        

    dict_rotina = filtrar_mes_rotina(mes)

    preferencias = get_preferencias()
    tipo = preferencias['tipo_grafico']

    etiquetas = dict_rotina['etiquetas']
    valores = dict_rotina['valores']
    dict_rotina = dict_rotina['dict_rotina']

    return render(request, 'atividades/rotina.html', {'rotina': dict_rotina, 'etiquetas': json.dumps(etiquetas), 'valores': json.dumps(valores), 'tipo': json.dumps(tipo)})

@require_GET
def atualizar_rotina(request):

    """
    View que atualiza os dados do dashboard Rotina a partir de uma requição AJAX contento os parâmetros solicitados pelo usuário.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    JsonResponse
        Retorna um JSON contendo o HTML atualizado do template 'atividades/partials/base_rotina.html' com um dicionário contento os seguintes contextos:
        - 'dict_rotina': Dicionário com os dados de rotina formatados e filtrados conforme parâmetros enviados pelo usuário.
        - 'etiquetas': Lista com os rótulos (labels) para geração do gráfico de rotina por remuneração.
        - 'valores': Lista com os valores para geração do gráfico de rotina por remuneração.
        - 'tipo': String com o tipo de gráfico definido nas preferências do usuário.

    Funcionamento:
    --------
    - A função verifica se a requisição é uma requisição AJAX, através do cabeçalho 'X-Requested-With'.
    - Obtém o tipo de período selecionado pelo usuário.
    - Checar qual tipo de período e obtém os demais parâmetros para chamar a função relativa ao período selecionado. A Função retornará o 'dict_rotina' que é o dicionário com os contextos necessários para a atualização da página.
    - Divide o 'dict_rotina' em suas devidas variáveis e recupera as preferências de usuário para obter o tipo do gráfico.
    - Renderiza o template 'atividades/partials/base_rotina.html' com os dados.

    Tratamento de erros:
    --------
    - Caso não seja um requisição AJAX, retorna erro 'Requisição Inválida' (HTTP 400).
    - Se a informação fornecida no parâmetro `periodoSelect` for inválida, retorna um erro 'Data inválida' (HTTP 400).
    - Caso o período selecionado for o 'personalizado' (periodoSelect == 6), a função formatará a data para o formatado %Y-%m-%d, caso haja erro na formatação retornará o erro 'Formato de data inválido. Use YYYY-MM-DD.' (HTTP 400).
    - Se houver erro na Função usada para gerar o dicionário 'dict_rotina' a função retornará 'Nenhum dado encontrado' (HTTP 404)
    - Se houver erro ao renderizar o template retorno o erro 'Erro ao renderizar o template:' com um código de erro específico (HTTP 500) 
    
    """

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
            
            preferencias = get_preferencias()
        else:       
            return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

        try:
            html_content = render_to_string('atividades/partials/base_rotina.html', {'rotina': dict_rotina, 'etiquetas': etiquetas, 'valores': valores, 'tipo':preferencias['tipo_grafico']})
        except Exception as e:
            return JsonResponse({'error': f'Erro ao renderizar o template: {str(e)}'}, status=500)

        return JsonResponse({'html': html_content, 'etiquetas': etiquetas, 'valores': valores, 'tipo':preferencias['tipo_grafico']})
    else:
        return JsonResponse({'error': 'Requisição inválida'}, status=400)
    
@require_GET
def atualizar_grafico_rotina(request):

    """
    View que atualiza os dados para a geração do gráfico do dashboard Rotina a partir de uma requição AJAX contento os parâmetros solicitados pelo usuário.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    JsonResponse
        Retorna um JSON contendo com um dicionário contento os seguintes contextos:
        - 'etiquetas': Lista com os rótulos (labels) para geração do gráfico.
        - 'valores': Lista com os valores para geração do gráfico.
        - 'tipo': String com o tipo de gráfico definido nas preferências do usuário.

    Funcionamento:
    --------
    - A função verifica se a requisição é uma requisição AJAX, através do cabeçalho 'X-Requested-With'.
    - Obtém o tipo de período e o gráfico desejado selecionado pelo usuário e recupera as preferências do usuário.
    - Checar qual tipo de período e obtém os demais parâmetros para filtrar as instâncias do modelo Atividades, obter a quantidade de dias, de horas e de horas de sono do período relativo às atividades filtradas.
    - Checa qual foi o gráfico escolhido pelo usuário e usa a Função pertinente à escolha para a geração do dicionário 'dict_rotina', que conterá as informações necessárias para a geração do gráfico.
    - Divide o 'dict_rotina' em suas devidas variáveis.

    Tratamento de erros:
    --------
    - Caso a requisição não seja uma requisição AJAX, retorna o erro 'Requisição Inválida' (HTTP 400).
    - Se a informação fornecida no parâmetro `periodoSelect` for inválida, retorna um erro 'Data inválida' (HTTP 400).
    - Caso o período selecionado for o 'personalizado' (periodoSelect == 6), a função formatará a data para o formatado %Y-%m-%d, caso haja erro na formatação retornará o erro 'Formato de data inválido. Use YYYY-MM-DD.' (HTTP 400).
    - Se a query 'atividades' retornar vazia, o dicionário 'dict_rotina' é preenchido com valor nulo para prevenção de erro em manipulações futuras.
    - Se a informação fornecida no parâmetro 'graficoSelect' for inválida, retorna o erro 'Grafico Select Inválido' (HTTP 400).
    - Se houver erro na Função usada para gerar o dicionário 'dict_rotina' a função retornará 'Não foi possível gerar dict_financeiro a partir do período selecionado'. (HTTP 404)
    
    """

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        periodoSelect = request.GET.get('periodoSelect')
        graficoSelect = request.GET.get('graficoSelect')
        preferencias = get_preferencias()

        try:
            if periodoSelect == '1':
                mesSelect = request.GET.get('mesSelect')
                atividades = Atividades.objects.filter(data__month=int(mesSelect))
                quant_dias = calendar.monthrange(datetime.today().year, int(mesSelect))[1]
                quant_horas = quant_dias * 24
                qt_horas_sono = quant_dias * preferencias['horas_sono']

            elif periodoSelect == '2':
                anoSelect = request.GET.get('anoSelect')
                ano = int(anoSelect)
                atividades = Atividades.objects.filter(data__year=ano)
                data_inicio = datetime(ano, 1, 1).date()
                data_final = datetime(ano, 12, 31).date()
                diferenca = data_final - data_inicio
                quant_dias = diferenca.days
                quant_horas = quant_dias * 24
                qt_horas_sono = quant_dias * preferencias['horas_sono']

            elif periodoSelect == '3':
                data_inicio = datetime.today().date()
                ano = data_inicio.year
                mes = data_inicio.month
                ultimo_dia = calendar.monthrange(ano, mes)[1]
                data_final = datetime(ano, mes, ultimo_dia).date()
                atividades = Atividades.objects.filter(data__range=(data_inicio, data_final))
                quant_dias = ultimo_dia - data_inicio.today().day
                quant_horas = quant_dias * 24
                qt_horas_sono = quant_dias * preferencias['horas_sono']

            elif periodoSelect == '4':
                data_inicio = datetime.today().date()
                ano = data_inicio.year
                data_final = datetime(ano, 12, 31).date()    
                atividades = Atividades.objects.filter(data__range=(data_inicio, data_final))
                diferenca = data_final - data_inicio
                quant_dias = diferenca.days
                quant_horas = quant_dias * 24
                qt_horas_sono = quant_dias * preferencias['horas_sono'] 

            elif periodoSelect == '5':
                atividades = Atividades.objects.all()

                data_inicio = Atividades.objects.all().order_by('data').first()
                data_final = Atividades.objects.all().order_by('data').last()

                diferenca = data_final.data - data_inicio.data
                quant_dias = diferenca.days
                quant_horas = quant_dias * 24
                qt_horas_sono = quant_dias * preferencias['horas_sono']

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
                qt_horas_sono = quant_dias * preferencias['horas_sono']

        except ValueError:
            return JsonResponse({'error': 'Data inválida'}, status=400)
        
        if atividades:        
            try:
                if graficoSelect == '1':
                    dict_rotina = gerar_grafico_remuneracao_rotina(atividades)
                elif graficoSelect == '2':
                    dict_rotina = gerar_grafico_tipo_rotina(atividades)
                elif graficoSelect == '3':
                    dict_rotina = gerar_grafico_categoria_rotina(atividades)
                elif graficoSelect == '4':
                    dict_rotina = gerar_grafico_ocupacao_rotina(atividades, quant_horas, qt_horas_sono)
            except ValueError:
                return JsonResponse({'error': 'Grafico Select Inválido'}, status=400)
        else:
            dict_rotina = {
                '':'',
            }
        
        if dict_rotina:
            etiquetas = list(dict_rotina.keys())
            valores = list(dict_rotina.values())
        else:       
            return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

        return JsonResponse({'etiquetas': etiquetas, 'valores': valores, 'tipo':preferencias['tipo_grafico']})
    else:
        return JsonResponse({'error': 'Requisição inválida'}, status=400)
    
def preferencias(request):

    """
    View que exibir registro único das preferências do usuário.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'atividades/preferencias.html' com o dicionário 'dict_preferencia' contendo as informações, já formatadas para exibição, das preferências do usuário do sistema.
    """

    preferencias = Preferencias.objects.get(id=1)

    dict_preferencia = {}

    tipo_grafico = {
        'bar': 'Barras',
        'pie': 'Pizza',
        'doughnut': 'Roscas'
    }.get(preferencias.tipo_grafico, None)

    inicio_semana = {
        '0': 'Segunda-Feira',
        '1': 'Domingo',
        '2': 'Sábado',
        '3': 'Sexta-Feira',
        '4': 'Quinta-Feira',
        '5': 'Quarta-Feira',
        '6': 'Terça-Feira'
    }.get(preferencias.inicio_semana, None)

    dict_preferencia = {
        'horas_sono':f'{preferencias.horas_sono} horas',
        'tipo_grafico': tipo_grafico,
        'inicio_semana': inicio_semana,
        'hora_envio_tarefas': preferencias.hora_envio_tarefas
    }

    return render(request, 'atividades/preferencias.html', {'preferencias':dict_preferencia})

def editar_preferencias(request):

    """
    Formulário para editar as preferências do usuário.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'atividades/editar_preferencias.html' com o formulário PreferenciaForms instanciado pelo id 1, que é o único parâmentro desse modelo.
        Se o método for POST: Salva o formulário enviado com as informações inseridas pelo usuário, atualizando em caso de qualquer alteração, e o redirecionando para a path 'preferencias', exibindo uma mensagem informando o sucesso na edição do tipo de atividade. 

    Tratamento de erros:
    --------
    - Caso o formulário enviado pelo usuário seja inválido, o formulário não será salvo e será exibida a mensagem de erro "Não foi possível realizar a edição. Favor revise os dados ou entre em contato com o administrador do sistema.".
    """

    preferencia = Preferencias.objects.get(id=1)
    forms = PreferenciasForms(instance=preferencia)

    if request.method == 'POST':

        forms = PreferenciasForms(request.POST, instance=preferencia)

        if forms.is_valid():
            forms.save()
            messages.success(request, 'Edição realizada com sucesso')
            return redirect('preferencias')
        else:
            messages.error(request, 'Não foi possível realizar a edição. Favor revise os dados ou entre em contato com o administrador do sistema.')

    return render(request, 'atividades/editar_preferencias.html', {'forms':forms})

def get_preferencias():

    """
    View que recupera as prefências do usuário do modelo Preferencias instânciada no objeto único desse modelo.

    Retorno:
    --------
    dict
        Retorna um dicionário com as preferências cadastradas pelo usuário na tela de preferências em consfigurações.

    Notas:
    --------
    - Essa versão do sistema é prepara apenas para um usuário único, com isso o modelo Preferencia terá sempre um único objeto de id=1.

    """

    preferencias = Preferencias.objects.get(id=1)

    dict_preferencia = {
        'horas_sono': preferencias.horas_sono,
        'tipo_grafico': preferencias.tipo_grafico,
        'inicio_semana': preferencias.inicio_semana 
    }

    return dict_preferencia

