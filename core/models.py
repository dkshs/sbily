from django.db import models
from decouple import config


class Link(models.Model):
    link_redirecionado = models.URLField()
    link_encurtado = models.CharField(max_length=8, unique=True)
    link_fixo = config("DOMAIN_DEFAULT", default="http://127.0.0.1:8000/")

    def __str__(self):
        return self.link_encurtado
