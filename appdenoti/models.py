from django.db import models
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import datetime
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.

class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Super usuário precisa ter is_superuser=True')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Super usuário precisa ter is_staff=True')
        
        return self._create_user(email, password, **extra_fields)


class ModelUsuario(AbstractUser):
    email = models.EmailField('E-mail', unique=True)
    fone = models.CharField('Telefone', max_length=15)
    is_staff = models.BooleanField('Membro de equipe', default=False)
    matricula = models.CharField('Matricula', max_length=15, blank=True, unique=True)
    liberado = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'fone', 'matricula']

    def __str__(self):
        return self.email

    objects = UsuarioManager()


class Entidade(models.Model):
    razao_social = models.CharField(max_length=100, default="")
    nome_fantasia = models.CharField(max_length=100, blank=True, default="")
    cnpj = models.IntegerField(blank=True, unique=True, null=True, default="")
    cpf = models.IntegerField(blank=True, unique=True, null=True, default="")
    endereco = models.CharField(max_length=100,default="")
    codigo_profissional = models.CharField(max_length=50, blank=True, default="")
    cnae = models.IntegerField(default="", null=True, blank=True,)
    usuario = models.OneToOneField(ModelUsuario, on_delete=models.SET_NULL,  blank=True, null=True)

    def __str__(self):
        return self.razao_social

class Notificacao(models.Model):
    def gerar_codigo_verificador():
        return random.randint(10000000, 99999999)

    codigo_verificador = models.PositiveIntegerField(primary_key=True, unique=True, default=gerar_codigo_verificador)
    notif = models.PositiveIntegerField(default=None,blank=True, null=True)
    data = models.DateTimeField(blank=True, null=True)

    ESCOLHA_MOTIVO = (
        ('CAD', 'Sem Cadastro'),
        ('ALV', 'Sem Alvará'),
        ('DEB', 'Em Debito'),
        ('SB', 'Sem Baixa'),
    )

    motivo = models.CharField(max_length=5, choices=ESCOLHA_MOTIVO,blank=True,default="Sem Cadastro")
    observacao = models.CharField(max_length=500,default='Sem Observação',blank=True)
    regularidade = models.BooleanField(default=False, null=True)
    prazo = models.PositiveIntegerField(default=30, null=True)
    fiscal = models.ForeignKey(ModelUsuario, on_delete=models.PROTECT, default='', blank=True, null=True)
    entidade = models.ForeignKey(Entidade , on_delete=models.PROTECT, default='',blank=True, null=True)

    def __str__(self):
        return str(self.notif)

    def format_data(self):
        return self.data.strftime("%d/%m/%Y %H:%M")

class Parecer(models.Model):
    parecer = models.TextField(max_length=500)
    data_parecer = models.DateTimeField(default=None, null=True)
    fiscal = models.ForeignKey(ModelUsuario, on_delete=models.PROTECT)
    notificacao = models.ForeignKey(Notificacao, on_delete=models.PROTECT)

    def __str__(self):
        return self.notificacao

    def format_data(self):
        return self.data.strftime("%d/%m/%Y %H:%M")


class Arquivo(models.Model):
    arquivo = models.FileField(upload_to='uploads/')
    nome_arquivo = models.CharField(max_length=50, unique=True)
    notificacao = models.ForeignKey(Notificacao, on_delete=models.PROTECT)

    def __str__(self):
        return self.nome_arquivo


class Liberacao(models.Model):
    email = models.EmailField('E-mail', null=False,blank=False, default="", primary_key=True)
    chave = models.IntegerField('Chave')
    data_criacao = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.email