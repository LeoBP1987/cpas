from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from usuarios.tasks import enviar_email_task


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            enviar_email_task.s(),  # .s() envia a tarefa para o Celery
            CronTrigger(hour=7, minute=00),  # Agendado para 07:00 diariamente
            id='email_diario',  # Identificador único para a tarefa
            replace_existing=True
        )
        scheduler.start()
