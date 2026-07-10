# Imagem do backend FaciliChat (FastAPI + Uvicorn)
# Usa Python 3.12 (boa compatibilidade com as dependências fixadas) na variante slim.
# A MESMA imagem serve dev e produção (item S9): o que muda é o docker-compose —
# o de dev monta o código como volume e roda `--reload`; o de produção usa o código
# copiado na imagem, sem reload e com `--proxy-headers` (atrás do Caddy).

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

# Usuário não-root (item S9): se alguém explorar uma falha da aplicação, o processo
# comprometido não tem privilégio de root dentro do container. `--system` cria usuário
# sem senha e sem home elaborado; o código copiado acima pertence ao root e fica
# somente-leitura para o app — o processo não precisa (nem deve) escrever nele.
RUN useradd --system --no-create-home appuser
USER appuser

# Porta exposta pela API
EXPOSE 8000

# Sobe o servidor acessível de fora do container (0.0.0.0)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
