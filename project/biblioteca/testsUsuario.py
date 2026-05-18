from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
from django.db import transaction
from biblioteca.models import Livro, Usuario, Emprestimo
from datetime import date, timedelta


class ExperienciaUsuarioE2ETestCase(StaticLiveServerTestCase):
    """
    Testes de Sistema (E2E) que simulam a experiência real do usuário
    no navegador, cobrindo fluxos de login, busca, catálogo,
    reserva/alerta e "Meus Livros".
    """

    def setUp(self):
        # Criação de dados de teste commitados para que o servidor live
        # (que roda em thread separada) consiga enxergá-los.
        self.user = User.objects.create_user(
            username="teste_e2e",
            password="Senha@123"
        )
        self.usuario = Usuario.objects.create(
            id_autenticado=self.user,
            nome="Usuário Teste",
            email="teste@e2e.com",
            matricula="E2E001"
        )

        self.livro_disponivel = Livro.objects.create(
            titulo="Aprendendo Git",
            autor="Loiane Groner",
            isbn="111",
            quantidade=2,
            disponivel=True
        )

        self.livro_esgotado = Livro.objects.create(
            titulo="Engenharia de Software",
            autor="Ian Sommerville",
            isbn="222",
            quantidade=0,
            disponivel=False
        )

        self.emprestimo = Emprestimo.objects.create(
            livro=self.livro_disponivel,
            usuario=self.usuario,
            dataEmprestimo=date.today() - timedelta(days=3),
            dataDevolucao=date.today() + timedelta(days=7),
            devolvido=False
        )

        # Commit explícito para que o servidor live visualize os dados
        transaction.commit()

        # Configuração do navegador headless
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = "/usr/bin/chromium"

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)

    def tearDown(self):
        self.driver.quit()
        super().tearDown()

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _fazer_login(self, username="teste_e2e", password="Senha@123"):
        """Realiza login via interface web e aguarda o redirecionamento."""
        self.driver.get(f"{self.live_server_url}/login/")

        campo_usuario = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "usuario"))
        )
        campo_senha = self.driver.find_element(By.NAME, "senha")
        botao = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        campo_usuario.send_keys(username)
        campo_senha.send_keys(password)
        botao.click()

        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/menu/")
        )

    # ------------------------------------------------------------------
    # Cenário A – Login com sucesso
    # ------------------------------------------------------------------
    def test_a_login_com_sucesso(self):
        self.driver.get(f"{self.live_server_url}/login/")

        campo_usuario = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "usuario"))
        )
        campo_senha = self.driver.find_element(By.NAME, "senha")
        botao = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        campo_usuario.send_keys("teste_e2e")
        campo_senha.send_keys("Senha@123")
        botao.click()

        WebDriverWait(self.driver, 10).until(EC.url_contains("/menu/"))

        busca = self.driver.find_element(By.NAME, "q")
        self.assertTrue(busca.is_displayed())

    # ------------------------------------------------------------------
    # Cenário B – Busca de livro no menu
    # ------------------------------------------------------------------
    def test_b_busca_livro_no_menu(self):
        self._fazer_login()

        campo_busca = self.driver.find_element(By.NAME, "q")
        botao_pesquisar = self.driver.find_element(
            By.XPATH, "//button[contains(text(),'Pesquisar')]"
        )

        campo_busca.send_keys("Aprendendo")
        botao_pesquisar.click()

        resultado = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Aprendendo Git')]")
            )
        )
        self.assertIsNotNone(resultado)

    # ------------------------------------------------------------------
    # Cenário C – Navegação pelo catálogo
    # ------------------------------------------------------------------
    def test_c_navegacao_catalogo(self):
        self._fazer_login()

        link_catalogo = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Catálogo"))
        )
        link_catalogo.click()

        WebDriverWait(self.driver, 10).until(EC.url_contains("/catalogo/"))
        self.assertIn("Livros Disponíveis", self.driver.page_source)

        livro_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'livro-card') and contains(., 'Aprendendo Git')]")
            )
        )
        livro_link.click()

        WebDriverWait(self.driver, 10).until(EC.url_contains("/livro/"))
        self.assertIn("Aprendendo Git", self.driver.page_source)

    # ------------------------------------------------------------------
    # Cenário D – Livro disponível: exibe botão "Reservar"
    # ------------------------------------------------------------------
    def test_d_livro_disponivel_exibe_reservar(self):
        self._fazer_login()

        self.driver.get(
            f"{self.live_server_url}/livro/{self.livro_disponivel.id}/"
        )

        tag = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "disponivel"))
        )
        self.assertEqual(tag.text, "Disponível")

        botao = self.driver.find_element(By.CLASS_NAME, "btn-reservar")
        self.assertEqual(botao.text, "Reservar")
        self.assertTrue(botao.is_displayed())

    # ------------------------------------------------------------------
    # Cenário E – Livro esgotado: ativar alerta de disponibilidade
    # ------------------------------------------------------------------
    def test_e_livro_esgotado_ativar_alerta(self):
        self._fazer_login()

        self.driver.get(
            f"{self.live_server_url}/livro/{self.livro_esgotado.id}/"
        )

        tag = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "reservado"))
        )
        self.assertEqual(tag.text, "Reservado")

        botao_alerta = self.driver.find_element(By.CLASS_NAME, "btn-alertar")
        self.assertEqual(botao_alerta.text, "Ativar alerta")

        botao_alerta.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Alerta de disponibilidade ativado com sucesso.')]")
            )
        )

        self.assertIn("/livro/", self.driver.current_url)

    # ------------------------------------------------------------------
    # Cenário F – Login inválido exibe erro
    # ------------------------------------------------------------------
    def test_f_login_invalido_exibe_erro(self):
        self.driver.get(f"{self.live_server_url}/login/")

        campo_usuario = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "usuario"))
        )
        campo_senha = self.driver.find_element(By.NAME, "senha")
        botao = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        campo_usuario.send_keys("usuario_errado")
        campo_senha.send_keys("senha_errada")
        botao.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'inválidos')]")
            )
        )

        self.assertIn("/login/", self.driver.current_url)

    # ------------------------------------------------------------------
    # Cenário G – "Meus Livros" após empréstimo
    # ------------------------------------------------------------------
    def test_g_meus_livros_apos_emprestimo(self):
        self._fazer_login()

        link_meus = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Meus Livros"))
        )
        link_meus.click()

        WebDriverWait(self.driver, 10).until(EC.url_contains("/meus-livros/"))

        self.assertIn("Aprendendo Git", self.driver.page_source)
        self.assertIn("Restam", self.driver.page_source)
        self.assertIn("dias em seu empréstimo!", self.driver.page_source)

        barra = self.driver.find_element(By.CLASS_NAME, "barra-progresso")
        self.assertTrue(barra.is_displayed())

        botao_renovar = self.driver.find_element(By.CLASS_NAME, "btn-renovar")
        self.assertEqual(botao_renovar.text, "Renovar")
        self.assertTrue(botao_renovar.is_displayed())
