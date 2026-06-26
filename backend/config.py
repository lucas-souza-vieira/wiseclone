# ==============================================================================
# WiseClone - Configurações da Aplicação
# AVISO: Este arquivo contém credenciais hardcoded propositalmente para fins
# educacionais de segurança. NÃO usar em produção desta forma.
# ==============================================================================

import os

# ⚠️  VULNERABILIDADE: Secret hardcoded no código-fonte (detectado pelo Gitleaks)
# Correto seria: SECRET_KEY = os.environ.get("SECRET_KEY")
SECRET_KEY = "wiseclone-jwt-secret-key-2024-super-secret"

# ⚠️  VULNERABILIDADE: API Key hardcoded
EXCHANGE_API_KEY = "xch_live_sk-f8d3a2b1c9e7f4d6a8b2c0e1f5a9b3d7"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas

# Banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://wiseclone:wiseclone123@db:5432/wiseclone"
)

# Moedas suportadas
SUPPORTED_CURRENCIES = ["BRL", "USD", "EUR", "GBP", "JPY", "ARS", "CAD", "CHF"]

# Taxas de câmbio base (em relação ao BRL) - atualizadas diariamente no seed
BASE_EXCHANGE_RATES = {
    "BRL": 1.0,
    "USD": 0.18,
    "EUR": 0.17,
    "GBP": 0.14,
    "JPY": 27.5,
    "ARS": 185.0,
    "CAD": 0.25,
    "CHF": 0.16,
}

# Configurações do servidor
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# ⚠️  VULNERABILIDADE: CORS permissivo demais (sem restrição de origem)
CORS_ORIGINS = ["*"]
