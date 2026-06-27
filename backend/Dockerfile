# Imagem do backend FaciliChat (FastAPI + Uvicorn)
# Usa Python 3.12 (boa compatibilidade com as dependências fixadas) na variante slim.

FROM python:3.12-slim

# Não gera arquivos .pyc e mantém os logs sem buffer (aparecem na hora no `docker logs`)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Diretório de trabalho: a raiz do backend, onde fica o pacote `app/`
WORKDIR /app

# Instala as dependências primeiro — camada cacheável enquanto requirements.txt não muda
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do backend (em dev, o docker-compose monta o volume por cima)
COPY . .

# Porta exposta pela API
EXPOSE 8000

# Sobe o servidor acessível de fora do container (0.0.0.0)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
