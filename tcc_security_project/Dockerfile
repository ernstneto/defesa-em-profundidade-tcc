# Dockerfile

# Usar uma imagem oficial do Python
FROM python:3.11-slim

# Definir variáveis de ambiente (com a sintaxe correta)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Criar e definir o diretório de trabalho
WORKDIR /app

# Instalar dependências
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do projeto
COPY . /app/
