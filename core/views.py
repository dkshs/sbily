from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import FormLinks
from .models import Links

def home(request):
    form = FormLinks()
    status = request.GET.get('status')
    return render(request, 'home.html', {'form': form, 'status': status})

def valida_link(request):
    form = FormLinks(request.POST)

    link_fixo = 'https://sbily.herokuapp.com/'
    link_encurtado = form.data['link_encurtado']
    link = Links.objects.filter(link_encurtado = link_encurtado)
    if len(link) > 0:
        return redirect("/?status=1")
        
    if form.is_valid():
        try:
            form.save()
            return render(request, 'links.html', {'link_fixo': link_fixo, 'link_encurtado': link_encurtado})
        except:
            return HttpResponse('Erro Interno do Sistema')

def redirecionar(request, link):
    link = Links.objects.filter(link_encurtado = link)
    if len(link) == 0:
        return redirect('/')

    return redirect(link[0].link_redirecionado)