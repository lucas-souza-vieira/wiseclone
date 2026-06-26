# ⚠️  DOCKERFILE COM VULNERABILIDADES INTENCIONAIS (para IaC Scanning)
# Detectadas por: Checkov, Trivy

# CKV_DOCKER_2: Imagem com tag 'latest' (não determinística, pode introduzir regressões)
FROM python:3.11

# CKV_DOCKER_3: Sem instrução HEALTHCHECK definida
# CKV_DOCKER_8: Container executa como root (sem instrução USER)

WORKDIR /app

# Copia tudo de uma vez (sem .dockerignore adequado)
COPY requirements.txt .

# CKV_DOCKER_9: Pip sem --no-cache-dir (aumenta tamanho da imagem)
RUN pip install -r requirements.txt

COPY . .

# CKV_DOCKER_7: Porta exposta sem documentação de propósito
EXPOSE 8000

# ⚠️  Executa como root — deveria ser: USER appuser
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
