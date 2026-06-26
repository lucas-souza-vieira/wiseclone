# WiseClone 🌍💸

**Banco internacional simulado** — Projeto acadêmico de DevSecOps (INE5680 — Segurança em Computação, UFSC 2026-1)

## Sobre o Sistema

WiseClone é uma plataforma financeira internacional simulada (inspirada no Wise), que permite:

- Cadastro com carteiras em **8 moedas** (BRL, USD, EUR, GBP, JPY, ARS, CAD, CHF)
- **Transferências** internacionais com câmbio automático
- **Calculadora de câmbio** em tempo real
- **Histórico de transações** completo
- Dashboard com visão geral de saldos

> ⚠️ Este é um projeto **simulado e acadêmico**. Nenhum dado ou transação é real.

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11 + FastAPI 0.95.2 |
| ORM | SQLAlchemy 1.4 |
| Banco | PostgreSQL 13 |
| Auth | JWT (python-jose) |
| Frontend | HTML5 + CSS3 + JavaScript Vanilla |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## 🚀 Como Rodar Localmente

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado
- Docker Compose (v2 — embutido no Docker Desktop ou `sudo apt install docker-compose-v2`)

### 1. Subir os containers

```bash
# Dentro da pasta wiseclone/
docker compose up -d --build
```

Esse comando:
- Builda a imagem Python com o backend
- Sobe o PostgreSQL
- Sobe o Nginx servindo o frontend

### 2. Verificar se está tudo rodando

```bash
docker compose ps
```

Saída esperada:
```
NAME                 STATUS
wiseclone_api        Up
wiseclone_db         Up
wiseclone_frontend   Up
```

### 3. Acessar a aplicação

| Serviço | URL |
|---------|-----|
| 🌐 Frontend (app) | http://localhost:8080 |
| ⚡ API REST | http://localhost:8000 |
| 📖 Documentação interativa (Swagger) | http://localhost:8000/docs |
| 📋 Redoc | http://localhost:8000/redoc |

### 4. Criar uma conta e testar

1. Acesse **http://localhost:8080/register.html**
2. Preencha nome, e-mail e senha
3. Você será redirecionado para o **Dashboard** com suas 8 carteiras já criadas
4. Teste a página de **Câmbio** em http://localhost:8080/exchange.html
5. Crie um segundo usuário e teste **Transferência** entre eles

### 5. Verificar a API manualmente (opcional)

```bash
# Health check
curl http://localhost:8000/health

# Registrar usuário via curl
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Teste","email":"teste@email.com","password":"senha123"}'

# Ver taxas de câmbio (endpoint público)
curl http://localhost:8000/exchange/rates
```

### 6. Parar os containers

```bash
docker compose down          # para os containers
docker compose down -v       # para E remove o banco de dados
```

---

## Pipeline DevSecOps

| Etapa | Ferramenta | Descrição |
|-------|-----------|-----------|
| Secret Detection | Gitleaks | Varredura de credenciais no histórico de commits |
| SCA | pip-audit | CVEs em dependências Python |
| SAST | Bandit + Semgrep | Análise estática do código-fonte |
| IaC Scanning | Checkov + Trivy | Segurança em Dockerfile e docker-compose |
| DAST | OWASP ZAP | Testes dinâmicos contra a aplicação em execução |

O pipeline é acionado automaticamente a cada `git push` para `main` ou `develop`.

---

## Estrutura do Projeto

```
wiseclone/
├── backend/
│   ├── main.py              # Aplicação FastAPI principal
│   ├── config.py            # Configurações (⚠️ secrets hardcoded — intencional)
│   ├── models.py            # Modelos ORM (User, Account, Transaction)
│   ├── schemas.py           # Schemas Pydantic
│   ├── auth.py              # Autenticação JWT
│   ├── utils.py             # Utilitários (⚠️ subprocess shell=True — intencional)
│   ├── routes/
│   │   ├── auth_routes.py   # POST /auth/register, /auth/login, GET /auth/me
│   │   ├── accounts.py      # GET /accounts/ e /accounts/{id}
│   │   ├── transactions.py  # POST /transfer, GET /transactions, /search
│   │   └── exchange.py      # GET /rates, POST /convert
│   └── requirements.txt     # Dependências (⚠️ CVEs intencionais)
├── frontend/
│   ├── index.html           # Dashboard
│   ├── login.html           # Login
│   ├── register.html        # Cadastro
│   ├── transfer.html        # Transferência
│   ├── exchange.html        # Calculadora de câmbio
│   ├── css/style.css        # Design system
│   └── js/app.js            # Lógica frontend
├── relatorio/
│   └── relatorio.md         # Relatório técnico DevSecOps
├── Dockerfile               # (⚠️ sem USER, sem HEALTHCHECK — intencional)
├── docker-compose.yml       # (⚠️ porta 5432 exposta, senha fraca — intencional)
└── .github/
    └── workflows/
        └── devsecops.yml    # Pipeline CI/CD completo
```

---

## Aviso de Segurança Educacional

Este projeto foi desenvolvido **intencionalmente** com vulnerabilidades para fins acadêmicos de análise de segurança. As vulnerabilidades incluem:

| Vulnerabilidade | Arquivo | Detectada por |
|----------------|---------|---------------|
| API Key hardcoded | `backend/config.py` | Gitleaks |
| Dependências com CVEs | `backend/requirements.txt` | pip-audit |
| SQL Injection | `backend/routes/transactions.py` | Semgrep/Bandit |
| subprocess shell=True | `backend/utils.py` | Bandit B602 |
| Container como root | `Dockerfile` | Checkov CKV_DOCKER_8 |
| Porta PostgreSQL exposta | `docker-compose.yml` | Checkov |
| Stack trace na resposta | `backend/main.py` | OWASP ZAP |
