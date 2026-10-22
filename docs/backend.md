# Backend

API REST do VetTrace, em Python com Flask. Este guia explica a estrutura do código, as rotas,
a autenticação, como rodar fora do Docker e as decisões de arquitetura.

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Estrutura de pastas](#2-estrutura-de-pastas)
3. [Como uma requisição percorre o código](#3-como-uma-requisição-percorre-o-código)
4. [Rotas da API](#4-rotas-da-api)
5. [Autenticação](#5-autenticação)
6. [Convenções](#6-convenções)
7. [Rodar sem Docker](#7-rodar-sem-docker)
8. [Dependências](#8-dependências)
9. [Decisões de arquitetura](#9-decisões-de-arquitetura)

---

## 1. Visão geral

| Item | Escolha |
|---|---|
| Linguagem | Python 3.14 |
| Framework | Flask 3.0.3, com *application factory* e blueprints |
| Banco | PostgreSQL 18, acessado com psycopg2 e SQL escrito à mão |
| Autenticação | JWT (Flask-JWT-Extended) e hash de senha (Werkzeug) |
| Servidor | Gunicorn no Docker; servidor do próprio Flask (`run.py`) fora do Docker |

---

## 2. Estrutura de pastas

```
backend_vet/
├── run.py                  # roda a API fora do Docker: create_app() + app.run(debug=True)
├── database.py             # get_db_connection(): abre a conexão a partir da DATABASE_URL
├── test_connection.py      # teste rápido da conexão (conta os usuários)
├── requirements.txt        # dependências com versão fixada
├── Dockerfile              # imagem usada no Docker (Gunicorn)
├── .dockerignore
└── app/
    ├── __init__.py         # create_app(): CORS, JWT, blueprints e as rotas / e /teste
    ├── config.py           # lê DATABASE_URL e SECRET_KEY do ambiente
    ├── routes/             # camada HTTP — um blueprint por módulo
    │   ├── auth.py         #   cadastro e login
    │   ├── residuo.py      #   resíduos
    │   └── cadaver.py      #   cadáveres
    ├── services/           # camada de dados — as queries SQL
    │   ├── residuo_service.py
    │   └── cadaver_service.py
    └── models/             # não usado pelas rotas (ver ADR-002)
```

---

## 3. Como uma requisição percorre o código

Exemplo: registrar um resíduo.

```
POST /residuo ──► routes/residuo.py                ──► services/residuo_service.py ──► PostgreSQL
                  @jwt_required() valida o token        INSERT ... VALUES (%s, ...)
                  lê o JSON e o id do usuário           commit e fecha a conexão
              ◄── 201 {"id": ...} ◄──────────────────── devolve o id criado
```

1. A rota, em `routes/`, recebe a requisição, valida o token e extrai os dados do JSON.
2. Chama a função do service correspondente (`service_criar_residuo`).
3. O service abre uma conexão com `get_db_connection()`, executa o SQL parametrizado, faz o
   `commit` e fecha a conexão.
4. A rota devolve a resposta em JSON.

Um módulo novo segue o mesmo molde: um arquivo em `routes/`, um em `services/` e o registro
do blueprint em `app/__init__.py`.

---

## 4. Rotas da API

Base: `http://127.0.0.1:5000`. Todas as rotas recebem e devolvem JSON.

| Método | Rota | Token? | Faz |
|---|---|---|---|
| GET | `/` | — | status da API (usado pelo healthcheck do container) |
| GET | `/teste` | — | teste de comunicação |
| POST | `/api/auth/cadastro` | — | cria um usuário |
| POST | `/api/auth/login` | — | autentica e devolve o token |
| POST | `/residuo` | ✅ | registra um resíduo |
| GET | `/residuo` | — | lista os resíduos; `?mes=10&ano=2026` filtra por mês |
| GET | `/residuo/peso-total` | — | soma das quantidades; aceita `?mes=&ano=` |
| PUT | `/residuo/<id>` | ✅ | edita um resíduo |
| DELETE | `/residuo/<id>` | ✅ | exclui um resíduo (ver ADR-004) |
| POST | `/cadaver` | ✅ | registra um cadáver |
| GET | `/cadaver` | — | lista os cadáveres |
| PUT | `/cadaver/<id>` | ✅ | edita um cadáver |
| DELETE | `/cadaver/<id>` | ✅ | exclui um cadáver (ver ADR-004) |

**Corpo das requisições de escrita** (o `PUT` usa o mesmo formato do `POST`):

```json
POST /residuo
{
  "tipo_grupo": "A",
  "descricao": "Luvas contaminadas",
  "quantidade": 2.5,
  "unidade": "kg",
  "data_registro": "2026-10-20T10:00:00",
  "setor_gerador": "Cirurgia",
  "setor_destino": "-"
}
```

```json
POST /cadaver
{
  "especie": "Canina",
  "identificacao": "Rex",
  "idade_anos": 7,
  "peso_kg": 12.4,
  "nome_proprietario": "Fulano",
  "causa_obito": "Insuficiência renal",
  "destino_id": 1,
  "data_entrada": "2026-10-20T08:30:00",
  "data_saida": null,
  "status": "congelado",
  "observacoes": ""
}
```

Valores aceitos pelo banco: `tipo_grupo` — A, B, D ou E; `unidade` — kg, L ou unidade;
`status` do cadáver — congelado, aguardando_retirada ou retirado; `destino_id` — 1 (labocien),
2 (empresa terceirizada) ou 3 (proprietário).

**Erros:** `{"erro": "..."}` nas rotas de autenticação e quando o registro não existe (404);
`{"msg": "..."}` quando o token falta ou é inválido (401).

---

## 5. Autenticação

1. **Cadastro** (`POST /api/auth/cadastro`): obrigatórios `nome`, `email`, `cargo`, `senha` e
   `confirmar_senha`; opcionais `telefone` e `crmv` (formato `UF-12345`, validado pelo banco).
   A senha é guardada como hash. O **perfil** é deduzido do cargo: se contém "técnico" →
   `tecnico`; se contém "admin" → `admin`; senão → `solicitante`.
2. **Login** (`POST /api/auth/login`): recebe `email` e `senha` e devolve o `token` e os dados
   do `usuario`.
3. **Uso do token**: as rotas marcadas com ✅ exigem o cabeçalho
   `Authorization: Bearer <token>`.

O token vale **7 dias** e carrega o id do usuário (`sub`) e o `perfil`. Ver ADR-003.

---

## 6. Convenções

- **Português** nos nomes de variáveis e funções, nas mensagens da API e nos commits.
- **Rota não faz SQL:** a rota trata a requisição; a query fica no service.
- **SQL sempre parametrizado** com `%s` — nunca monte SQL com f-string (risco de SQL injection).
- **Rotas novas** com o prefixo `/api/` (ex.: `/api/empresas`). As rotas de resíduo e
  cadáver ainda não seguem esse padrão.
- **Rastreabilidade (RDC 222/2018):** todo registro novo grava o usuário responsável (vindo
  do token), a data e a hora.
- **Sem exclusão física** de registros de movimentação (RN05, RN28, RN35): use status ou
  exclusão lógica.
- **Mudou alguma coluna?** Atualize o `db/schema.sql` — ver
  [banco-de-dados.md](banco-de-dados.md#alterar-o-schema).

---

## 7. Rodar sem Docker

Útil para depurar com breakpoints. O banco continua no Docker.

**Pré-requisitos:** Python 3.14 (a mesma versão do container) e o Docker Desktop, para o banco.

```bash
docker compose stop frontend backend        # libera a porta 5000, se a stack estiver de pé
docker compose up -d --wait db              # sobe só o banco

cd backend_vet
python -m venv venv                         # só na primeira vez
venv\Scripts\activate                       # Windows (Linux/Mac: source venv/bin/activate)
python -m pip install -r requirements.txt   # na primeira vez e quando as dependências mudarem
python run.py                               # API em http://127.0.0.1:5000
```

Crie o `backend_vet/.env` apontando para o banco do Docker — a porta é o `POSTGRES_PORT` do `.env`
da raiz (5432 por padrão; 5433 se você tiver PostgreSQL instalado):

```env
SECRET_KEY=troque-em-producao
DATABASE_URL=postgresql://vettrace:vettrace@localhost:5432/vettrace
```

> O `run.py` conecta no banco ao iniciar (`db.create_all()`). Se o banco não estiver de pé,
> ele imprime as rotas e **depois** falha com `OperationalError` — confira `docker compose ps`.

Teste rápido da conexão: `python test_connection.py`, dentro de `backend_vet/`.

Para voltar à stack completa, pare o `run.py` e rode `docker compose up -d --wait`.

---

## 8. Dependências

- O `requirements.txt` lista todas as bibliotecas com **versão fixada**.
- `pywin32` e `pypiwin32` têm o marcador `; sys_platform == "win32"`: só são instalados no
  Windows. Sem o marcador, o build da imagem Docker (Linux) quebra.
- O Gunicorn não está no `requirements.txt`: ele não roda no Windows e só é usado no
  container, onde o `Dockerfile` o instala.
- Para adicionar uma biblioteca, siga [contribuindo.md](contribuindo.md#dependências-do-backend).

---

## 9. Decisões de arquitetura

Registros de decisão (ADRs) do backend. São registros retroativos: documentam decisões já
implementadas e as consequências que elas trazem hoje. Infraestrutura em
[docker.md](docker.md#9-decisões-de-arquitetura); frontend em
[frontend.md](frontend.md#9-decisões-de-arquitetura); banco em
[banco-de-dados.md](banco-de-dados.md#decisões-de-arquitetura).

### ADR-001 · Flask com blueprints e duas camadas: rotas e services

- **Status:** aceita
- **Contexto:** API pequena (autenticação, resíduos e cadáveres), feita por uma equipe
  acadêmica que precisava de algo simples de aprender e de dividir entre pessoas.
- **Decisão:** Flask com *application factory* (`create_app()` em `app/__init__.py`) e um
  blueprint por módulo. Cada módulo tem duas camadas: `routes/` (HTTP: lê a requisição e
  devolve JSON) e `services/` (dados: as queries).
- **Consequências:** ✅ todo módulo novo segue o mesmo molde; ✅ a factory permite subir a API
  pelo Gunicorn sem efeitos colaterais. ⚠️ `auth.py` ainda executa SQL dentro da própria rota
  e depende de um ajuste de `sys.path` para importar o `database.py`; ⚠️ os services ainda não
  tratam erros — um campo faltando no JSON vira erro 500.

### ADR-002 · SQL escrito à mão com psycopg2, sem ORM

- **Status:** aceita
- **Contexto:** o banco é modelado diretamente em SQL (`db/schema.sql`, com CHECKs, triggers e
  índices) e a equipe já domina SQL.
- **Decisão:** acessar o PostgreSQL com psycopg2 e SQL parametrizado (`%s`), recebendo as
  linhas como dicionários (`RealDictCursor`). A conexão vem de `database.get_db_connection()`,
  que lê a `DATABASE_URL`.
- **Consequências:** ✅ controle total das queries, sem camada oculta; ✅ os parâmetros `%s`
  protegem contra SQL injection. ⚠️ o Flask-SQLAlchemy continua instalado e inicializado (há
  um model `Usuario` incompleto e o `run.py` chama `db.create_all()`), mas nenhuma rota o usa
  — não crie models novos sem decidir com o time; ⚠️ cada função abre e fecha a própria
  conexão (não há pool).

### ADR-003 · Autenticação sem estado com JWT

- **Status:** aceita
- **Contexto:** o frontend é estático e separado da API; cada requisição precisa identificar o
  usuário sem uma sessão guardada no servidor.
- **Decisão:** o login devolve um JWT (Flask-JWT-Extended) com o id do usuário (`sub`) e o
  `perfil`, válido por 7 dias. As rotas de escrita usam `@jwt_required()`. As senhas são
  guardadas como hash (`werkzeug.security`).
- **Consequências:** ✅ a API não guarda sessão — reiniciar o container não desloga ninguém;
  ✅ a identidade do usuário chega assinada. ⚠️ não há logout nem revogação: o token vale até
  expirar; ⚠️ a chave de assinatura (`JWT_SECRET_KEY`) está fixa em `app/__init__.py` e
  deveria vir de variável de ambiente; ⚠️ as rotas GET ainda não exigem token; ⚠️ o `perfil`
  vai no token, mas nenhuma rota o verifica ainda.

### ADR-004 · O responsável pelo registro vem do token

- **Status:** aceita
- **Contexto:** a RDC 222/2018 exige rastreabilidade — quem registrou e quando. Se o frontend
  informasse o responsável, qualquer pessoa poderia registrar em nome de outra.
- **Decisão:** `POST /residuo` e `POST /cadaver` gravam o responsável a partir do token
  (`get_jwt_identity()`); o valor enviado pelo frontend é ignorado. A data e a hora do evento
  vêm do formulário; o `created_at` é preenchido pelo banco.
- **Consequências:** ✅ autoria confiável em todo registro novo. ⚠️ `DELETE /residuo/<id>` e
  `DELETE /cadaver/<id>` fazem exclusão física, o que contraria as regras RN05, RN28 e RN35 —
  o time precisa decidir entre status e exclusão lógica; ⚠️ as edições (`PUT`) não guardam
  histórico de quem alterou.
