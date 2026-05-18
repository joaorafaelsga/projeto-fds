# Guia de Contribuição — ReadMe

Obrigado pelo interesse em contribuir com o **ReadMe**!  
Este guia foi feito para que qualquer pessoa consiga configurar o ambiente, entender o fluxo de trabalho e enviar contribuições de forma tranquila.

---

## Sobre o projeto

O **ReadMe** é um sistema de gerenciamento de acervo bibliotecário acadêmico desenvolvido com **Django 6**, **PostgreSQL**, **Cloudinary** (mídia) e hospedado na **Azure**.  
O objetivo é oferecer uma plataforma simples e intuitiva para consulta, reserva e administração de livros.

**Links úteis:**
- Deploy: [https://readme.azurewebsites.net/](https://readme.azurewebsites.net/)
- JIRA: [https://pvcb-cesar.atlassian.net/jira/software/projects/FDS/boards/2/backlog](https://pvcb-cesar.atlassian.net/jira/software/projects/FDS/boards/2/backlog)
- Figma: [Protótipos de interface](https://www.figma.com/site/eSIqH0rLKXhKKrPWGQ9nS3/ReadMe)

---

## Antes de começar

Certifique-se de ter instalado:

- **Python 3.13+**
- **Git**
- **PostgreSQL 15+** (ou Docker para subir um container local)
- **Chromium** (necessário para os testes E2E com Selenium)

---

## Configurando o ambiente local

### 1. Clone o repositório

```bash
git clone https://github.com/pedrovcb/ReadMe.git
cd ReadMe/project
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv ../.venv
source ../.venv/bin/activate      # Linux / macOS
# ou
..\.venv\Scripts\activate         # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na pasta `project/` com:

```bash
DATABASE_URL=postgres://usuario:senha@localhost:5432/readme_db
SECRET_KEY=uma-chave-secreta-local-aleatoria
DEBUG=True
CLOUDINARY_URL=cloudinary://sua-url-do-cloudinary   # opcional para desenvolvimento
```

Todas as informações do `.env` devem ser configuradas de acordo com seus bancos de dados no **Neon PostgreSQL** e **Cloudinary**

### 5. Rode as migrações

```bash
python manage.py migrate
```

### 6. Crie um superusuário (necessário para acessar admin)

```bash
python manage.py createsuperuser
```

---

## Rodando o projeto

```bash
python manage.py runserver
```

Acesse em: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Testes

O projeto possui dois conjuntos de testes:

### Testes unitários / funcionais

```bash
python manage.py test biblioteca.tests --verbosity=2
```

### Testes E2E (Selenium)

```bash
python manage.py test biblioteca.testsUsuario --verbosity=2
```

### Rodar todos de uma vez

```bash
python manage.py test biblioteca --verbosity=2
```

> Importante: os testes E2E utilizam o Chromium em modo headless. Certifique-se de que o executável `chromium` esteja disponível em `/usr/bin/chromium` (Linux) ou ajuste o caminho no arquivo `testsUsuario.py` caso necessário.

---

## Como contribuir

### 1. Nunca commite direto na `main`

Sempre trabalhe em uma branch separada. Isso mantém o histórico limpo, evita conflitos e permite code review.

```bash
git checkout -b feature/nome-da-sua-historia
```

Bons exemplos de nomes de branch:
- `feature/reserva-livro`
- `fix/correcao-login-redirect`
- `test/adiciona-teste-emprestimo`

### 2. Desenvolva e teste localmente

Antes de abrir um Pull Request, garanta que **todos os testes unitários estejam passando** na sua máquina.

### 3. Commits descritivos

Escreva mensagens de commit que expliquem **o que** foi feito e **por que**:

```bash
git commit -m "feat: adiciona fluxo de reserva de livro para alunos

- cria view reservar_livro com validações de estoque e duplicidade
- adiciona rota e corrige template para enviar POST
- inclui testes unitários cobrindo cenários de sucesso e erro"
```

### 4. Abra um Pull Request

```bash
git push origin feature/nome-da-sua-historia
```

No GitHub, abra um PR para a branch `main` descrevendo:
- O que foi alterado
- Como testar
- Prints ou evidências (se houver mudanças visuais)

### 5. Code review

Solicite a revisão de pelo menos **um membro da equipe**.  
O merge só deve acontecer após aprovação.

---

## Padrões de código

- Siga o estilo existente do projeto.
- Mantenha **views** em `views.py`, **modelos** em `models.py` e **templates** em `templates/biblioteca/`.
- Funcionalidades novas devem vir acompanhadas de testes no arquivo apropriado:
  - Lógica de views/models → `tests.py`
  - Fluxos de usuário no navegador → `testsUsuario.py`
- Prefira código legível a comentários excessivos. Comente apenas trechos de lógica complexa ou regras de negócio não óbvias.

---

## CI/CD e Deploy

O projeto utiliza **GitHub Actions** com o seguinte fluxo:

1. Ao fazer `push` para a `main`, a pipeline roda os **testes** automaticamente.
2. Se os testes passarem, o deploy para a **Azure Web App** acontece de forma automática.


---

## Gestão de tarefas

- Utilizamos o **JIRA** para organizar sprints, histórias de usuário e backlog.
- A prática de **Programação em Par** é incentivada, especialmente para funcionalidades mais complexas.

---

## Reportando bugs

Encontrou algo estranho? Abra uma **Issue no GitHub** incluindo:

1. Descrição do problema
2. Passos para reproduzir
3. Comportamento esperado vs. comportamento atual
4. Screenshots, logs ou mensagens de erro (se houver)

---

## Dúvidas?

Ficou com alguma dúvida que não está neste guia?  
Sinta-se à vontade para abrir uma Issue ou entrar em contato com a equipe.

Obrigado pela atenção!
