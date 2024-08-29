from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Define o módulo de configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cpas.settings')

# Cria a instância do Celery
app = Celery('cpas')

# Usar a configuração do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carregar tarefas de todos os aplicativos
app.autodiscover_tasks()