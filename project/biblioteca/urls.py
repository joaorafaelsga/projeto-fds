from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('menu/', views.menu, name='menu'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('livro/<int:id>/', views.livro, name='livro'),
    path('livro/<int:id>/alerta/', views.criar_alerta, name='criar_alerta'),
    path('livro/<int:id>/reservar/', views.reservar_livro, name='reservar_livro'),
    path('meus-livros/', views.meusLivros, name='meusLivros'),
    path('profdisciplinacategoria/', views.profdisciplinacategoria, name='profdisciplinacategoria'),
    path('indicar-livro/', views.indicar_livro, name='indicar_livro'),
    path('api/livros/', views.salvar_livros),
    path("alunos-com-livros/", views.alunos_com_livros, name="alunos_com_livros"),
    path('emprestimo/<int:id>/renovar/', views.renovar_livro, name='renovar_livro'),
    path('logout/', views.logout_view, name='logout'),
    path('professor/', views.professor_hub, name='professor_hub'),
]
