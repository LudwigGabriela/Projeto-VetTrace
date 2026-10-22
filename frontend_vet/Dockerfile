# syntax=docker/dockerfile:1

# ============================================================
# Imagem do frontend VetTrace — Nginx servindo os arquivos estáticos
# e fazendo proxy da API para o backend.
# Build: docker compose build frontend   (guia: docs/docker.md)
# ============================================================

# 1.30 é a linha "stable" do Nginx; alpine deixa a imagem com ~50 MB.
FROM nginx:1.30-alpine

# Tira a página "Welcome to nginx!" que vem na imagem
RUN rm -rf /usr/share/nginx/html/*

# Substitui a configuração padrão pela nossa (páginas na 80, API na 5000)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia só o que o navegador precisa: Dockerfile e nginx.conf não ficam públicos
COPY paginas/ /usr/share/nginx/html/paginas/
COPY js/      /usr/share/nginx/html/js/
COPY estilos/ /usr/share/nginx/html/estilos/
COPY assets/  /usr/share/nginx/html/assets/

EXPOSE 80 5000

# CMD herdado da imagem oficial: nginx -g "daemon off;"
