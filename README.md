# Sistema de Login com Django + Firebase

## Estrutura do Projeto

## Arquivos principais

### 1. `requirements.txt`
Lista das dependências do projeto:
- **Django**: framework principal.
- **firebase-admin**: comunicação com o Firebase.
- **gunicorn**: servidor WSGI para deploy.
- **python-dotenv**: para carregar variáveis de ambiente.

---

### 2. `.env`
Arquivo de configuração que guarda informações sensíveis:
- `DEBUG`: ativa/desativa o modo debug do Django.
- `DJANGO_SECRET_KEY`: chave secreta do Django.
- Variáveis do Firebase (`FIREBASE_API_KEY`, `FIREBASE_PROJECT_ID`, etc.).

---

### 3. `firebase_config.py`
Responsável por inicializar o Firebase Admin usando o arquivo `firebase-service-account.json`.

Funções principais:
- Verifica se o Firebase já foi inicializado.
- Carrega as credenciais do arquivo de serviço.
- Inicializa o app Firebase para uso no projeto.

---

### 4. `navbar.css`
Arquivo de estilos customizados para o sistema:
- Cores, botões, formulários e alertas.
- Estilo da **navbar** e da **página de autenticação**.
- Responsividade e animações (fade-in).

---

### 5. Templates (`.html`)
Arquivos de frontend com **Django Template Language**:
- **Navbar.html** → Layout principal com navbar.
- **home.html** → Página inicial, mostra se o usuário está logado.
- **login.html** → Formulário de login.
- **register.html** → Formulário de cadastro.

---

### 6. `admin.py`
Configura o Django Admin para gerenciar o **CustomUser**.  
Mostra informações como email, UID do Firebase e se o email foi verificado.

---

### 7. `apps.py`
Define a configuração do app `accounts`.

---

### 8. `forms.py`
Formulário de cadastro com validações:
- Checa se o usuário já existe (username/email).
- Confere se as senhas coincidem.
- Aplica regras de mínimo de caracteres.

---

### 9. `utils.py`
Funções auxiliares para autenticação no Firebase:
- `get_or_create_user` → Busca ou cria usuário no Django a partir do UID/email do Firebase.
- `firebase_sign_in` → Faz login no Firebase com email e senha.
- `firebase_sign_up` → Cria nova conta no Firebase.

---

### 10. `views.py`
Controla o fluxo das páginas:
- **home** → Renderiza a página inicial.
- **login_view** → Faz login com Firebase e autentica no Django.
- **register_view** → Cria conta no Firebase e registra no Django.
- **logout_view** → Finaliza a sessão.

---

### 11. `urls.py`
Define as rotas principais:
- `/` → Página inicial.
- `/login/` → Página de login.
- `/register/` → Página de cadastro.
- `/logout/` → Logout.
- `/admin/` → Painel administrativo.

---

## Fluxo de Funcionamento
1. O usuário acessa **login** ou **cadastro**.
2. O Django envia os dados para o **Firebase Authentication**.
3. Se sucesso → cria ou busca o usuário no banco do Django.
4. Usuário é autenticado no Django e pode navegar no sistema.
5. Logout finaliza a sessão.

---

## Style
- Baseado no **Bootstrap 5** com customizações no `navbar.css`.
- Design moderno: gradientes, sombras suaves, responsividade e animações.

---
