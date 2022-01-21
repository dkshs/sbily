from django.contrib import admin
from django.db import models
from .models import Links

@admin.register(Links)
class LinksADM(admin.ModelAdmin):
    list_display = ('link_redirecionado', 'link_fixo', 'link_encurtado')
    search_fields = ['link_redirecionado', 'link_encurtado']