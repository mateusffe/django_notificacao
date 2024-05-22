from django.contrib import admin
from .models import Fiscal, usuarioEntidade, Parecer, Arquivo, Entidade, Notificacao
# Register your models here.


admin.site.register(Fiscal)
admin.site.register(usuarioEntidade)
admin.site.register(Parecer)
admin.site.register(Arquivo)
admin.site.register(Entidade)
admin.site.register(Notificacao)



