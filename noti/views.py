from django.shortcuts import render, redirect
from .models import Entidade, Notificacao, usuarioEntidade, Parecer
from django.views import View
from django.http import JsonResponse

from django.contrib import messages
from .forms import EntidadeForm, UserEntidade, NotificacaoForm, ParecerForm, buscaempresafilter
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate, logout
# Create your views here.


#criar um redirect de login para accounts login
def loginredirect(request):
    return redirect('accounts/login')



##INDEX PARA FISCAL E USUARIO

def index(request):
    if str(request.user) == 'AnonymousUser':
        teste = 'Usuário não logado'
    else:
        teste = 'Usuário Logado'

    context = { 
        'logado':teste
    }
    return render(request, 'index.html', context)

def indexcomum(request):
    return render(request, 'indexcomum.html')


#INICIO CODIFICAÇÃO PARA ENTIDADE

def forment(request):
    data = {}
    data['form'] = EntidadeForm()
    return render(request, 'formentidade.html', data)

def criaentidade(request):
    form= EntidadeForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('index')
    
def editarentidade(request, pk):
    data = {} 
    data['db'] = Entidade.objects.get(pk=pk)
    data['form'] = EntidadeForm(instance = data['db'])
    return render(request, 'formentidade.html', data)


def alterarentidade(request, pk): 
    data = {}
    data['db'] = Entidade.objects.get(pk=pk)
    form = EntidadeForm(request.POST or None, instance=data['db'])
    if form.is_valid():
        form.save()
        return redirect('buscaempresa')


def buscaempresa(request):
    dados = {}
    form = buscaempresafilter(request.GET or None)
    all = Entidade.objects.all()
    
    if form.is_valid():
        if form.cleaned_data.get('nome'):
            all = all.filter(razao_social__icontains=form.cleaned_data['nome'])
    all =all.order_by('id')
    paginator = Paginator(all, 5)
    pages = request.GET.get('page')
    dados['db'] = paginator.get_page(pages)
    
    if request.is_ajax():
        data = [
            {
                'id': dbs.id,
                'razao_social': dbs.razao_social,
            }
            for dbs in dados['db']
        ]
        return JsonResponse(data, safe=False)
    
    dados['form'] = form
    return render(request, 'buscaempresa.html', dados)

def deletarentidade(request, pk): 
    data = {}
    data['db'] = Entidade.objects.get(pk=pk)
    data['db'].delete()
    return redirect('buscaempresa')


def visualizarentidade(request, pk):
    data = {}
    data['db'] = Entidade.objects.get(pk=pk)
    return  render(request, 'visualizarentidade.html', data)

##FIM CODIGO ENTIDADE

##COMECO CODIGO USUARIO ENTIDADE

def userent(request):
    data = {}
    data['f'] = UserEntidade()
    return render(request, 'formcadastrousuario.html', data)

def criaruserent(request):
    form= UserEntidade(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('index')

def buscausuario(request):
    dados = {}
    form = buscaempresafilter(request.GET or None)
    all = usuarioEntidade.objects.all()
    
    if form.is_valid():
        if form.cleaned_data.get('nome'):
            all = all.filter(user__username__icontains=form.cleaned_data['nome'])
    all =all.order_by('liberado')
    paginator = Paginator(all, 5)
    pages = request.GET.get('page')
    dados['db'] = paginator.get_page(pages)
    
    if request.is_ajax():
        data = [
            {
                'user': dbs.user,
                'escolha':dbs.escolha,
                'liberado': dbs.liberado,
            }
            for dbs in dados['db']
        ]
        return JsonResponse(data, safe=False)
    
    dados['form'] = form
    return render(request, 'buscausuario.html', dados)

##FIM CODIGO USUARIO ENTIDADE

##LOGICA NOTIFICACAO 
def CriarNotificacao(request):
    data = {}
    data['f'] = NotificacaoForm()
    return render(request, 'cadastrarnotificacao.html', data)

def salvarnotificacao(request):
    form= NotificacaoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('index')

def buscanotificacao(request):
    dados = {}
    form = buscaempresafilter(request.GET or None)
    all =  Notificacao.objects.all()
       
    if form.is_valid():
      if form.cleaned_data.get('nome'):
            all = all.filter(notif__icontains=form.cleaned_data['nome'])
            
    all =all.order_by('notif')
    paginator = Paginator(all, 5)
    pages = request.GET.get('page')
    dados['db'] = paginator.get_page(pages)
    
    if request.is_ajax():
        data = [
            {
                'notif': dbs.notif,
                'entidade': dbs.entidade,
                'regularidade':dbs.regularidade,
            }
            for dbs in dados['db']
        ]
        return JsonResponse(data, safe=False)
    
    dados['form'] = form
    return render(request, 'buscanotificaogeral.html', dados)
    
def visualizarnotificacao(request, pk):
    data = {}
    data['db'] = Notificacao.objects.get(pk=pk)
    data['pn'] = Parecer.objects.all()
    data['pn'] = data['pn'].filter(notificacao__codigo_verificador__icontains= pk)
   
    return  render(request, 'visualizarnotificacao.html', data)
    
 
##FIM NOTIFICACAO

##PARECER
def CriarParecer(request):
    data = {}
    data['f'] = ParecerForm()
    return render(request, 'parecer.html', data)


def salvarparecer(request):
    form= ParecerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('index')
##FIM PARECER