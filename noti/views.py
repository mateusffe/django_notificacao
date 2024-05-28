from django.shortcuts import render, redirect
from .models import Entidade
from django.contrib import messages
from .forms import EntidadeForm, UserEntidade
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate, logout
# Create your views here.


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
    all =  Entidade.objects.all()
    paginator = Paginator(all, 5)
    pages = request.GET.get('page')
    dados['db'] = paginator.get_page(pages)
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

def sair(request):
    logout(request)
    return redirect('index')      
##FIM CODIGO USUARIO ENTIDADE