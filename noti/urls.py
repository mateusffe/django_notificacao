from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastrarempresa', views.forment),
    path('criaentidade', views.criaentidade),
    path('buscaempresa', views.buscaempresa, name='buscaempresa'),
    path('editarentidade/<int:pk>/', views.editarentidade, name='editarentidade'),
    path('alterarentidade/<int:pk>/', views.alterarentidade, name='alterarentidade'),
    path('deletarentidade/<int:pk>/', views.deletarentidade, name='deletarentidade'),
    path('visualizarentidade/<int:pk>/', views.visualizarentidade, name='visualizarentidade'),
    path('criarusuarioentidade', views.criaruserent),
    path('formcadastro', views.userent),
        path('indexcomum',views.indexcomum),
    path("accounts/", include("django.contrib.auth.urls"), name='loginoriginal'),
    path("login", views.loginredirect),
    path("notificar", views.CriarNotificacao, name='notificar'),
    path("salvarnotificacao", views.salvarnotificacao ),
    path('parecer', views.CriarParecer),
    path('salvarparecer', views.salvarparecer),
    path('buscanotificacao', views.buscanotificacao, name='buscanotificacao'),
    path('buscausuario', views.buscausuario, name='buscausuario'),
    path('visualizarnotificacao/<int:pk>/', views.visualizarnotificacao, name='visualizarnotificacao'),
]