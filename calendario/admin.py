from django.contrib import admin
from calendario.models import Calendario

class ListandoCalendario(admin.ModelAdmin):
    list_display = ('id', 'dia', 'range')
    list_display_links = ('id',)
    search_fields = ('dia', 'range')
    list_filter = ('dia', 'range')
    list_per_page = 10

admin.site.register(Calendario, ListandoCalendario)