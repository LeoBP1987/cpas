from django.contrib import admin
from atividades.models import TipoAtividade, Instituicao, Atividades

class ListandoTipoAtividade(admin.ModelAdmin):
    list_display = ('id', 'nome_tipo', 'horas')
    list_display_links = ('id', 'nome_tipo')
    search_fields = ('nome_tipo', 'horas')
    list_filter = ('horas',)
    list_per_page = 10

class ListandoInstituicao(admin.ModelAdmin):
    list_display = ('id', 'nome_inst', 'valor_padrao')
    list_display_links = ('id', 'nome_inst',)
    search_fields = ('nome_inst', 'valor_padrao')
    list_filter = ('nome_inst', 'valor_padrao')
    list_per_page = 10

class ListandoAtividades(admin.ModelAdmin):
    list_display = ('id', 'tipo_atividade', 'data', 'valor',)
    list_display_links = ('id', 'data')
    search_fields = ('instituicao', 'data', 'valor')
    list_filter = ('data', 'valor')
    list_per_page = 10

admin.site.register(TipoAtividade, ListandoTipoAtividade)
admin.site.register(Instituicao, ListandoInstituicao)
admin.site.register(Atividades, ListandoAtividades)