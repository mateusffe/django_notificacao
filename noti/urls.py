from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastrarempresa', views.forment),
    path('criarentidade', views.criaentidade),
    path('buscaempresa', views.buscaempresa, name='buscaempresa'),
    path('editarentidade/<int:pk>/', views.editarentidade, name='editarentidade'),
    path('alterarentidade/<int:pk>/', views.alterarentidade, name='alterarentidade'),
    path('deletarentidade/<int:pk>/', views.deletarentidade, name='deletarentidade'),
    path('visualizarentidade/<int:pk>/', views.visualizarentidade, name='visualizarentidade'),
    path('criarusuarioentidade', views.criaruserent),
    path('formcadastro', views.userent),
    path('sair', views.sair),
    path('indexcomum',views.indexcomum)

]