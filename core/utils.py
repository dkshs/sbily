from django.contrib import messages
from django.contrib.messages import constants
from django.core.validators import URLValidator


def link_is_valid(request, link_redirecionado, link_encurtado):
    if len(link_encurtado.strip()) == 0 or len(link_redirecionado.strip()) == 0:
        messages.add_message(request, constants.ERROR, "Preencha todos os campos")
        return False

    if link_encurtado.count("/") != 0:
        messages.add_message(
            request, constants.ERROR, "Link encurtado não pode conter barras."
        )
        return False
    elif link_encurtado.count("#") != 0:
        messages.add_message(
            request, constants.ERROR, "Link encurtado não pode conter #."
        )
        return False

    validate = URLValidator()
    try:
        validate(link_redirecionado)
    except:
        messages.add_message(request, constants.ERROR, "Informe uma URL válida.")
        return False

    return True
