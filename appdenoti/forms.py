from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib import messages
from django.forms import ModelForm, DateTimeInput
from .models import Entidade, Notificacao, Parecer, Arquivo, Liberacao
from .models import ModelUsuario

class ModelUsuarioCreateForm(UserCreationForm):
    class Meta:
        model = ModelUsuario
        fields = ['username', 'first_name','last_name','fone']
        labels = {'username': 'Username/E-mail'}
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['username']

        if commit:
            user.save()

        return user


class ModelUsuarioChangeForm(UserChangeForm):
    class Meta:
        model = ModelUsuario
        fields = ('first_name', 'last_name','matricula', 'fone')

class buscafiltro(forms.Form):
    nome = forms.CharField(required=False)


class EntidadeForm(ModelForm):
     class Meta:
        model = Entidade
        fields = ['razao_social', 'nome_fantasia', 'cnpj', 'cpf', 'endereco', 'codigo_profissional', 'cnae']
        exclude = ['usuario']

class NotificacaoForm(forms.ModelForm):
    class Meta:
        model = Notificacao
        fields = [
            'codigo_verificador',
            'notif',
            'data',
            'motivo',
            'observacao',
            'regularidade',
            'prazo',
            'fiscal',
            'entidade'
        ]
        widgets = {
            'data': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Data', 'type':'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'codigo_verificador': forms.NumberInput(attrs={'class': 'form-control'}),
            'notif': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nº Notificação'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motivo', 'type':''}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Observação'}),
            'regularidade': forms.CheckboxInput(attrs={'class': 'form-check-input formentidade01'}),
            'prazo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prazo em dias'}),
            'fiscal': forms.Select(attrs={'class': 'form-control'}),
            'entidade': forms.Select(attrs={'class': 'form-control'}),
        }

    input_formats = {
        'data': ['%Y-%m-%dT%H:%M']
    }

class ParecerForm(forms.ModelForm):
    class Meta:
        model = Parecer
        fields = ['parecer', 'data_parecer', 'fiscal', 'notificacao']
        widgets = {
            'parecer': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Digite o parecer'}),
            'data_parecer': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Data do Parecer','type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'fiscal': forms.Select(attrs={'class': 'form-control'}),
            'notificacao': forms.Select(attrs={'class': 'form-control'}),
        }

    input_formats = {
        'data_parecer': ['%Y-%m-%dT%H:%M']
    }


class ArquivoForm(forms.ModelForm):
    class Meta:
        model = Arquivo
        fields = ['arquivo', 'nome_arquivo', 'notificacao']
        widgets = {
            'arquivo': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Selecione o arquivo'}),
            'nome_arquivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Arquivo'}),
            'notificacao': forms.Select(attrs={'class': 'form-control'}),
        }
    
class CodigoVerificadorForm(forms.Form):
    codigo_verificador = forms.CharField(max_length=8, label='Código do Documento')


class LiberacaoForm(forms.ModelForm):
    class Meta:
        model = Liberacao
        fields = ['email', 'chave']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite o email'}),
            'chave': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': ' CNPJ ou CPF APENAS NUMEROS'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        chave = cleaned_data.get('chave')

        if chave:
            if len(str(chave)) == 11:
                cpf = chave
            elif len(str(chave)) == 14:
                cnpj = chave
            else:
                raise forms.ValidationError("A chave deve ter 11 dígitos (CPF) ou 14 dígitos (CNPJ).")
            
            if 'cnpj' in locals():
                entidade_existente = Entidade.objects.filter(cnpj=cnpj).exists()
                if not entidade_existente:
                    raise forms.ValidationError("Não existe uma Empresa notificada nesse CNPJ.")
                entidade_usuario = Entidade.objects.filter(cnpj=cnpj, usuario__isnull=False).exists()
                if entidade_usuario:
                    raise forms.ValidationError("Este CNPJ já está associado a um usuário.")

            if 'cpf' in locals():
                entidade_existente = Entidade.objects.filter(cpf=cpf).exists()
                if not entidade_existente:
                    raise forms.ValidationError("Não existe notificação para este CPF.")
                entidade_usuario = Entidade.objects.filter(cpf=cpf, usuario__isnull=False).exists()
                if entidade_usuario:
                    raise forms.ValidationError("Este CPF já está associado a um usuário.")
        
        return cleaned_data

    def save(self, commit=True):
        # Salva a instância do formulário no banco de dados
        instance = super().save(commit=False)
    
        
        if commit:
            instance.save()
        return instance