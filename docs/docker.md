# Docker

Como rodar o VetTrace com Docker, como os containers se comunicam e como resolver os
problemas mais comuns.

## Sumário

1. [Subir o sistema](#1-subir-o-sistema)
2. [Arquitetura](#2-arquitetura)
3. [Como os containers se comunicam](#3-como-os-containers-se-comunicam)
4. [Comandos do dia a dia](#4-comandos-do-dia-a-dia)
5. [Desenvolvendo com Docker](#5-desenvolvendo-com-docker)
6. [Variáveis de ambiente](#6-variáveis-de-ambiente)
7. [Arquivos Docker do projeto](#7-arquivos-docker-do-projeto)
8. [Problemas comuns](#8-problemas-comuns)
9. [Decisões de arquitetura](#9-decisões-de-arquitetura)

---

## 1. Subir o sistema

Pré-requisito: [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e
**aberto** — ele não inicia sozinho com o Windows. Na raiz do projeto:

```bash
cp .env.example .env                  # só na primeira vez; ajuste as portas se precisar
docker compose up -d --build --wait
```

A primeira vez leva alguns minutos (baixa as imagens e instala as dependências).

| O quê | Endereço |
|---|---|
| Sistema | **http://localhost:8080** |
| API | http://127.0.0.1:5000 — teste em http://127.0.0.1:5000/teste |
| Banco (DBeaver/pgAdmin) | `localhost`, porta do `POSTGRES_PORT` — ver [banco-de-dados.md](banco-de-dados.md#conectar-por-dbeaver--pgadmin) |

Para conferir: `docker compose ps` deve listar `vettrace-db`, `vettrace-backend` e
`vettrace-frontend` como `healthy`.

> O login fica no `localStorage`, que é separado por endereço: quem usava o Live Server
> (`127.0.0.1:5500`) precisa entrar de novo em `localhost:8080`.

---

## 2. Arquitetura

```
 SEU COMPUTADOR (host)
 ┌────────────────────────────────────────────────────────────┐
 │  Navegador                                                 │
 │   │ http://localhost:8080         │ http://127.0.0.1:5000  │
 │   │ (páginas)                     │ (fetch da API)         │
 └───┼───────────────────────────────┼────────────────────────┘
     │ 127.0.0.1:8080 → 80           │ 127.0.0.1:5000 → 5000
 ┌───▼───────────────────────────────▼────────────────────────┐
 │  vettrace-frontend · Nginx 1.30                            │
 │    :80   serve HTML / CSS / JS                             │
 │    :5000 proxy reverso ──────────────┐                     │
 └──────────────────────────────────────┼─────────────────────┘
    rede-web                            │ http://backend:5000
 ┌──────────────────────────────────────▼─────────────────────┐
 │  vettrace-backend · Python 3.14 + Flask + Gunicorn         │
 │    :5000 (não publicada no host)                           │
 └──────────────────────────────────────┬─────────────────────┘
    rede-dados                          │ postgresql://...@db:5432
 ┌──────────────────────────────────────▼─────────────────────┐
 │  vettrace-db · PostgreSQL 18                               │
 │    :5432 → publicada em 127.0.0.1:${POSTGRES_PORT}         │
 │    volume vettrace-data (os dados ficam aqui)              │
 └────────────────────────────────────────────────────────────┘
```

| Serviço | Container | Imagem | Portas no host | Redes |
|---|---|---|---|---|
| `frontend` | `vettrace-frontend` | `frontend_vet/Dockerfile` (Nginx 1.30) | `127.0.0.1:8080` (páginas) e `127.0.0.1:5000` (API) | rede-web |
| `backend` | `vettrace-backend` | `backend_vet/Dockerfile` (Python 3.14 + Gunicorn) | nenhuma | rede-web e rede-dados |
| `db` | `vettrace-db` | `postgres:18` (oficial) | `127.0.0.1:${POSTGRES_PORT}` | rede-dados |

Os dados do banco ficam no volume `vettrace-data` e sobrevivem a `stop`, `down` e rebuild.

---

## 3. Como os containers se comunicam

**O caminho de um login**

1. O navegador abre `http://localhost:8080` e o Nginx devolve `login.html` e os scripts.
2. O `login.js`, rodando no navegador, chama `http://127.0.0.1:5000/api/auth/login`.
3. A porta 5000 também é do Nginx, que repassa a chamada para `http://backend:5000`.
4. O Flask consulta o banco em `db:5432`, confere a senha e devolve o token.

**O nome do serviço é o endereço.** Containers na mesma rede se encontram pelo nome do
serviço (`db`, `backend`), resolvido pelo DNS interno do Docker. Por isso a `DATABASE_URL` do
backend aponta para `db`, e não para `localhost`.

**Duas redes.** A `rede-web` liga frontend e backend; a `rede-dados` liga backend e banco. O
backend é a única ponte: o frontend não alcança o banco.

**Portas só em `127.0.0.1`.** Páginas, API e banco aceitam conexões apenas desta máquina —
o banco usa o usuário e a senha padrão que estão no repositório.

**Ordem de subida.** Cada serviço tem um *healthcheck*, e o `depends_on` monta a fila:
banco saudável → backend sobe → backend saudável → frontend sobe.

Para ver na prática:

```bash
docker compose exec frontend wget -qO- http://backend:5000/teste   # frontend → backend: responde
docker compose exec frontend nc -zv -w 3 db 5432                    # frontend → banco: "bad address 'db'"
docker compose exec backend python test_connection.py               # backend → banco: conta os usuários
```

---

## 4. Comandos do dia a dia

Sempre na raiz do projeto.

| Quero... | Comando |
|---|---|
| Subir tudo | `docker compose up -d --build --wait` |
| Subir só o banco | `docker compose up -d --wait db` |
| Ver o estado | `docker compose ps` |
| Ver os logs ao vivo | `docker compose logs -f` ou `docker compose logs -f backend` |
| Parar sem remover | `docker compose stop` |
| Religar | `docker compose start` |
| Reiniciar um serviço | `docker compose restart backend` |
| Aplicar mudança de código | `docker compose up -d --build` |
| Desligar e remover os containers (os dados ficam) | `docker compose down` |
| Abrir um terminal no backend | `docker compose exec backend sh` |
| Abrir o psql | `docker compose exec db psql -U vettrace -d vettrace` |
| ⚠️ Apagar o banco e recomeçar | `docker compose down -v` — faça [backup](banco-de-dados.md#backup-e-restauração) antes |

> O `restart` reaproveita a configuração antiga. Mudou o `docker-compose.yml` ou o `.env`?
> Use `docker compose up -d`.

---

## 5. Desenvolvendo com Docker

O código é **copiado para dentro da imagem** no build. Depois de editar, rode
`docker compose up -d --build` — ou deixe o modo watch cuidar disso:

```bash
docker compose watch
```

| Você salva... | O que acontece |
|---|---|
| HTML, CSS ou JS em `frontend_vet/` | o arquivo é copiado para o container na hora — basta dar F5 |
| `.py` em `backend_vet/app/` ou `backend_vet/database.py` | o arquivo é copiado e o backend reinicia (~2 s) |
| `backend_vet/requirements.txt` ou `nginx.conf` | a imagem é reconstruída |

Para depurar o Flask com breakpoints, rode-o fora do Docker:
[backend.md — Rodar sem Docker](backend.md#7-rodar-sem-docker).

---

## 6. Variáveis de ambiente

O Compose lê o `.env` da raiz (copiado do `.env.example`).

| Variável | Padrão | Para quê |
|---|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `vettrace` | usuário, senha e nome do banco |
| `POSTGRES_PORT` | `5432` | porta do banco no seu computador — use `5433` se já tiver PostgreSQL instalado |
| `FRONTEND_PORT` | `8080` | porta das páginas no seu computador |
| `SECRET_KEY` | — | chave do Flask |

- No container, a `DATABASE_URL` é montada pelo próprio `docker-compose.yml`, apontando para
  `db:5432`. A `DATABASE_URL` do `.env` só vale para rodar o Flask fora do Docker.
- O `backend_vet/.env` é lido apenas pelo Flask rodando fora do Docker.
- Nenhum `.env` entra nas imagens nem vai para o Git.
- A porta da API (5000) é fixa: o JavaScript chama `http://127.0.0.1:5000` direto.

Variável nova: adicione ao `.env.example` e a esta tabela.

---

## 7. Arquivos Docker do projeto

| Arquivo | Para quê |
|---|---|
| `docker-compose.yml` | os 3 serviços, as 2 redes, o volume, os healthchecks e o modo watch |
| `.env.example` | modelo do `.env` |
| `backend_vet/Dockerfile` | imagem da API: Python 3.14, dependências, usuário sem privilégios e Gunicorn |
| `backend_vet/.dockerignore` | mantém `venv/`, `.env` e caches fora da imagem |
| `frontend_vet/Dockerfile` | imagem do Nginx com `paginas/`, `js/`, `estilos/` e `assets/` |
| `frontend_vet/nginx.conf` | páginas na porta 80, proxy da API na 5000 e cabeçalhos de segurança |
| `db/schema.sql` | estrutura do banco, aplicada na primeira subida — ver [banco-de-dados.md](banco-de-dados.md) |

---

## 8. Problemas comuns

**`failed to connect to the docker API ... dockerDesktopLinuxEngine`**
O Docker Desktop está fechado. Abra-o e espere `docker info` responder.

**`port is already allocated`**
Outro processo usa a porta. 5000: o Flask local (`python run.py`) está rodando? 5432: há um
PostgreSQL instalado na máquina — use `POSTGRES_PORT=5433`. 8080: mude o `FRONTEND_PORT`.

**O navegador mostra "Erro ao conectar com o servidor."**
1. `docker compose ps`: os três estão `healthy`?
2. http://127.0.0.1:5000/teste responde? Se não, veja `docker compose logs frontend backend`.
3. `502 Bad Gateway`: o Nginx está de pé, mas o backend não — `docker compose logs backend`.

**Mudei o código e nada aconteceu**
`docker compose up -d --build` (ou use o `watch`). No navegador, Ctrl+F5.

**Container `unhealthy`**
`docker compose logs <serviço>` e `docker inspect <container> --format "{{json .State.Health}}"`,
que mostra a saída do teste que falhou.

**`invalid file request` durante o build**
O arquivo tem um *reparse point* do OneDrive — acontece quando o projeto está ou já esteve
numa pasta sincronizada (como `OneDrive\Documentos`). Mantenha o projeto fora do OneDrive e
regrave os arquivos afetados (PowerShell, dentro de `backend_vet` ou `frontend_vet`):

```powershell
Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\\venv\\' -and $_.Attributes -band [IO.FileAttributes]::ReparsePoint } | ForEach-Object {
    $tmp = "$($_.FullName).tmp"
    [IO.File]::WriteAllBytes($tmp, [IO.File]::ReadAllBytes($_.FullName))
    Remove-Item -LiteralPath $_.FullName -Force
    Move-Item -LiteralPath $tmp -Destination $_.FullName
}
```

**O build falha no `pip install` por causa do `pywin32`**
Os marcadores `; sys_platform == "win32"` do `requirements.txt` sumiram — o `pip freeze` os
apaga. Recoloque-os: ver [contribuindo.md](contribuindo.md#dependências-do-backend).

**O banco "sumiu" depois de clonar ou renomear a pasta**
O volume leva o nome da pasta (`<pasta>_vettrace-data`): pasta nova, banco novo e vazio. O
antigo continua listado em `docker volume ls`.

---

## 9. Decisões de arquitetura

Registros de decisão (ADRs) da infraestrutura. São registros retroativos: documentam
decisões já implementadas. As demais ADRs estão em
[backend.md](backend.md#9-decisões-de-arquitetura) (001 a 004),
[frontend.md](frontend.md#9-decisões-de-arquitetura) (005 a 008) e
[banco-de-dados.md](banco-de-dados.md#decisões-de-arquitetura) (009).

### ADR-010 · Ambiente completo em Docker Compose

- **Status:** aceita
- **Contexto:** cada máquina tinha versões diferentes de Python e de PostgreSQL — em algumas,
  um PostgreSQL instalado já ocupava a porta 5432 — e rodar o projeto exigia vários passos
  manuais.
- **Decisão:** descrever o sistema inteiro no `docker-compose.yml`: `db` (imagem oficial
  `postgres:18`), `backend` e `frontend` (imagens próprias), com versões fixadas, healthchecks
  e `depends_on` encadeado.
- **Consequências:** ✅ um comando sobe o sistema igual em qualquer máquina; ✅ o backend só
  sobe depois que o banco terminou de aplicar o schema. ⚠️ mudanças de código exigem rebuild
  (ou `docker compose watch`); ⚠️ é preciso manter o Docker Desktop aberto.

### ADR-011 · Nginx serve as páginas e faz o proxy da API na porta 5000

- **Status:** aceita
- **Contexto:** o JavaScript do frontend chama `http://127.0.0.1:5000` direto, em 7 arquivos.
  Publicar o backend no host exporia o Flask diretamente.
- **Decisão:** o container `frontend` (Nginx) serve as páginas na porta 80 (publicada em 8080)
  e também escuta na 5000, repassando as chamadas para `backend:5000`. O backend não publica
  porta. O Nginx resolve o nome `backend` a cada requisição (`resolver 127.0.0.11`).
- **Consequências:** ✅ nenhum arquivo do frontend precisou mudar; ✅ uma única porta de
  entrada para a API — o lugar certo para HTTPS, limites e logs no futuro; ✅ o proxy continua
  funcionando quando o backend é recriado. ⚠️ páginas (8080) e API (5000) estão em portas
  diferentes, então o navegador faz requisições *cross-origin* e o CORS do Flask continua
  necessário; ⚠️ a porta 5000 do host fica com o Nginx — para rodar o Flask local é preciso
  parar `frontend` e `backend`.

### ADR-012 · Duas redes e portas publicadas só em 127.0.0.1

- **Status:** aceita
- **Contexto:** o banco usa usuário e senha padrão publicados no repositório, e o time
  trabalha em redes compartilhadas, como a da faculdade.
- **Decisão:** `rede-web` (frontend ↔ backend) e `rede-dados` (backend ↔ db). Todas as portas
  publicadas usam o prefixo `127.0.0.1:`.
- **Consequências:** ✅ ninguém na mesma rede Wi-Fi alcança o banco ou a API; ✅ um Nginx
  comprometido não chega ao banco. ⚠️ não dá para abrir o sistema de outro dispositivo (um
  celular, por exemplo) sem mudar as portas — e o JavaScript ainda aponta para `127.0.0.1`.

### ADR-013 · Gunicorn como servidor da API no container

- **Status:** aceita
- **Contexto:** `app.run(debug=True)` é o servidor de desenvolvimento do Flask: não é feito
  para uso real e, com o debug ligado, expõe um console que executa código Python.
- **Decisão:** a imagem do backend roda o Gunicorn (2 workers) chamando a factory
  `app:create_app()` — sem o `db.create_all()` do `run.py` — como um usuário sem privilégios
  (`appuser`).
- **Consequências:** ✅ servidor de produção, com log de cada requisição; ✅ o processo não
  roda como root. ⚠️ o Gunicorn não funciona no Windows, por isso é instalado só no
  `Dockerfile` — fora do Docker continua o `python run.py`.
