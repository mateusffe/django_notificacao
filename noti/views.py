from django.shortcuts import render, redirect
from .models import Entidade, Notificacao, usuarioEntidade, Parecer, Arquivo
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
import re
from datetime import timedelta
from django.contrib.auth.decorators import login_required

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import io
from django.contrib import messages
from .forms import EntidadeForm, UserEntidade, NotificacaoForm, ParecerForm, buscaempresafilter, ArquivoForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
        queries = []
        search_input = form.cleaned_data.get('nome')

        if search_input: 
            entidade_match = re.search(r'empresa:\s*([^\s]+)', search_input, re.IGNORECASE)
            cnpj_match = re.search(r'cnpj:\s*([^\s]+)', search_input, re.IGNORECASE)
            cpf_match =  re.search(r'cpf:\s*([^\s]+)', search_input, re.IGNORECASE)
          
            if entidade_match:
                empresa = entidade_match.group(1)
                queries.append(Q(razao_social__icontains=empresa))

            if cnpj_match:
                cnpj = cnpj_match.group(1)
                queries.append(Q(cnpj__icontains=cnpj))

            if cpf_match:
                cpf = cpf_match.group(1)
                queries.append(Q(cpf__icontains=cpf))
            
            else:  
                queries.append(Q(razao_social__icontains=form.cleaned_data['nome']))
                
                

        filtrado = next((all.filter(query) for query in queries if all.filter(query).exists()), all)
        
        all = filtrado

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
    data['pn'] = Notificacao.objects.all()
    data['pn'] = data['pn'].filter(entidade__id__icontains= pk)
    return  render(request, 'visualizarentidade.html', data)

##FIM CODIGO ENTIDADE

##COMECO CODIGO USUARIO ENTIDADE

def userent(request):
    data = {}
    data['form'] = UserEntidade()
    return render(request, 'formcadastrousuario.html', data)


def criaruserent(request):
    form= UserEntidade(request.POST or None) 
    if form.is_valid():
        form.save(commit=True)        
        return redirect('index')
    else:
        return render(request, 'formcadastrousuario.html',{'form':form})
    


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
    data['form'] = NotificacaoForm()
    return render(request, 'cadastrarnotificacao.html', data)

def salvarnotificacao(request):
    form= NotificacaoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('index')

@login_required
def buscanotificacao(request):
    dados = {}
    form = buscaempresafilter(request.GET or None)
    all =  Notificacao.objects.all()
       
 
    if form.is_valid():
        queries = []
        search_input = form.cleaned_data.get('nome')

        if search_input:
            fiscal_match = re.search(r'fiscal:\s*([^\s]+)', search_input, re.IGNORECASE)
            entidade_match = re.search(r'empresa:\s*([^\s]+)', search_input, re.IGNORECASE)
            
            if fiscal_match:
                fiscal = fiscal_match.group(1)
                queries.append(Q(fiscal__nome__icontains=fiscal))

            if entidade_match:
                empresa = entidade_match.group(1)
                queries.append(Q(entidade__razao_social__icontains=empresa))


            else:  
                queries.append(Q(notif__icontains=form.cleaned_data['nome']))
                queries.append(Q(entidade__razao_social__icontains=form.cleaned_data['nome']))
                queries.append(Q(fiscal__nome__icontains=form.cleaned_data['nome']))
                

        filtrado = next((all.filter(query) for query in queries if all.filter(query).exists()), all)
        
        all = filtrado
      
            
    all =all.order_by('notif')
    paginator = Paginator(all, 10)
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
    data['ar'] = Arquivo.objects.all()
    data['ar'] = data['ar'].filter(notificacao__codigo_verificador__icontains= pk)
    return  render(request, 'visualizarnotificacao.html', data)
    
def regularizar(request, pk):
    notificacao = Notificacao.objects.get(pk=pk)
    notificacao.regularidade = True
    notificacao.save()
    return redirect('index')
    
@login_required
def editarnotificacao(request, pk):
    data = {} 
    data['db'] = Notificacao.objects.get(pk=pk)
    data['form'] = NotificacaoForm(instance = data['db'])
    return render(request, 'cadastrarnotificacao.html', data)

@login_required
def alterarnotificacao(request, pk): 
    data = {}
    data['db'] = Notificacao.objects.get(pk=pk)
    form = NotificacaoForm(request.POST or None, instance=data['db'])
    if form.is_valid():
        form.save()
        return redirect('index')
##FIM NOTIFICACAO

##PARECER
@login_required
def CriarParecer(request):
    data = {}
    data['f'] = ParecerForm()
    return render(request, 'parecer.html', data)

@login_required
def salvarparecer(request):
    form= ParecerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('index')
##FIM PARECER


@login_required
def generate_pdf(request, codigo_verificador):
    # Obter a notificação pelo código verificador
    notificacao = Notificacao.objects.get(codigo_verificador=codigo_verificador)

    # Caminho para o modelo de PDF
    pdf_template_path = 'static/modelonotif.pdf'

    # Ler o PDF existente
    pdf_template = PdfReader(pdf_template_path)
    pdf_writer = PdfWriter()

    # Pegar a primeira página do modelo
    page = pdf_template.pages[0]

    # Criar um buffer para o novo PDF
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Adicionar o código verificador no PDF
    can.setFont("Helvetica", 12)
    can.drawString(50, 50, f"Código Verificador: {notificacao.codigo_verificador}")
    can.save()

    # Mover o buffer para o início
    packet.seek(0)

    # Ler o PDF do buffer
    new_pdf = PdfReader(packet)
    new_page = new_pdf.pages[0]

    # Adicionar a nova página com o código verificador ao template existente
    page.merge_page(new_page)
    pdf_writer.add_page(page)

    # Criar a resposta HTTP com o PDF resultante
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="notificacao_{codigo_verificador}.pdf"'

    # Escrever o PDF resultante na resposta
    pdf_writer.write(response)

    return response

@login_required
def criaarquivo(request):
    if request.method == 'POST':
        form = ArquivoForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponse('The file is saved')
    else:
        form =ArquivoForm()
        context = {
            'f':form,
        }
    return render(request, 'upload_arquivo.html', context)

@login_required
def download_arquivo(request, arquivo_id):
    arquivo = Arquivo.objects.get(id=arquivo_id)
    response = HttpResponse(arquivo.arquivo, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{arquivo.arquivo.name}"'
    return response

def validador(request):
    if request.method == 'POST':
        codigo_verificador = request.POST.get('codigo_verificador')
        try:
            notificacao = Notificacao.objects.get(codigo_verificador=codigo_verificador)
            context = {
                'codigo_verificador': codigo_verificador,
                'codigo_valido': True,
                'prazo': notificacao.prazo,
                'data_notif': notificacao.data,
                'data_final': notificacao.data + timedelta(days=30),
                'fiscal': notificacao.fiscal,
            }
        except Notificacao.DoesNotExist:
            context = {
                'codigo_verificador': codigo_verificador,
                'codigo_valido': False,
            }
        return render(request, 'validador.html', context)
    else:
        return render(request, 'validador.html')



@login_required
def listar_notificacoes(request):
    usuario = request.user
    try:
        usuario_entidade = usuarioEntidade.objects.get(user=usuario)
        entidade = usuario_entidade.entidade
    except usuarioEntidade.DoesNotExist:
        entidade = None

    if entidade:
        notificacoes = Notificacao.objects.filter(entidade=entidade)
    else:
        notificacoes = []

    # Paginação
    paginator = Paginator(notificacoes, 10)  # Mostra 10 notificações por página
    page = request.GET.get('page')
    
    try:
        notificacoes_paginadas = paginator.page(page)
    except PageNotAnInteger:
        notificacoes_paginadas = paginator.page(1)
    except EmptyPage:
        notificacoes_paginadas = paginator.page(paginator.num_pages)

    context = {
        'f': notificacoes_paginadas
    }
    return render(request, 'buscanotiusuario.html', context)