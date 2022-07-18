from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Link
from django.contrib import messages
from django.contrib.messages import constants
from decouple import config


def home(request):
    return render(request, "home.html")


def valida_link(request):
    link_redirecionado = request.POST.get("link_redirecionado")
    link_encurtado = request.POST.get("link_encurtado")

    if len(link_encurtado.strip()) == 0 or len(link_redirecionado.strip()) == 0:
        messages.add_message(request, constants.ERROR, "Preencha todos os campos")
        return redirect("/")

    link = Link.objects.filter(link_encurtado=link_encurtado)

    if link.exists():
        messages.add_message(request, constants.ERROR, "Este link encurtado já existe")
        return redirect("/")

    try:
        link.create(
            link_redirecionado=link_redirecionado, link_encurtado=link_encurtado
        )
        messages.add_message(
            request, constants.SUCCESS, "Link Encurtado criado com sucesso"
        )
        link_encurtado_format = Link.link_fixo + link_encurtado
        return render(request, "link.html", {"link_encurtado": link_encurtado_format})
    except:
        messages.add_message(request, constants.ERROR, "Erro interno do sistema")
        return redirect("/")


def redirecionar(request, link):
    link = Link.objects.filter(link_encurtado=link)
    if not link.exists():
        return redirect("/")

    return redirect(link[0].link_redirecionado)


def handler404(request, exception, template_name="404.html"):
    response = render(request, template_name)
    response.status_code = 404
    return response


def handler500(request, *args, **argv):
    response = render(request, "500.html")
    response.status_code = 500
    return response
