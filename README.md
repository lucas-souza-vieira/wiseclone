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

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11 + FastAPI |
| ORM | SQLAlchemy 1.4 |
| Banco | PostgreSQL 13 |
| Auth | JWT (python-jose) |
| Frontend | HTML5 + CSS3 + JavaScript (Vanilla) |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## Rodando Localmente

```bash
# Pré-requisitos: Docker e Docker Compose
docker-compose up -d --build

# Acessar:
# Frontend: http://localhost:80
# API:      http://localhost:8000
# Docs:     http://localhost:8000/docs
```

## Pipeline DevSecOps

| Etapa | Ferramenta | Descrição |
|-------|-----------|-----------|
| Secret Detection | Gitleaks | Varredura de credenciais no histórico |
| SCA | pip-audit | CVEs em dependências Python |
| SAST | Bandit + Semgrep | Análise estática do código |
| IaC Scanning | Checkov + Trivy | Segurança em Dockerfile e docker-compose |
| DAST | OWASP ZAP | Testes dinâmicos na aplicação em execução |

## Estrutura do Projeto

```
wiseclone/
├── backend/
│   ├── main.py              # Aplicação FastAPI principal
│   ├── config.py            # Configurações
│   ├── models.py            # Modelos ORM (User, Account, Transaction)
│   ├── schemas.py           # Schemas Pydantic
│   ├── auth.py              # Autenticação JWT
│   ├── utils.py             # Utilitários
│   ├── routes/              # Endpoints da API
│   └── requirements.txt     # Dependências
├── frontend/
│   ├── index.html           # Dashboard
│   ├── login.html
│   ├── register.html
│   ├── transfer.html
│   ├── exchange.html
│   ├── css/style.css
│   └── js/app.js
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/
    └── devsecops.yml        # Pipeline CI/CD completo
```

## Aviso de Segurança Educacional

Este projeto foi desenvolvido **intencionalmente** com vulnerabilidades para fins acadêmicos de análise de segurança. As vulnerabilidades incluem (e foram documentadas no relatório técnico):

- Credenciais hardcoded (detectadas pelo Gitleaks)
- Dependências com CVEs conhecidas (detectadas pelo pip-audit)
- SQL Injection em endpoint de busca (detectado pelo Semgrep/Bandit)
- Container executando como root (detectado pelo Checkov)
- Headers de segurança ausentes (detectados pelo OWASP ZAP)
