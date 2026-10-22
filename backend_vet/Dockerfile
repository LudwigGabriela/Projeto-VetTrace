# syntax=docker/dockerfile:1

# ============================================================
# Imagem do backend VetTrace — API Flask servida pelo Gunicorn
# Build: docker compose build backend   (guia: docs/docker.md)
# ============================================================

# Mesma versão do Python do venv local (3.14): o que roda no container
# se comporta igual ao que roda na máquina de quem desenvolve.
FROM python:3.14-slim

# PYTHONDONTWRITEBYTECODE: não grava .pyc dentro do container
# PYTHONUNBUFFERED: os print() aparecem na hora no "docker compose logs"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Usuário sem privilégios: se a API for comprometida, o invasor não é root.
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin appuser

# Dependências ANTES do código: esta camada fica em cache e só é refeita
# quando o requirements.txt muda. Mudar um .py não reinstala nada.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Gunicorn é o servidor de produção (o app.run(debug=True) do run.py é só
# para desenvolvimento). Fica fora do requirements.txt porque não roda no
# Windows e porque a aplicação em si não depende dele.
RUN pip install gunicorn==26.2.0

# Código da aplicação. O .dockerignore deixa de fora venv/, .env e caches.
# --chown: o "docker compose watch" precisa poder sobrescrever estes arquivos.
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 5000

# Forma exec (lista JSON): o Gunicorn vira o PID 1 e recebe o SIGTERM do
# "docker stop", encerrando as requisições em andamento com elegância.
# "app:create_app()" chama a factory direto, sem passar pelo db.create_all()
# do run.py — quem cria as tabelas é o db/schema.sql.
# --no-control-socket: o socket de gerenciamento do Gunicorn 26 é dispensável
# aqui (quem gerencia o processo é o Docker) e exigiria um diretório home.
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--worker-tmp-dir", "/dev/shm", \
     "--no-control-socket", \
     "--access-logfile", "-", \
     "app:create_app()"]
