from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from usuarios.tasks import enviar_email_task
from django.db.models.signals import post_migrate


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        
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
