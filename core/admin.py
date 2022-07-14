from django.contrib import admin
from .models import Link

@admin.register(Link)
class LinksADM(admin.ModelAdmin):
    list_display = ('link_redirecionado', 'link_fixo', 'link_encurtado')
    search_fields = ['link_redirecionado', 'link_encurtado']
