from django.forms import ModelForm
from .models import Entidade, Notificacao


class EntidadeForm(ModelForm):
     class Meta:
        model = Entidade
        fields = ['razao_social', 'nome_fantasia', 'cnpj', 'cpf', 'endereco', 'cp', 'cnae']


    