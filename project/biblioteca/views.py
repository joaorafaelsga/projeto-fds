import json
from django.shortcuts import render, redirect, get_object_or_404


from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Livro, Usuario, Emprestimo, AlertaLivroDisponivel, IndicacaoLivros
from django.http import JsonResponse
from django.contrib.auth import logout

# Create your views here.

def is_professor(user):
    if not user.is_authenticated:
        return False

    return Usuario.objects.filter(
        id_autenticado=user,
        is_professor=True
    ).exists()

def home(request):
    livros = Livro.objects.all()[:20]

    context = {
        'livros': livros,
    }

    return render(request, 'biblioteca/home.html', context)

def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        matricula = request.POST.get('matricula')
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            return render(request, 'cadastro.html', {'erro': 'As senhas não coincidem.'})

        if User.objects.filter(username=usuario).exists():
            return render(request, 'cadastro.html', {'erro': 'Esse nome de usuário já existe.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'cadastro.html', {'erro': 'Esse email já está em uso.'})
        
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'cadastro.html', {'erro': 'Esse email já está cadastrado na biblioteca.'})
        

        user = User.objects.create_user(
            username=usuario,
            email=email,
            password=senha
        )

        Usuario.objects.create(
            id_autenticado=user,
            nome=nome,
            email=email,
            matricula=matricula
        )

        login(request, user)
        return redirect('menu')

    return render(request, 'cadastro.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')

        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            login(request, user)

            usuario_obj = Usuario.objects.filter(id_autenticado=user).first()

            if usuario_obj and usuario_obj.is_professor:
                return redirect('professor_hub')

            return redirect('menu')
        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha inválidos.'})
    
    return render(request, 'login.html')

def alunos_com_livros(request):
    emprestimos_ativos = Emprestimo.objects.filter(devolvido=False).select_related("usuario", "livro")

    return render(request, "biblioteca/alunos_com_livros.html", {
        "emprestimos_ativos": emprestimos_ativos
    })

def menu(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Faça login para acessar o menu.')
        return redirect('login')

    livro = None
    erro = None
    query = request.GET.get('q', '')

    if query:
        try:
            livro = Livro.objects.filter(titulo__icontains=query).first()
            if not livro:
                erro = 'Nenhum livro encontrado.'
        except:
            erro = 'Erro na pesquisa.'

    return render(request, 'biblioteca/menu.html', {
        'livro': livro,
        'erro': erro,
        'query': query
    })

def catalogo(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Faça login para acessar o catálogo.')
        return redirect('login')

    livros = Livro.objects.all()
    return render(request, 'biblioteca/catalogo.html', {'livros': livros})

def livro(request, id):
    livro = Livro.objects.get(id=id)
    return render(request, 'biblioteca/livro.html', {'livro': livro})

@login_required
def reservar_livro(request, id):
    livro = get_object_or_404(Livro, id=id)

    if livro.quantidade <= 0 or not livro.disponivel:
        messages.error(request, 'Este livro não está disponível para empréstimo.')
        return redirect('livro', id=livro.id)

    usuario = Usuario.objects.filter(id_autenticado=request.user).first()
    if not usuario:
        messages.warning(request, 'Seu usuário não possui cadastro de aluno vinculado.')
        return redirect('cadastro')

    emprestimo_existente = Emprestimo.objects.filter(
        livro=livro,
        usuario=usuario,
        devolvido=False
    ).first()

    if emprestimo_existente:
        messages.warning(request, 'Você já possui um empréstimo ativo para este livro.')
        return redirect('meusLivros')

    Emprestimo.objects.create(
        livro=livro,
        usuario=usuario
    )

    livro.quantidade -= 1
    if livro.quantidade <= 0:
        livro.disponivel = False
    livro.save()

    messages.success(request, f'Livro "{livro.titulo}" reservado com sucesso!')
    return redirect('meusLivros')

def meusLivros(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Faça login para acessar seus livros.')
        return redirect('login')

    usuario = Usuario.objects.filter(id_autenticado=request.user).first()

    if not usuario:
        messages.warning(request, 'Seu usuário não possui cadastro de aluno vinculado.')
        return render(request, 'biblioteca/meusLivros.html', {
            'emprestimos': []
        })

    emprestimos = Emprestimo.objects.filter(
        usuario=usuario,
        devolvido=False
    )

    return render(request, 'biblioteca/meusLivros.html', {
        'emprestimos': emprestimos
    })

@login_required
def criar_alerta(request, id):
    livro = Livro.objects.get(id=id)

    alerta, criado = AlertaLivroDisponivel.objects.get_or_create(
        usuario=request.user,
        livro=livro,
        defaults={'ativo': True}
    )

    if not criado and not alerta.ativo:
        alerta.ativo = True
        alerta.save()

    messages.success(request, 'Alerta de disponibilidade ativado com sucesso.')
    return redirect('livro', id=livro.id)

@login_required(login_url='login')
@user_passes_test(is_professor, login_url='login')
def professor_hub(request):
    return render(request, 'biblioteca/professor.html')

@login_required(login_url='login')
@user_passes_test(is_professor, login_url='login')
def profdisciplinacategoria(request):
    return render(request, 'biblioteca/profdisciplinacategoria.html')

def salvar_livros(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        for item in data:
            Livro.objects.create(
                titulo=item['titulo'],
                autor=item['autor'],
                quantidade=1
            )

        return JsonResponse({'status': 'ok'})
    
@login_required
def renovar_livro(request, id):
    if request.method == "POST":
        usuario = Usuario.objects.filter(id_autenticado=request.user).first()

        if not usuario:
            return redirect('cadastro')

        emprestimo = get_object_or_404(
            Emprestimo,
            id=id,
            usuario=usuario
        )

        emprestimo.renovar()

    return redirect('meusLivros')

@login_required
def indicar_livro(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        autor = request.POST.get('autor')

        if not titulo or not autor:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect('profdisciplinacategoria')

        IndicacaoLivros.objects.create(
            professor=request.user,
            titulo=titulo,
            autor=autor
        )
        
        messages.success(request, 'Indicação de livro enviada com sucesso!')
        return redirect('profdisciplinacategoria')
        
    return redirect('profdisciplinacategoria')