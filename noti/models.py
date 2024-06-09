import random
from django.db import models
from django.contrib.auth.models import User





class usuarioEntidade(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liberado = models.BooleanField(default=False)
    ESCOLHA_TIPO = (        ('Autonomo', 'autonomo'),
        ('Empresa', 'empresa')
    )
    escolha = models.CharField(max_length=10, choices=ESCOLHA_TIPO, default="A")

  
class Entidade(models.Model):
    razao_social = models.CharField(max_length=100, default=None)
    nome_fantasia = models.CharField(max_length=100, blank=True)
    cnpj = models.IntegerField(default=None ,null=True, blank=True)
    cpf = models.IntegerField(default=None ,null=True, blank=True)
    endereco = models.CharField(max_length=100)
    cp = models.CharField(max_length=50 ,null=True, blank=True)
    cnae = models.IntegerField(default=None, null=True, blank=True)
    usuario = models.OneToOneField(usuarioEntidade, on_delete=models.CASCADE, default=None,  blank=True, null=True)

class Fiscal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=256, null=True, blank=True)
    matricula = models.IntegerField(default=None)
    cpf = models.CharField(max_length=11, null=True, blank=True)



class Notificacao(models.Model):
    def gerar_codigo_verificador():
        return random.randint(10000000, 99999999)
    
    codigo_verificador = models.PositiveIntegerField(primary_key=True, unique=True, default=gerar_codigo_verificador)
    notif = models.PositiveIntegerField(default=None)
    data = models.DateTimeField(default=None)
    
    ESCOLHA_MOTIVO = (
        ('CAD', 'Sem Cadastro'),
        ('ALV', 'Sem Alvará'),
        ('DEB', 'Em Debito'),
        ('SB', 'Sem Baixa'),
    )
    
    motivo = models.CharField(max_length=5, choices=ESCOLHA_MOTIVO, default=None)
    observacao = models.CharField(max_length=500)
    regularidade = models.BooleanField(default=False)
    prazo = models.PositiveIntegerField(default=30)
    fiscal = models.ForeignKey('Fiscal', on_delete=models.PROTECT, default=None)
    entidade = models.ForeignKey('Entidade', on_delete=models.PROTECT, default=None)


class Parecer(models.Model):
    parecer = models.CharField(max_length=500)
    data_parecer = models.DateTimeField(default=None)
    fiscal = models.ForeignKey(Fiscal, on_delete=models.PROTECT)
    notificacao = models.ForeignKey(Notificacao, on_delete=models.PROTECT)


class Arquivo(models.Model):
    arquivo = models.FileField(upload_to='uploads/')
    nome_arquivo = models.CharField(max_length=20)
    notificacao = models.ForeignKey(Notificacao, on_delete=models.PROTECT)

