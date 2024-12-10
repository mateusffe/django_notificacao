from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .forms import ModelUsuarioCreateForm, ModelUsuarioChangeForm
from .models import ModelUsuario, Entidade, Notificacao, Parecer, Arquivo, Liberacao

# Register your models here.

@admin.register(ModelUsuario)
class ModelUsuarioAdmin(UserAdmin):
    add_form = ModelUsuarioCreateForm
    form = ModelUsuarioChangeForm
    model = ModelUsuario
    list_display = ('first_name', 'last_name', 'email', 'fone', 'is_staff', 'matricula')

    fieldsets = (
        (None, {'fields':('email', 'password')}),
        ('Informações Pessoais', {'fields':('first_name','last_name','fone', 'matricula')}),
        ('Permissões', {'fields':('is_active','is_staff','is_superuser','groups','user_permissions')}),
        ('Datas importantes',{'fields':('last_login','date_joined')}),
    )



admin.site.register(Entidade)
admin.site.register(Notificacao)
admin.site.register(Parecer)
admin.site.register(Arquivo)
admin.site.register(Liberacao)
