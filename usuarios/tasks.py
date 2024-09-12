from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime

def gerar_tarefas_dia():

    """
    Gera uma mensagem com as atividades cadastradas para o dia atual, formatada em HTML básico.

    Esta função busca as atividades no banco de dados que estão agendadas para o dia atual
    e gera uma mensagem com os detalhes de cada uma delas, formatada em HTML básico.
    Caso não existam atividades cadastradas, uma mensagem padrão de descanso é retornada.

    Retorno:
    --------
    str
        Uma string contendo a lista de atividades do dia ou uma mensagem indicando que
        não há atividades cadastradas para hoje.
    """

    from atividades.models import Atividades

    data_hoje = datetime.today().date()

    dict_ativ_hoje = {}

    # Usando tags HTML básicas
    message = '''Evite supresas, segue abaixo as tarefas que você tem cadastrada para hoje para poder se programar.
                
    
            '''

    atividades = Atividades.objects.filter(data=data_hoje)

    if atividades:
        for atividade in atividades:
            if atividade.saida < 24:
                periodo = f'{atividade.entrada:02d}:00 às {atividade.saida:02d}:00'
            else:
                periodo = f'{atividade.entrada:02d}:00 às 00:00'

            dict_ativ_hoje[atividade.entrada] = {
                'entrada': atividade.entrada,
                'periodo': periodo,
                'instituicao': atividade.instituicao.nome_inst,
                'tipo': atividade.tipo_atividade.nome_tipo
            }
        lista_ativ_hoje = list(dict_ativ_hoje.values())

        lista_ativ_hoje.sort(key=lambda x: x['entrada'])

        for atividade in lista_ativ_hoje:
            message += f'''
                        {atividade['periodo']} 

                        {atividade['instituicao']} 

                        {atividade['tipo']} 
                        

                        '''
    else:
        message = 'Você não tem tarefas cadastradas para hoje. Relaxe e aproveite seu dia.'

    return message

def enviar_email():
    """
    Envia um e-mail com as atividades do dia atual.

    Esta função utiliza a função `gerar_tarefas_dia` para gerar o conteúdo da mensagem
    de e-mail e, em seguida, envia o e-mail com o assunto 'AGENDA DE HOJE' para uma lista 
    de destinatários predefinida.

    Retorno:
    --------
    None
        A função não retorna valor, apenas realiza o envio do e-mail através da Função send_mail.

    Tratamento de erro:
    --------
    - Caso o usuário não possua um email cadastrado a função dispara um email para o administrador do sistema informando o erro.

    Notas:
    --------
    - A importação dos módulos necessários para carregar o email do usuário e o mail do administrado são realizadas via 'lazy import' para evitar erros de tentativa de importação antes do Django estar totalmente carregado.

    """
    from django.contrib.auth import get_user_model
    from pathlib import Path, os
    from dotenv import load_dotenv

    load_dotenv()

    User = get_user_model()
    usuario = User.objects.first()
    email = str(usuario.email)

    if email and email != 'seu_email@email.com':
        subject = 'AGENDA DE HOJE'
        message = gerar_tarefas_dia()
        recipient_list = [email]
    else:
        subject = 'ERRO NO ENVIO DE RELATÓRIO DIÁRIO'
        message = f'O usuário {usuario.first_name} não possui um email válido cadastrado.'
        recipient_list = [str(os.getenv('DEFAULT_FROM_EMAIL'))]
    
    send_mail(subject, message, str(os.getenv('DEFAULT_FROM_EMAIL')), recipient_list)  

@shared_task
def enviar_email_task():
    """
    Tarefa assíncrona para enviar e-mail com as atividades do dia atual.

    Esta função utiliza o Celery para executar a tarefa de envio de e-mail de forma assíncrona.
    Ela chama a função `enviar_email`, que por sua vez envia o e-mail contendo as atividades
    cadastradas para o dia atual.

    Retorno:
    --------
    None
        A função não retorna valor, apenas executa a tarefa de envio de e-mail de forma assíncrona.
    """
    enviar_email()
