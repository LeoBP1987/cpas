from django.contrib import admin
from atividades.models import TipoAtividade, Instituicao, Atividades

class ListandoTipoAtividade(admin.ModelAdmin):
    list_display = ('id', 'nome_tipo', 'categoria')
    list_display_links = ('id', 'nome_tipo')
    search_fields = ('nome_tipo', 'categoria')
    list_filter = ('categoria',)
    list_per_page = 10

class ListandoInstituicao(admin.ModelAdmin):
    list_display = ('id', 'nome_inst', 'valor_fixo')
    list_display_links = ('id', 'nome_inst',)
    search_fields = ('nome_inst', 'fixo_mensal_inst', 'valor_fixo')
    list_filter = ('nome_inst', 'fixo_mensal_inst', 'valor_fixo')
    list_per_page = 10

class ListandoAtividades(admin.ModelAdmin):
    list_display = ('id', 'tipo_atividade', 'data', 'fixo_mensal_ativ', 'valor',)
    list_display_links = ('id', 'data')
    search_fields = ('instituicao', 'data', 'valor')
    list_filter = ('data', 'fixo_mensal_ativ', 'valor')
    list_per_page = 10

admin.site.register(TipoAtividade, ListandoTipoAtividade)
admin.site.register(Instituicao, ListandoInstituicao)
admin.site.register(Atividades, ListandoAtividades)