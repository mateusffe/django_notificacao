from django.urls import path
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

]