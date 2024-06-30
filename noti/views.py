from django.shortcuts import render, redirect
from .models import Entidade, Notificacao, usuarioEntidade, Parecer, Arquivo
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
import re
from django.utils import timezone

from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlencode


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


def is_staff(user):
    return user.is_staff

def is_not_staff(user):
    return not user.is_staff

##INDEX PARA FISCAL E USUARIO

def index(request):
   
    usuario = request.user
    prazo_limite = timezone.now() - timedelta(days=30)
    if usuario.is_authenticated:
        if usuario.is_staff:
            count_irregulares = Notificacao.objects.filter(regularidade=False).count()
            count_regulares = Notificacao.objects.filter(regularidade=True).count()
            count_total = Notificacao.objects.count()
            count_fora_do_prazo = Notificacao.objects.filter(Q(data__lte=prazo_limite) & Q(regularidade=False)).count()
             
            context = { 
            'irregulares':count_irregulares,
            'regulares':count_regulares,
            'total':count_total,
            'data':count_fora_do_prazo,
            
            }
            return render(request, 'index.html', context)
        else:
            entidade = Entidade.objects.get(usuario__user=usuario)
            notificacoes = Notificacao.objects.filter(entidade=entidade)
            c_not_usuario_ab = notificacoes.filter(regularidade=False).count()
            c_usuario_limit = notificacoes.filter(Q(data__lte=prazo_limite) & Q(regularidade=False)).count()
            context = {
            'total':notificacoes.count(),
            'abertos':c_not_usuario_ab,
            'data_us':c_usuario_limit,
            } 
            return render(request, 'index.html', context)
   
    else:
         return render(request, 'index.html')
 
    



#INICIO CODIFICAÇÃO PARA ENTIDADE
@login_required
@user_passes_test(is_staff)
def forment(request):
    data = {}
    data['form'] = EntidadeForm()
    return render(request, 'formentidade.html', data)

@login_required
@user_passes_test(is_staff)
def criaentidade(request):
    form= EntidadeForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('index')

@login_required
@user_passes_test(is_staff)
def editarentidade(request, pk):
    data = {} 
    data['db'] = Entidade.objects.get(pk=pk)
    data['form'] = EntidadeForm(instance = data['db'])
    return render(request, 'formentidade.html', data)

@login_required
@user_passes_test(is_staff)
def alterarentidade(request, pk): 
    data = {}
    data['db'] = Entidade.objects.get(pk=pk)
    form = EntidadeForm(request.POST or None, instance=data['db'])
    if form.is_valid():
        form.save()
        return redirect('buscaempresa')
    else: 
        error_message = "FORMULARIO INVALIDO."
        fm = EntidadeForm(instance = data['db'])
        data={
            'error_message':error_message,
            'form':fm,
        }
        return render(request, 'formentidade.html', data)

@login_required
@user_passes_test(is_staff)
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

@login_required
@user_passes_test(is_staff)
def deletarentidade(request, pk): 
    data = {}
    data['db'] = Entidade.objects.get(pk=pk)
    data['db'].delete()
    return redirect('buscaempresa')

@login_required
@user_passes_test(is_staff)
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
    

@login_required
@user_passes_test(is_staff)
def buscausuario(request):
    dados = {}
    form = buscaempresafilter(request.GET or None)
    all_users = usuarioEntidade.objects.all()

    if form.is_valid():
        queries = []
        search_input = form.cleaned_data.get('nome')

        if search_input: 
            liberado_match = re.search(r'liberado:\s*([^\s]+)', search_input, re.IGNORECASE)
            escolha_match = re.search(r'tipo:\s*([^\s]+)', search_input, re.IGNORECASE)

            if liberado_match:
                lib = liberado_match.group(1).lower()
                if lib in ['true', '1', 'liberado']:
                    queries.append(Q(liberado=True))
                elif lib in ['false', '0', 'no']:
                    queries.append(Q(liberado=False))

            if escolha_match:
                esc = escolha_match.group(1)
                queries.append(Q(escolha__icontains=esc))
            
            if not liberado_match and not escolha_match:
                queries.append(Q(user__username__icontains=form.cleaned_data['nome']))

        if queries:
            combined_query = Q()
            for query in queries:
                combined_query &= query
            filtrado = all_users.filter(combined_query)
        else:
            filtrado = all_users

        all_users = filtrado

    all_users = all_users.order_by('liberado')
    paginator = Paginator(all_users, 5)
    pages = request.GET.get('page')
    dados['db'] = paginator.get_page(pages)
    
    
    if request.is_ajax():
        data = []
        for dbs in dados['db']:
            try:
                entidade = Entidade.objects.get(usuario=dbs)
                entidade_razao_social = entidade.razao_social
            except Entidade.DoesNotExist:
                entidade_razao_social = None

            data.append({
                'user': dbs.user.username,
                'escolha': dbs.escolha,
                'liberado': dbs.liberado,
                'entidade': entidade_razao_social,
            })
        
        return JsonResponse(data, safe=False)
    
    dados['form'] = form
    return render(request, 'buscausuario.html', dados)


##FIM CODIGO USUARIO ENTIDADE

##LOGICA NOTIFICACAO 
@login_required
@user_passes_test(is_staff)
def CriarNotificacao(request):
    data = {}
    data['form'] = NotificacaoForm()
    return render(request, 'cadastrarnotificacao.html', data)

@login_required
@user_passes_test(is_staff)
def salvarnotificacao(request):
    form= NotificacaoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('index')

@login_required
@user_passes_test(is_staff)
def buscanotificacao(request):
    dados = {}
    form = buscaempresafilter(request.GET or None)
    all =  Notificacao.objects.all()
    data_limite = timezone.now() - timedelta(days=30)

 
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
    dados['data_limite'] = data_limite
    
    return render(request, 'buscanotificaogeral.html', dados)

@login_required
def visualizarnotificacao(request, pk):
    data = {}
    data['db'] = Notificacao.objects.get(pk=pk)
    data['pn'] = Parecer.objects.all()
    data['pn'] = data['pn'].filter(notificacao__codigo_verificador__icontains= pk)
    data['ar'] = Arquivo.objects.all()
    data['ar'] = data['ar'].filter(notificacao__codigo_verificador__icontains= pk)
    return  render(request, 'visualizarnotificacao.html', data)

@login_required
@user_passes_test(is_staff)
def regularizar(request, pk):
    notificacao = Notificacao.objects.get(pk=pk)
    notificacao.regularidade = True
    notificacao.save()
    return redirect('index')
    
@login_required
@user_passes_test(is_staff)
def editarnotificacao(request, pk):
    data = {} 
    data['db'] = Notificacao.objects.get(pk=pk)
    data['form'] = NotificacaoForm(instance = data['db'])
    return render(request, 'cadastrarnotificacao.html', data)

@login_required
@user_passes_test(is_staff)
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
@user_passes_test(is_staff)
def CriarParecer(request):
    data = {}
    data['f'] = ParecerForm()
    return render(request, 'parecer.html', data)

@login_required
@user_passes_test(is_staff)
def salvarparecer(request):
    form= ParecerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('index')
##FIM PARECER


@login_required
@user_passes_test(is_staff)
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
@user_passes_test(is_staff)
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
@user_passes_test(is_not_staff)
def historicousuario(request):
    data = {}
    usuario = request.user
    entidade = Entidade.objects.get(usuario__user=usuario)
    data['db'] = Notificacao.objects.filter(entidade=entidade)   
    return render(request, 'buscanotiusuario.html', data)

@login_required
@user_passes_test(is_not_staff)
def paginausuario(request, id):
    usuario_entidade = usuarioEntidade.objects.get(id=id)
    action = request.GET.get('action', 'view')  # Default to 'view' if no action is specified
    
    if action == 'view':
        data={}
        data['db'] = usuarioEntidade.objects.get(id=id)
        data['et'] = Entidade.objects.get(usuario__user=id)
        return render(request, 'paginausuario.html', data)

    elif action == 'delete':
        try:
            entidade = Entidade.objects.get(usuario=usuario_entidade)
            entidade.usuario = None  # Dissociar a entidade do usuarioEntidade
        except Entidade.DoesNotExist:
           pass
        usuario_entidade.delete()  # Excluir o usuarioEntidade
        return redirect('index')  # Redirecionar para a lista de usuários após deletar
    
    elif action == 'libera':
        usuario_entidade.liberado = True
        usuario_entidade.save()
        return redirect('/buscausuario')
    else:
        # Ação padrão (visualizar)
        return render(request, 'paginausuario.html', {'usuario_entidade': usuario_entidade})

@login_required
@user_passes_test(is_staff)
def filtros(request):
    prazo_limite = timezone.now() - timedelta(days=30)

    action = request.GET.get('action')
    data ={}
    if action == 'aberto':
        notificacoes = Notificacao.objects.filter(regularidade=False)
    elif action == 'foraprazo':
        notificacoes = Notificacao.objects.filter(Q(data__lte=prazo_limite) & Q(regularidade=False))
    elif action=='total': 
        notificacoes = Notificacao.objects.all()
    elif action=='regular':
        notificacoes = Notificacao.objects.filter(regularidade=True)
    else:
        return redirect('index')
    
    paginator = Paginator(notificacoes, 10) 
    page_number = request.GET.get('page')
    data['db'] = paginator.get_page(page_number)
    
    return render(request, 'filtros.html', data)

@login_required
@user_passes_test(is_not_staff)
def filtrosue(request):
    usuario = request.user 
    prazo_limite = timezone.now() - timedelta(days=30)
    entidade = Entidade.objects.get(usuario__user=usuario)
    if not usuario.is_staff:
        action = request.GET.get('action')
        data ={}
        if action == 'aberto':
            notificacoes =  Notificacao.objects.filter(Q(entidade=entidade) & Q(regularidade=False))
        elif action == 'foraprazo':
            notificacoes = Notificacao.objects.filter(Q(data__lte=prazo_limite) & Q(regularidade=False) & Q(entidade=entidade))
        elif action=='total': 
            notificacoes = Notificacao.objects.filter(entidade=entidade)
        else:
            return redirect('index')
        
    paginator = Paginator(notificacoes, 10) 
    page_number = request.GET.get('page')
    data['db'] = paginator.get_page(page_number)
    
    return render(request, 'filtrosue.html', data)