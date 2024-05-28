from django import forms
from django.forms import ModelForm
from .models import Entidade, Notificacao, usuarioEntidade
from django.contrib.auth.models import User


class EntidadeForm(ModelForm):
     class Meta:
        model = Entidade
        fields = ['razao_social', 'nome_fantasia', 'cnpj', 'cpf', 'endereco', 'cp', 'cnae']


class UserEntidade(ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    cnpj = forms.CharField(max_length=18, required=False)
    cpf = forms.CharField(max_length=14, required=False)
    

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean(self):
        cleaned_data = super().clean()
        cnpj = cleaned_data.get('cnpj')
        cpf = cleaned_data.get('cpf')

        if not cnpj and not cpf:
            raise forms.ValidationError("Você deve fornecer pelo menos um CPF ou CNPJ.")

        if cnpj:
            entidade_existente = Entidade.objects.filter(cnpj=cnpj).exists()
            if not entidade_existente:
                raise forms.ValidationError("Não existe uma Entidade cadastrada com este CNPJ.")

        if cpf:
            entidade_existente = Entidade.objects.filter(cpf=cpf).exists()
            if not entidade_existente:
                raise forms.ValidationError("Não existe uma Entidade cadastrada com este CPF.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

            usuario_entidade = usuarioEntidade.objects.create(
                user=user
            )

            cnpj = self.cleaned_data['cnpj']
            cpf = self.cleaned_data['cpf']

            if cnpj:
                entidade = Entidade.objects.filter(cnpj=cnpj).first()
            else:
                entidade = Entidade.objects.filter(cpf=cpf).first()

            if entidade:
                entidade.usuario = usuario_entidade
                entidade.save()

            # Retornando o ID do usuarioEntidade criado
            return user, usuario_entidade.id

        return user


    
