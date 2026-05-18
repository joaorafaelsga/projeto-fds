from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
from biblioteca.models import Livro, Usuario, Emprestimo, AlertaLivroDisponivel


# PÁGINA: login.html

class PaginaLoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("login")
        User.objects.create_user(username="joao", password="senha123")

    # --- Carregamento ---
    def test_pagina_carrega(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_titulo_pagina(self):
        response = self.client.get(self.url)
        self.assertContains(response, "ReadMe - Login")

    def test_texto_log_in_visivel(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Log In")

    # --- Formulário ---
    def test_campo_usuario_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="usuario"')

    def test_campo_senha_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="senha"')

    def test_botao_submit_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'type="submit"')

    # --- Funcionamento do formulário ---
    def test_login_valido_redireciona_para_menu(self):
        response = self.client.post(self.url, {"usuario": "joao", "senha": "senha123"})
        self.assertRedirects(response, reverse("menu"))

    def test_login_senha_errada_exibe_erro(self):
        response = self.client.post(self.url, {"usuario": "joao", "senha": "errada"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "inválidos")

    def test_login_usuario_inexistente_exibe_erro(self):
        response = self.client.post(self.url, {"usuario": "ninguem", "senha": "123"})
        self.assertContains(response, "inválidos")


# PÁGINA: cadastro.html


class PaginaCadastroTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("cadastro")

    # --- Carregamento ---
    def test_pagina_carrega(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_titulo_pagina(self):
        response = self.client.get(self.url)
        self.assertContains(response, "ReadMe - Cadastro")

    def test_heading_cadastro_visivel(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Cadastro")

    # --- Links ---
    def test_link_para_login_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("login"))

    def test_link_para_menu_no_logo(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("menu"))

    # --- Formulário ---
    def test_campo_nome_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="nome"')

    def test_campo_email_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="email"')

    def test_campo_matricula_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="matricula"')

    def test_campo_usuario_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="usuario"')

    def test_campos_senha_presentes(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="senha"')
        self.assertContains(response, 'name="confirmar_senha"')

    def test_botao_criar_conta_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Criar conta")

    # --- Funcionamento do formulário ---
    def test_cadastro_valido_cria_usuario(self):
        self.client.post(self.url, {
            "nome": "Ana", "email": "ana@email.com", "matricula": "2024001",
            "usuario": "ana", "senha": "Senha@123", "confirmar_senha": "Senha@123",
        })
        self.assertTrue(User.objects.filter(username="ana").exists())

    def test_cadastro_valido_redireciona_para_menu(self):
        response = self.client.post(self.url, {
            "nome": "Ana", "email": "ana@email.com", "matricula": "2024001",
            "usuario": "ana", "senha": "Senha@123", "confirmar_senha": "Senha@123",
        })
        self.assertRedirects(response, reverse("menu"))

    def test_senhas_diferentes_exibe_erro(self):
        response = self.client.post(self.url, {
            "nome": "Ana", "email": "ana@email.com", "matricula": "2024001",
            "usuario": "ana", "senha": "Senha@123", "confirmar_senha": "Errada",
        })
        self.assertContains(response, "senhas não coincidem")

    def test_username_duplicado_exibe_erro(self):
        User.objects.create_user(username="ana", password="q")
        response = self.client.post(self.url, {
            "nome": "Ana", "email": "nova@email.com", "matricula": "2024002",
            "usuario": "ana", "senha": "Senha@123", "confirmar_senha": "Senha@123",
        })
        self.assertContains(response, "usuário já existe")

    def test_email_duplicado_exibe_erro(self):
        User.objects.create_user(username="outro", email="ana@email.com", password="q")
        response = self.client.post(self.url, {
            "nome": "Ana", "email": "ana@email.com", "matricula": "2024002",
            "usuario": "ana2", "senha": "Senha@123", "confirmar_senha": "Senha@123",
        })
        self.assertContains(response, "email já está em uso")



# PÁGINA: menu.html


class PaginaMenuTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("menu")
        self.auth_user = User.objects.create_user(username="menu_user", password="senha123")
        Usuario.objects.create(
            id_autenticado=self.auth_user,
            nome="Menu User",
            email="menu@email.com",
            matricula="M001"
        )
        self.client.login(username="menu_user", password="senha123")
        self.livro = Livro.objects.create(
            titulo="Dom Casmurro", autor="Machado de Assis", isbn="001"
        )

    # --- Carregamento ---
    def test_pagina_carrega(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_texto_pesquise_um_livro_visivel(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Pesquise um livro")

    # --- Formulário de busca ---
    def test_campo_busca_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="q"')

    def test_botao_pesquisar_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Pesquisar")

    # --- Funcionamento da busca ---
    def test_busca_livro_existente_exibe_titulo(self):
        response = self.client.get(self.url, {"q": "Dom Casmurro"})
        self.assertIsNotNone(response.context["livro"])
        self.assertContains(response, "Dom Casmurro")

    def test_busca_parcial_encontra_livro(self):
        response = self.client.get(self.url, {"q": "Dom"})
        self.assertIsNotNone(response.context["livro"])

    def test_busca_inexistente_exibe_erro(self):
        response = self.client.get(self.url, {"q": "Livro Fantasma"})
        self.assertContains(response, "Nenhum livro encontrado")

    def test_link_do_livro_encontrado_aponta_para_pagina_correta(self):
        response = self.client.get(self.url, {"q": "Dom Casmurro"})
        self.assertContains(response, reverse("livro", args=[self.livro.id]))



# PÁGINA: catalogo.html


class PaginaCatalogoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("catalogo")
        self.auth_user = User.objects.create_user(username="cat_user", password="senha123")
        Usuario.objects.create(
            id_autenticado=self.auth_user,
            nome="Cat User",
            email="cat@email.com",
            matricula="C001"
        )
        self.client.login(username="cat_user", password="senha123")
        self.livro1 = Livro.objects.create(
            titulo="O Cortico", autor="Aluisio Azevedo", isbn="002", disponivel=True
        )
        self.livro2 = Livro.objects.create(
            titulo="Iracema", autor="Jose de Alencar", isbn="003", disponivel=False
        )

    # --- Carregamento ---
    def test_pagina_carrega(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_heading_livros_disponiveis(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Livros")

    def test_todos_os_livros_aparecem(self):
        response = self.client.get(self.url)
        self.assertContains(response, "O Cortico")
        self.assertContains(response, "Iracema")

    def test_badge_disponivel_aparece(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Disponível")

    def test_badge_reservado_aparece(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Reservado")

    def test_catalogo_vazio_exibe_mensagem(self):
        Livro.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "Nenhum livro cadastrado")

    # --- Links ---
    def test_cada_livro_tem_link_para_sua_pagina(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("livro", args=[self.livro1.id]))
        self.assertContains(response, reverse("livro", args=[self.livro2.id]))



# PÁGINA: livro.html


class PaginaLivroTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.livro_disponivel = Livro.objects.create(
            titulo="Memorias Postumas", autor="Machado de Assis",
            isbn="004", quantidade=2, disponivel=True
        )
        self.livro_esgotado = Livro.objects.create(
            titulo="Vidas Secas", autor="Graciliano Ramos",
            isbn="005", quantidade=0, disponivel=False
        )
        self.user = User.objects.create_user(username="leitor", password="senha123")
        self.usuario = Usuario.objects.create(
            id_autenticado=self.user,
            nome="Leitor Teste",
            email="leitor@teste.com",
            matricula="L001"
        )

    def _url(self, livro):
        return reverse("livro", args=[livro.id])

    # --- Carregamento ---
    def test_pagina_livro_disponivel_carrega(self):
        response = self.client.get(self._url(self.livro_disponivel))
        self.assertEqual(response.status_code, 200)

    def test_pagina_livro_esgotado_carrega(self):
        response = self.client.get(self._url(self.livro_esgotado))
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_titulo_do_livro_visivel(self):
        response = self.client.get(self._url(self.livro_disponivel))
        self.assertContains(response, "Memorias Postumas")

    def test_autor_do_livro_visivel(self):
        response = self.client.get(self._url(self.livro_disponivel))
        self.assertContains(response, "Machado de Assis")

    def test_isbn_visivel(self):
        response = self.client.get(self._url(self.livro_disponivel))
        self.assertContains(response, "004")

    # --- Botões condicionais ---
    def test_botao_reservar_aparece_quando_disponivel(self):
        response = self.client.get(self._url(self.livro_disponivel))
        self.assertContains(response, "Reservar")

    def test_tag_disponivel_aparece_quando_disponivel(self):
        response = self.client.get(self._url(self.livro_disponivel))
        self.assertContains(response, "Disponível")

    def test_botao_ativar_alerta_aparece_quando_esgotado(self):
        response = self.client.get(self._url(self.livro_esgotado))
        self.assertContains(response, "Ativar alerta")

    def test_tag_reservado_aparece_quando_esgotado(self):
        response = self.client.get(self._url(self.livro_esgotado))
        self.assertContains(response, "Reservado")

    # --- Formulário de alerta ---
    def test_formulario_alerta_aponta_para_url_correta(self):
        response = self.client.get(self._url(self.livro_esgotado))
        self.assertContains(response, reverse("criar_alerta", args=[self.livro_esgotado.id]))

    def test_alerta_requer_login(self):
        url = reverse("criar_alerta", args=[self.livro_esgotado.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_alerta_criado_com_usuario_logado(self):
        self.client.login(username="leitor", password="senha123")
        url = reverse("criar_alerta", args=[self.livro_esgotado.id])
        self.client.post(url)
        self.assertTrue(
            AlertaLivroDisponivel.objects.filter(
                usuario=self.user, livro=self.livro_esgotado
            ).exists()
        )

    # --- Reserva / Empréstimo ---
    def test_reservar_livro_disponivel_cria_emprestimo(self):
        self.client.login(username="leitor", password="senha123")
        url = reverse("reservar_livro", args=[self.livro_disponivel.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("meusLivros"))
        self.assertTrue(
            Emprestimo.objects.filter(
                livro=self.livro_disponivel,
                usuario=self.usuario,
                devolvido=False
            ).exists()
        )
        self.livro_disponivel.refresh_from_db()
        self.assertEqual(self.livro_disponivel.quantidade, 1)
        self.assertTrue(self.livro_disponivel.disponivel)

    def test_reservar_livro_sem_login_redireciona(self):
        url = reverse("reservar_livro", args=[self.livro_disponivel.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_reservar_livro_esgotado_falha(self):
        self.client.login(username="leitor", password="senha123")
        url = reverse("reservar_livro", args=[self.livro_esgotado.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("livro", args=[self.livro_esgotado.id]))

    def test_reservar_livro_ja_emprestado_redireciona(self):
        Emprestimo.objects.create(
            livro=self.livro_disponivel,
            usuario=self.usuario,
            dataDevolucao=date.today() + timedelta(days=7)
        )
        self.client.login(username="leitor", password="senha123")
        url = reverse("reservar_livro", args=[self.livro_disponivel.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("meusLivros"))



# PÁGINA: meusLivros.html


class PaginaMeusLivrosTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("meusLivros")
        self.auth_user = User.objects.create_user(username="pedro", password="senha123")
        self.usuario = Usuario.objects.create(
            id_autenticado=self.auth_user,
            nome="Pedro", email="pedro@email.com", matricula="2024003"
        )
        self.client.login(username="pedro", password="senha123")
        self.livro = Livro.objects.create(
            titulo="Grande Sertao Veredas", autor="Guimaraes Rosa", isbn="006"
        )
        self.emprestimo = Emprestimo.objects.create(
            livro=self.livro,
            usuario=self.usuario,
            dataEmprestimo=date.today() - timedelta(days=3),
            dataDevolucao=date.today() + timedelta(days=7),
        )

    # --- Carregamento ---
    def test_pagina_carrega(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_heading_meus_livros_visivel(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Meus Livros")

    def test_titulo_do_livro_emprestado_aparece(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Grande Sertao Veredas")

    def test_dias_restantes_aparecem(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Restam")
        self.assertContains(response, "dias em seu empr")

    def test_barra_de_progresso_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, "barra-progresso")

    def test_botao_renovar_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Renovar")

    # --- Estado vencido ---
    def test_emprestimo_vencido_exibe_mensagem(self):
        self.emprestimo.dataDevolucao = date.today() - timedelta(days=1)
        self.emprestimo.save()
        response = self.client.get(self.url)
        self.assertContains(response, "chegou ao fim")

    # --- Lista vazia ---
    def test_sem_emprestimos_exibe_mensagem(self):
        Emprestimo.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "Nenhum empr")

       
# PÁGINA: profDiciplinaCategoria.html


class PaginaProfDisciplinaCategoriaTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("profdisciplinacategoria")
        self.auth_user = User.objects.create_user(username="prof", password="senha123")
        Usuario.objects.create(
            id_autenticado=self.auth_user,
            nome="Professor",
            email="prof@email.com",
            matricula="P001",
            is_professor=True
        )
        self.client.login(username="prof", password="senha123")

    # --- Carregamento ---
    def test_pagina_carrega(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_titulo_pagina(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Biblioteca")

    def test_heading_gerenciador_visivel(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Gerenciador de Biblioteca")

    def test_boas_vindas_professor_visivel(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Bem vindo(a) professor(a)")

    # --- Seção Categorias ---
    def test_secao_categorias_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Categorias")

    def test_input_categoria_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'id="input-categoria"')

    def test_botao_adicionar_categoria_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Adicionar")

    # --- Seção Livros ---
    def test_secao_livros_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Livros")

    def test_input_titulo_livro_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'placeholder="Título do livro"')

    def test_input_autor_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'placeholder="Autor"')

    def test_select_categoria_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'id="select-categoria"')

    def test_botao_adicionar_livro_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Adicionar livro")