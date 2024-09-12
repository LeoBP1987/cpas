from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from usuarios.tasks import enviar_email_task
from django.db.models.signals import post_migrate


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):

        """
        Inicializa a tarefa agendada para envio diário de e-mails com as atividades do usuário.

        Esta função é chamada quando o Django é carregado. Ela configura um
        agendador de tarefas utilizando o `BackgroundScheduler` do APScheduler, que agenda
        o envio de um e-mail diário contendo as atividades do dia com base nas preferências 
        de horário definidas pelo usuário.

        A função obtém as preferências de envio (horário) a partir do modelo `Preferencias` e,
        em seguida, configura um job cron que executa a tarefa assíncrona `enviar_email_task` 
        no horário especificado.

        Agendamento:
        ------------
        - A tarefa é agendada para ser executada diariamente no horário configurado nas 
          preferências do usuário.
        - O job cron é criado com a `CronTrigger` para especificar a hora e minuto exatos
          de execução, baseados no campo `hora_envio_tarefas` do modelo `Preferencias`.

        Retorno:
        --------
        None
            A função não retorna nenhum valor, apenas configura e inicia o agendador de tarefas.

        Notas:
        --------
        - A importação do modelo prefêrencia é realizada via 'lazy import' para evitar erros de tentativa de importação antes do Django estar totalmente carregado.
        """
        
        from atividades.models import Preferencias

        preferencias = Preferencias.objects.get(id=1)
        hora = str(preferencias.hora_envio_tarefas.hour)
        minutos = str(preferencias.hora_envio_tarefas.minute)
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            enviar_email_task.s(),
            CronTrigger(hour=hora, minute=minutos),
            id='email_diario',
            replace_existing=True
        )
        scheduler.start()