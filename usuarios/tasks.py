from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime

def gerar_tarefas_dia():

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
    subject = 'AGENDA DE HOJE'
    message = gerar_tarefas_dia()
    recipient_list = ['suzanalamartin@gmail.com']
    
    send_mail(subject, message, 'leonardobp1987@gmail.com', recipient_list)

@shared_task
def enviar_email_task():
    enviar_email()
