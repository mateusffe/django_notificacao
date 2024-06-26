import random
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver




class usuarioEntidade(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuarioentidade')
    liberado = models.BooleanField(default=False)
    ESCOLHA_TIPO = (        ('Autonomo', 'autonomo'),
        ('Empresa', 'empresa')
    )
    escolha = models.CharField(max_length=10, choices=ESCOLHA_TIPO, default="A")

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.liberado:
            self.user.is_active = False
            self.user.save()
        super().save(*args, **kwargs)
    
    
@receiver(post_save, sender=usuarioEntidade)
def update_user_is_active(sender, instance, created, **kwargs):
     if instance.liberado and not instance.user.is_active:
        instance.user.is_active = True
        instance.user.save()


class Entidade(models.Model):
    razao_social = models.CharField(max_length=100, default=None)
    nome_fantasia = models.CharField(max_length=100, blank=True)
    cnpj = models.IntegerField(default=None ,null=True, blank=True)
    cpf = models.IntegerField(default=None ,null=True, blank=True)
    endereco = models.CharField(max_length=100)
    cp = models.CharField(max_length=50 ,null=True, blank=True)
    cnae = models.IntegerField(default=None, null=True, blank=True)
    usuario = models.OneToOneField(usuarioEntidade, on_delete=models.SET_NULL, default=None,  blank=True, null=True)

    def __str__(self):
        return self.razao_social

class Fiscal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=256, null=True, blank=True)
    matricula = models.IntegerField(default=None)
    cpf = models.CharField(max_length=11, null=True, blank=True)

    def __str__(self):
        return self.nome if self.nome else "Fiscal sem nome"

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
    
    def __str__(self):
        return str(self.notif)
    
    def format_data(self):
        return self.data.strftime("%d/%m/%Y %H:%M")

class Parecer(models.Model):
    parecer = models.CharField(max_length=500)
    data_parecer = models.DateTimeField(default=None)
    fiscal = models.ForeignKey(Fiscal, on_delete=models.PROTECT)
    notificacao = models.ForeignKey(Notificacao, on_delete=models.PROTECT)

    def __str__(self):
        return self.notificacao

class Arquivo(models.Model):
    arquivo = models.FileField(upload_to='uploads/')
    nome_arquivo = models.CharField(max_length=20)
    notificacao = models.ForeignKey(Notificacao, on_delete=models.PROTECT)

    def __str__(self):
        return self.nome_arquivo

