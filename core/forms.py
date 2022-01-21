from django import forms
from django.forms import forms, ModelForm
from .models import Links

class FormLinks(ModelForm):
    class Meta:
        model = Links
        fields = "__all__"