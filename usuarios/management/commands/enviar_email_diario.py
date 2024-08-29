from django.core.management.base import BaseCommand
from usuarios.tasks import enviar_email

class Command(BaseCommand):
    help = 'Envia um email diariamente em uma hora específica.'

    def handle(self, *args, **kwargs):
        enviar_email()
        self.stdout.write(self.style.SUCCESS('Email enviado com sucesso!'))